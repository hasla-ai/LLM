import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from .providers import ChatMessage, get_provider
from .database import get_task_states, load_graph, load_profile, record_event, save_graph, save_profile, set_task_status

ROOT = Path(__file__).parent
PROJECT_FILE = ROOT.parent / "project.json"
WORKSPACE = ROOT.parent
BLOCKED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
BLOCKED_FILES = {".env"}
app = FastAPI(title="Claude-style AI workspace")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

class MessageIn(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=20000)

class ChatIn(BaseModel):
    messages: list[MessageIn] = Field(min_length=1, max_length=100)

class ProjectUpdate(BaseModel):
    instructions: str = Field(min_length=1, max_length=5000)

class FeasibilityIn(BaseModel):
    location: str = Field(min_length=2, max_length=200)
    power_mw: float = Field(gt=0, le=5000)
    annual_hours: int = Field(gt=0, le=8760)
    hydrogen_source: str = Field(min_length=2, max_length=100)
    plant_type: str = Field(default="fuel-cell", max_length=100)
    electrical_efficiency: float = Field(default=0.50, gt=0.05, lt=0.90)
    storage_days: float = Field(default=1.0, gt=0, le=30)
    storage_density_kg_m3: float = Field(default=30.0, gt=0)
    power_block_area_m2_per_mw: float = Field(default=900.0, gt=0)
    fixed_area_m2: float = Field(default=3000.0, ge=0)
    site_utilization: float = Field(default=0.35, gt=0.05, le=0.90)

class GraphIn(BaseModel):
    blocks: list[dict] = Field(min_length=1, max_length=30)

class GeoGraphIn(BaseModel):
    nodes: list[dict] = Field(min_length=1, max_length=100)
    edges: list[dict] = Field(default_factory=list, max_length=200)

class GeoGraphSaveIn(GeoGraphIn):
    nodes: list[dict] = Field(default_factory=list, max_length=100)
    project_id: str = Field(default="default", min_length=1, max_length=100)

class TaskStatusIn(BaseModel):
    project_id: str = Field(default="default", min_length=1, max_length=100)
    task_id: str = Field(min_length=1, max_length=100)
    status: str = Field(pattern="^(needs-data|review|approval|done)$")

class GeoProjectProfileIn(FeasibilityIn):
    project_id: str = Field(default="default", min_length=1, max_length=100)

class GeoProjectIn(BaseModel):
    project_id: str = Field(default="default", min_length=1, max_length=100)

@app.get("/")
async def index():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/mvp")
async def mvp_page():
    return FileResponse(ROOT / "static" / "mvp.html")

@app.get("/builder")
async def builder_page():
    return FileResponse(ROOT / "static" / "builder.html")

@app.get("/map")
async def map_page():
    return FileResponse(ROOT / "static" / "geo.html")

@app.get("/tasks")
async def tasks_page():
    return FileResponse(ROOT / "static" / "tasks.html")

@app.get("/api/health")
async def health():
    from .config import settings
    return {"status": "ok", "provider": settings.provider, "model": settings.model}

@app.get("/api/project")
async def project():
    import json
    return json.loads(PROJECT_FILE.read_text(encoding="utf-8"))

@app.put("/api/project")
async def update_project(payload: ProjectUpdate):
    import json
    data = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    data["instructions"] = payload.instructions.strip()
    PROJECT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data

def safe_workspace_path(relative: str) -> Path:
    candidate = (WORKSPACE / relative).resolve()
    if WORKSPACE not in candidate.parents and candidate != WORKSPACE:
        raise ValueError("workspace 밖의 경로는 접근할 수 없습니다.")
    if any(part in BLOCKED_DIRS for part in candidate.relative_to(WORKSPACE).parts):
        raise ValueError("보호된 디렉터리입니다.")
    if candidate.name in BLOCKED_FILES:
        raise ValueError("보호된 파일입니다.")
    return candidate

@app.get("/api/files")
async def files():
    result = []
    for path in WORKSPACE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(WORKSPACE)
        if any(part in BLOCKED_DIRS for part in rel.parts) or path.name in BLOCKED_FILES:
            continue
        result.append({"path": str(rel).replace("\\", "/"), "size": path.stat().st_size})
    return {"files": sorted(result, key=lambda item: item["path"].lower())[:500]}

@app.get("/api/discover")
async def discover():
    """Infer project context without asking the user to fill in an onboarding form."""
    names = {p.name.lower() for p in WORKSPACE.iterdir()}
    stack = []
    if any(name.endswith(".py") for name in names) or "requirements.txt" in names or "pyproject.toml" in names:
        stack.append("Python")
    if "requirements.txt" in names or "pyproject.toml" in names:
        stack.append("Python packages")
    if "package.json" in names:
        stack.append("JavaScript/Node.js")
    if "dockerfile" in names or "docker-compose.yml" in names:
        stack.append("Docker")
    commands = []
    if "requirements.txt" in names:
        commands.append("pip install -r requirements.txt")
    if "package.json" in names:
        commands.append("npm install")
    if (WORKSPACE / "tests").exists() or (WORKSPACE / "pytest.ini").exists():
        commands.append("pytest")
    return {"mode": "zero-onboarding", "stack": sorted(set(stack)), "commands": commands, "entrypoints": ["app/main.py"] if (WORKSPACE / "app/main.py").exists() else []}

@app.post("/api/mvp/feasibility")
async def feasibility(payload: FeasibilityIn):
    energy_mwh = payload.power_mw * payload.annual_hours
    h2_kwh_per_kg = 33.33
    h2_kg_per_hour = payload.power_mw * 1000 / (payload.electrical_efficiency * h2_kwh_per_kg)
    h2_kg_per_year = h2_kg_per_hour * payload.annual_hours
    storage_kg = h2_kg_per_hour * 24 * payload.storage_days
    storage_volume_m3 = storage_kg / payload.storage_density_kg_m3
    method = payload.hydrogen_source.lower()
    if "배관" in method or "pipeline" in method:
        supply_area_m2 = 500.0
        supply_note = "배관 인입·계량·감압 설비의 예비 면적 계수"
    elif "액화" in method or "liquid" in method:
        supply_area_m2 = 1200.0
        supply_note = "액화수소 저장·기화 설비의 예비 면적 계수"
    elif "전해" in method or "electro" in method:
        supply_area_m2 = 1800.0
        supply_note = "전해조·정제·압축 설비의 예비 면적 계수"
    else:
        supply_area_m2 = 900.0
        supply_note = "튜브트레일러·하역·임시 저장 설비의 예비 면적 계수"
    process_area_m2 = (
        payload.power_mw * payload.power_block_area_m2_per_mw
        + supply_area_m2
        + storage_volume_m3 * 3.0
        + payload.fixed_area_m2
    )
    gross_area_m2 = process_area_m2 / payload.site_utilization
    return {
        "status": "preliminary",
        "disclaimer": "예비 검토용 결과이며 설계·허가·시공 결정을 대체하지 않습니다.",
        "project": payload.model_dump(),
        "derived": {
            "annual_generation_mwh": round(energy_mwh, 2),
            "capacity_factor": round(payload.annual_hours / 8760, 4),
            "hydrogen_kg_per_hour": round(h2_kg_per_hour, 2),
            "hydrogen_kg_per_year": round(h2_kg_per_year, 2),
            "storage_inventory_kg": round(storage_kg, 2),
            "storage_volume_m3": round(storage_volume_m3, 2),
            "screening_process_area_m2": round(process_area_m2, 2),
            "screening_gross_area_m2": round(gross_area_m2, 2),
            "screening_gross_area_ha": round(gross_area_m2 / 10000, 3),
        },
        "area_model": {
            "formula": "A_gross = (P·a_power + A_supply + 3·V_storage + A_fixed) / U_site",
            "hydrogen_formula": "m_H2 = P_electric / (efficiency · 33.33 kWh/kg)",
            "supply_area_note": supply_note,
            "assumptions": {
                "hydrogen_lhv_kwh_per_kg": h2_kwh_per_kg,
                "storage_days": payload.storage_days,
                "storage_density_kg_m3": payload.storage_density_kg_m3,
                "power_block_area_m2_per_mw": payload.power_block_area_m2_per_mw,
                "site_utilization": payload.site_utilization,
            },
            "warning": "스크리닝 계수이며 설계·허가·안전거리 산정값이 아닙니다. 공급사 자료와 관할 기준으로 대체해야 합니다.",
        },
        "work_packages": [
            {"id": "site", "title": "부지·좌표 검토", "owners": ["토목", "건축", "환경"], "status": "needs-data"},
            {"id": "grid", "title": "계통연계 검토", "owners": ["발송배전", "전기안전"], "status": "needs-data"},
            {"id": "hydrogen", "title": "수소 공급·저장·감압 검토", "owners": ["수소·가스", "기계·배관"], "status": "needs-data"},
            {"id": "safety", "title": "누출·화재·폭발 위험성 검토", "owners": ["수소안전", "소방", "계측제어"], "status": "needs-data"},
            {"id": "permit", "title": "법규·인허가 매트릭스", "owners": ["인허가", "품질"], "status": "needs-data"},
        ],
        "required_documents": [
            "전력수요 및 운영조건 정의서",
            "부지·토지·재해·주변시설 자료",
            "수소 공급 압력·순도·유량·저장조건",
            "계통연계 지점과 접속조건",
            "적용 법령·기술기준 확인자료",
        ],
        "generated_documents": [
            "예비 사업성 검토서",
            "설계기준서 초안",
            "전문분야별 작업분해표",
            "예비 위험성 검토 계획",
            "인허가 제출자료 목록",
        ],
    }

@app.post("/api/mvp/report")
async def report(payload: FeasibilityIn):
    result = await feasibility(payload)
    project = result["project"]
    derived = result["derived"]
    lines = [
        "# Forge H2 예비 설계·사업성 검토서",
        "",
        "> 상태: 예비 검토 초안. 자격 있는 전문가의 검토와 관할기관 확인이 필요합니다.",
        "",
        "## 1. 프로젝트 개요",
        "",
        f"- 설치 지역: {project['location']}",
        f"- 발전 방식: {project['plant_type']}",
        f"- 목표 발전 용량: {project['power_mw']} MW",
        f"- 연간 운전시간: {project['annual_hours']} 시간",
        f"- 수소 공급 방식: {project['hydrogen_source']}",
        f"- 단순 연간 발전량: {derived['annual_generation_mwh']} MWh",
        f"- 계산상 설비 이용률: {derived['capacity_factor'] * 100:.1f}%",
        f"- 예비 수소 사용량: {derived['hydrogen_kg_per_hour']} kg/h, 연간 {derived['hydrogen_kg_per_year']} kg",
        f"- 예비 저장재고: {derived['storage_inventory_kg']} kg ({project['storage_days']}일)",
        f"- 예비 총부지 면적: {derived['screening_gross_area_m2']} m² ({derived['screening_gross_area_ha']} ha)",
        "",
        "## 2. 설계 전제와 미확인 사항",
        "",
        "- 수소 압력·순도·유량·저장조건은 공급자 자료로 확인해야 합니다.",
        "- 부지 경계·토지용도·지질·재해·주변 민감시설 자료가 필요합니다.",
        "- 계통연계 지점·접속용량·보호협조 조건을 확인해야 합니다.",
        "- 적용 법령과 기술기준은 관할기관 및 전문 검토자가 확정해야 합니다.",
        "",
        "## 3. 1차 면적 모델",
        "",
        f"- 수소 사용량 공식: `{result['area_model']['hydrogen_formula']}`",
        f"- 총부지 공식: `{result['area_model']['formula']}`",
        f"- 공정·지원시설 면적: {derived['screening_process_area_m2']} m²",
        f"- 총부지 스크리닝 면적: {derived['screening_gross_area_m2']} m²",
        "- 면적 계수는 공급사 자료, 안전거리, 방폭·소방 기준으로 갱신해야 합니다.",
        "",
        "## 4. 전문분야별 작업분해",
        "",
    ]
    for item in result["work_packages"]:
        lines.append(f"- [ ] **{item['title']}** — 담당: {', '.join(item['owners'])} — 상태: {item['status']}")
    lines += [
        "",
        "## 5. 예비 위험성 검토 계획",
        "",
        "1. 수소 누출원과 격리구역 식별",
        "2. 환기·감지·차단·비상정지 개념 검토",
        "3. 화재·폭발·압력방출 시나리오 작성",
        "4. 방폭·재료적합성·배관접합 요구사항 확인",
        "5. HAZID/HAZOP 및 필요 시 정량 위험성 평가 수행",
        "",
        "## 6. 생성 대상 문서",
        "",
    ]
    lines.extend(f"- [ ] {doc}" for doc in result["generated_documents"])
    lines += [
        "",
        "## 7. 승인 게이트",
        "",
        "- [ ] 사업·수요 담당자 확인",
        "- [ ] 수소·가스 안전 담당자 검토",
        "- [ ] 기계·배관 담당자 검토",
        "- [ ] 전기·계통연계 담당자 검토",
        "- [ ] 소방·환경·인허가 담당자 검토",
        "- [ ] 관할기관 사전협의",
        "",
        "## 8. 주의사항",
        "",
        "이 문서는 입력값을 구조화한 예비 초안이며, 설계도서·허가신청서·시공승인서를 대체하지 않습니다.",
    ]
    return {"filename": "forge_h2_preliminary_design.md", "content": "\n".join(lines)}

@app.post("/api/builder/analyze")
async def analyze_builder(payload: GraphIn):
    values = {}
    for block in payload.blocks:
        kind = str(block.get("type", ""))
        values.update(block.get("values", {}))
        values["_" + kind] = True
    required = ["location", "power_mw", "annual_hours", "hydrogen_source"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        return {"ok": False, "missing": missing, "message": "필수 블록의 값을 입력하세요."}
    request = FeasibilityIn(
        location=str(values["location"]),
        power_mw=float(values["power_mw"]),
        annual_hours=int(values["annual_hours"]),
        hydrogen_source=str(values["hydrogen_source"]),
        plant_type=str(values.get("plant_type", "fuel-cell")),
        electrical_efficiency=float(values.get("electrical_efficiency", 0.50)),
        storage_days=float(values.get("storage_days", 1.0)),
        storage_density_kg_m3=float(values.get("storage_density_kg_m3", 30.0)),
        power_block_area_m2_per_mw=float(values.get("power_block_area_m2_per_mw", 900.0)),
        site_utilization=float(values.get("site_utilization", 0.35)),
    )
    result = await feasibility(request)
    return {"ok": True, "normalized": request.model_dump(), "result": result}

@app.post("/api/geo/analyze")
async def analyze_geo(payload: GeoGraphIn):
    valid = []
    for node in payload.nodes:
        try:
            lat = float(node["lat"])
            lon = float(node["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            valid.append({"id": node.get("id"), "type": node.get("type", "unknown"), "lat": lat, "lon": lon, "properties": node.get("properties", {})})
    if not valid:
        return {"ok": False, "message": "유효한 위도·경도 노드가 없습니다."}
    workplan_preview = []
    domain_by_type = {
        "site": "부지·토목·환경",
        "hydrogen-source": "수소·가스 안전",
        "storage": "기계·배관·수소안전",
        "power-block": "발전·기계·전기",
        "grid": "발송배전·전기안전",
    }
    for index, node in enumerate(valid, start=1):
        workplan_preview.append({
            "id": f"GEO-{index:03d}",
            "node_id": node["id"],
            "domain": domain_by_type.get(node["type"], "종합설계"),
            "status": "needs-data",
        })
    return {
        "ok": True,
        "coordinate_graph": {"crs": "WGS84", "nodes": valid, "edges": payload.edges},
        "extent": {
            "south": min(n["lat"] for n in valid),
            "north": max(n["lat"] for n in valid),
            "west": min(n["lon"] for n in valid),
            "east": max(n["lon"] for n in valid),
        },
        "next_checks": ["부지 경계", "토지이용·재해", "주변 민감시설", "수소 공급경로", "계통연계 지점"],
        "workplan_preview": workplan_preview,
    }

@app.post("/api/geo/save")
async def save_geo(payload: GeoGraphSaveIn):
    added = save_graph(payload.project_id, payload.nodes, payload.edges)
    return {"ok": True, "project_id": payload.project_id, **added, "mode": "append-only"}

@app.get("/api/geo/graph")
async def get_geo(project_id: str = "default"):
    return load_graph(project_id)

@app.get("/api/geo/profile")
async def get_geo_profile(project_id: str = "default"):
    return {"project_id": project_id, "profile": load_profile(project_id)}

@app.put("/api/geo/profile")
async def put_geo_profile(payload: GeoProjectProfileIn):
    profile = payload.model_dump(exclude={"project_id"})
    save_profile(payload.project_id, profile)
    return {"ok": True, "project_id": payload.project_id, "profile": profile}

def inferred_geo_profile(graph: dict):
    capacities = []
    for node in graph["nodes"]:
        if node.get("type") != "power-block":
            continue
        try:
            capacities.append(float((node.get("properties") or {}).get("capacity_mw", 0)))
        except (TypeError, ValueError):
            continue
    return {
        "location": "WGS84 공간 그래프",
        "power_mw": round(sum(capacities) or 10.0, 3),
        "annual_hours": 4000,
        "hydrogen_source": "배관 공급",
        "plant_type": "fuel-cell",
        "electrical_efficiency": 0.50,
        "storage_days": 1.0,
        "storage_density_kg_m3": 30.0,
        "power_block_area_m2_per_mw": 900.0,
        "fixed_area_m2": 3000.0,
        "site_utilization": 0.35,
    }

def haversine_m(first: dict, second: dict):
    lat1, lon1 = radians(float(first["lat"])), radians(float(first["lon"]))
    lat2, lon2 = radians(float(second["lat"])), radians(float(second["lon"]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371000 * 2 * asin(sqrt(value))

def spatial_screen(graph: dict):
    nodes = graph["nodes"]
    by_type = {}
    for node in nodes:
        by_type.setdefault(node.get("type", "unknown"), []).append(node)
    warnings = []
    if not by_type.get("site"):
        warnings.append("발전소 부지(site) 좌표가 없습니다.")
    for node_type, label in [("hydrogen-source", "수소 공급원"), ("storage", "저장·감압 설비"), ("power-block", "발전 블록"), ("grid", "계통연계 지점")]:
        if not by_type.get(node_type):
            warnings.append(f"{label} 좌표가 없습니다.")

    connections = []
    for source_type, target_type, label in [
        ("hydrogen-source", "storage", "수소 공급원 → 저장·감압"),
        ("storage", "power-block", "저장·감압 → 발전 블록"),
        ("power-block", "grid", "발전 블록 → 계통연계"),
    ]:
        pairs = [(haversine_m(a, b), a, b) for a in by_type.get(source_type, []) for b in by_type.get(target_type, [])]
        if pairs:
            distance, source, target = min(pairs, key=lambda item: item[0])
            item = {"label": label, "from": source["id"], "to": target["id"], "distance_m": round(distance, 1)}
            connections.append(item)
            if distance < 50:
                warnings.append(f"{label}가 {distance:.1f}m로 근접합니다. 이 값은 법정 안전거리가 아닌 추가 검토 신호입니다.")

    edge_routes = []
    route_total = 0.0
    for edge in graph["edges"]:
        source = next((node for node in nodes if node.get("id") == edge.get("from")), None)
        target = next((node for node in nodes if node.get("id") == edge.get("to")), None)
        if source and target:
            distance = haversine_m(source, target)
            route_total += distance
            edge_routes.append({"from": source["id"], "to": target["id"], "distance_m": round(distance, 1)})
        else:
            warnings.append(f"연결 {edge.get('from')} → {edge.get('to')}의 대상 좌표를 찾을 수 없습니다.")

    valid = [node for node in nodes if isinstance(node.get("lat"), (int, float)) and isinstance(node.get("lon"), (int, float))]
    extent = None
    if valid:
        extent = {
            "south": min(node["lat"] for node in valid),
            "north": max(node["lat"] for node in valid),
            "west": min(node["lon"] for node in valid),
            "east": max(node["lon"] for node in valid),
        }
    power_block_mw = sum(float((node.get("properties") or {}).get("capacity_mw", 0) or 0) for node in by_type.get("power-block", []))
    return {
        "node_count": len(nodes),
        "edge_count": len(graph["edges"]),
        "extent": extent,
        "capacity_summary": {"power_block_mw": round(power_block_mw, 3)},
        "connection_distances": connections,
        "edge_routes": edge_routes,
        "total_edge_route_m": round(route_total, 1),
        "proximity_review_threshold_m": 50,
        "warnings": warnings,
        "limitations": ["점 좌표 간 직선거리만 계산합니다.", "지형·필지경계·법정 안전거리·배관 상세경로를 대체하지 않습니다."],
    }

async def build_geo_assessment(project_id: str):
    graph = load_graph(project_id)
    saved_profile = load_profile(project_id)
    profile = saved_profile or inferred_geo_profile(graph)
    feasibility_result = await feasibility(FeasibilityIn(**profile))
    spatial = spatial_screen(graph)
    return {
        "project_id": project_id,
        "status": "preliminary",
        "profile_source": "saved" if saved_profile else "inferred_from_map",
        "profile": profile,
        "feasibility": feasibility_result,
        "spatial": spatial,
        "warnings": spatial["warnings"],
    }

@app.post("/api/geo/assessment")
async def geo_assessment(payload: GeoProjectIn):
    assessment = await build_geo_assessment(payload.project_id)
    record_event(payload.project_id, "assessment.generated", {
        "profile_source": assessment["profile_source"],
        "derived": assessment["feasibility"]["derived"],
        "spatial": assessment["spatial"],
    })
    return assessment

@app.get("/api/geo/snapshot")
async def geo_snapshot(project_id: str = "default"):
    graph = load_graph(project_id)
    return {
        "project_id": project_id,
        "schema": "forge-h2.project.v1",
        "graph": graph,
        "profile": load_profile(project_id),
        "task_states": get_task_states(project_id),
        "history": "append-only database; historical events are not returned by this endpoint",
    }

@app.get("/api/geo/snapshot/download")
async def download_geo_snapshot(project_id: str = "default"):
    snapshot = await geo_snapshot(project_id)
    filename = f"forge-h2-{project_id}-snapshot.json"
    return Response(
        content=json.dumps(snapshot, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.post("/api/geo/workplan")
async def geo_workplan(payload: GeoGraphSaveIn):
    graph = {"nodes": payload.nodes, "edges": payload.edges}
    templates = {
        "site": ("부지·토목·환경", "부지 경계, 토지이용, 재해, 주변 민감시설 자료", "부지 적합성 검토서"),
        "hydrogen-source": ("수소·가스 안전", "공급 압력, 순도, 유량, 공급경로 자료", "수소 공급조건서"),
        "storage": ("기계·배관·수소안전", "저장량, 압력, 재료, 방출·차단 조건", "저장·감압 설비 검토서"),
        "power-block": ("발전·기계·전기", "발전방식, 출력, 효율, 냉각·배기 조건", "발전 블록 설계기준서"),
        "grid": ("발송배전·전기안전", "접속점, 전압, 단락용량, 보호협조 조건", "계통연계 검토서"),
    }
    task_states = get_task_states(payload.project_id)
    tasks = []
    for index, node in enumerate(graph["nodes"], start=1):
        domain, inputs, output = templates.get(node.get("type"), ("종합설계", "요소의 위치·속성·연결관계", "전문 검토 카드"))
        tasks.append({
            "id": f"GEO-{index:03d}",
            "node_id": node.get("id"),
            "question": f"{node.get('type')} 요소를 해당 좌표에 배치할 수 있는가?",
            "domain": domain,
            "required_inputs": inputs,
            "deliverable": output,
            "acceptance": ["좌표와 단위 확인", "적용 기준 연결", "미확인 가정 표시", "전문가 검토자 지정"],
            "status": task_states.get(f"GEO-{index:03d}", "needs-data"),
        })
    workplan = {"project_id": payload.project_id, "graph_node_count": len(graph["nodes"]), "tasks": tasks}
    record_event(payload.project_id, "workplan.generated", workplan)
    return workplan

@app.get("/api/geo/report")
async def geo_report(project_id: str = "default"):
    graph = load_graph(project_id)
    plan = await geo_workplan(GeoGraphSaveIn(project_id=project_id, nodes=graph["nodes"], edges=graph["edges"]))
    assessment = await build_geo_assessment(project_id)
    nodes = graph["nodes"]
    valid = [node for node in nodes if isinstance(node.get("lat"), (int, float)) and isinstance(node.get("lon"), (int, float))]
    status_labels = {"needs-data": "자료 필요", "review": "검토 진행", "approval": "승인 대기", "done": "완료"}
    lines = [
        "# Forge H2 공간 기반 예비 설계문서",
        "",
        "> 상태: 예비 검토용 자동 생성본. 인허가 제출·시공 지시·안전거리 확정에 사용할 수 없으며, 관련 분야 자격자와 관할 기관의 검토가 필요합니다.",
        "",
        "## 1. 프로젝트 개요",
        "",
        f"- 프로젝트 ID: `{project_id}`",
        f"- 좌표계: WGS84 (위도·경도)",
        f"- 배치 요소: {len(nodes)}개",
        f"- 공정 연결: {len(graph['edges'])}개",
    ]
    if valid:
        lines.extend([
            f"- 공간 범위: 남쪽 {min(n['lat'] for n in valid):.6f}, 북쪽 {max(n['lat'] for n in valid):.6f}, 서쪽 {min(n['lon'] for n in valid):.6f}, 동쪽 {max(n['lon'] for n in valid):.6f}",
        ])
    else:
        lines.append("- 공간 범위: 아직 유효한 좌표가 없습니다.")
    lines.extend(["", "## 2. 공간 배치 목록", ""])
    if nodes:
        for node in nodes:
            properties = node.get("properties") or {}
            name = properties.get("name") or node.get("type", "unknown")
            capacity = properties.get("capacity_mw")
            capacity_text = f", 용량 {capacity} MW" if capacity is not None else ""
            lines.append(f"- **{name}** (`{node.get('type', 'unknown')}`): {float(node.get('lat', 0)):.6f}, {float(node.get('lon', 0)):.6f}{capacity_text}")
    else:
        lines.append("- 배치된 요소가 없습니다.")
    lines.extend(["", "## 3. 공정 연결", ""])
    if graph["edges"]:
        for edge in graph["edges"]:
            lines.append(f"- `{edge.get('from')}` → `{edge.get('to')}` ({edge.get('type', 'process-flow')})")
    else:
        lines.append("- 정의된 공정 연결이 없습니다.")
    lines.extend(["", "## 4. 전문 작업계획", ""])
    if plan["tasks"]:
        for task in plan["tasks"]:
            checked = "x" if task["status"] == "done" else " "
            lines.append(f"- [{checked}] **{task['id']} · {task['domain']}** — {task['question']} ({status_labels.get(task['status'], task['status'])})")
            lines.append(f"  - 필요자료: {task['required_inputs']}")
            lines.append(f"  - 산출물: {task['deliverable']}")
    else:
        lines.append("- 공간 요소를 배치하면 전문 작업이 생성됩니다.")
    lines.extend([
        "",
        "## 5. 다음 검토 게이트",
        "",
        "1. 토지이용·재해·환경·주변 민감시설 자료 확인",
        "2. 수소 공급 압력·순도·유량·운송/저장 조건 확인",
        "3. 방출·차단·환기·화재 대응과 위험구역 검토",
        "4. 발전 블록·계통연계 조건 및 보호협조 검토",
        "5. HAZID/HAZOP, 정량 위험성평가, 인허가 요구사항 확인",
        "",
        "## 6. 제한사항",
        "",
        "이 문서는 공간 그래프와 현재 작업상태를 구조화해 만든 예비 산출물입니다. 실제 설계도서, 법정 안전거리, 구조·전기·소방 계산서 및 인허가 서류를 대체하지 않습니다.",
    ])
    derived = assessment["feasibility"]["derived"]
    spatial = assessment["spatial"]
    lines.extend([
        "",
        "## 7. 공간·용량 통합 예비검토",
        "",
        f"- 프로필 출처: {assessment['profile_source']}",
        f"- 발전량: {derived['annual_generation_mwh']} MWh/년",
        f"- 시간당 수소 사용량: {derived['hydrogen_kg_per_hour']} kg/h",
        f"- 예비 총부지면적: {derived['screening_gross_area_m2']} m² ({derived['screening_gross_area_ha']} ha)",
        f"- 지도상 공정 연결 총 직선거리: {spatial['total_edge_route_m']} m",
        "",
        "### 자동 검토 신호",
        "",
    ])
    lines.extend(f"- {warning}" for warning in spatial["warnings"] or ["현재 자동 검토 경고가 없습니다."])
    return {
        "project_id": project_id,
        "filename": f"forge-h2-{project_id}-preliminary-design.md",
        "status": "preliminary",
        "content": "\n".join(lines),
    }

@app.get("/api/geo/report/download")
async def download_geo_report(project_id: str = "default"):
    report = await geo_report(project_id)
    filename = "forge-h2-" + "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in project_id)[:80] + "-preliminary-design.md"
    return Response(
        content=report["content"],
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.post("/api/geo/task-status")
async def update_task_status(payload: TaskStatusIn):
    set_task_status(payload.project_id, payload.task_id, payload.status)
    return {"ok": True, "project_id": payload.project_id, "task_id": payload.task_id, "status": payload.status}

@app.get("/api/files/content")
async def file_content(path: str):
    try:
        target = safe_workspace_path(path)
    except ValueError as exc:
        return {"error": str(exc)}
    if not target.is_file():
        return {"error": "파일을 찾을 수 없습니다."}
    if target.stat().st_size > 500_000:
        return {"error": "파일이 너무 큽니다."}
    try:
        return {"path": path, "content": target.read_text(encoding="utf-8")}
    except UnicodeDecodeError:
        return {"error": "텍스트 파일만 열 수 있습니다."}

@app.post("/api/artifact")
async def artifact(payload: dict):
    """Extract the first fenced code block as a reusable Artifact."""
    import re
    content = str(payload.get("content", ""))
    match = re.search(r"```([\w+-]*)\n([\s\S]*?)```", content)
    if not match:
        return {"found": False, "message": "코드 Artifact를 찾지 못했습니다."}
    language = match.group(1) or "text"
    return {"found": True, "language": language, "content": match.group(2).rstrip()}

@app.post("/api/verify")
async def verify():
    """Run the project's fixed, read-only Python syntax check."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "app"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "passed": result.returncode == 0,
        "command": "python -m compileall -q app",
        "output": (result.stdout + result.stderr).strip(),
    }

@app.post("/api/chat")
async def chat(payload: ChatIn):
    messages = [ChatMessage(**m.model_dump()) for m in payload.messages]
    try:
        content = await get_provider().reply(messages)
        return {"role": "assistant", "content": content}
    except RuntimeError as exc:
        return {"role": "assistant", "content": f"⚠️ {exc}"}
