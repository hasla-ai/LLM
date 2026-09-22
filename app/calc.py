"""Forge H2 — 수소 예비검토 계산 (단위 명시·근거 추적).

`app/main.py` 의 `/api/mvp/feasibility` 가 쓰던 계산을 대체한다.
기존 구현의 결함 네 가지를 고친다.

1. LHV 33.33 이 코드에 직접 박혀 있었다. 기준값은 공식 라이브러리의
   `reference_values`에서 읽으며, 그 값은 출처·근거 상태와 함께 반환된다.
   `execution_policy.requires_unit_check` 를 선언해 놓고 코드가 라이브러리를 참조하지 않았다.

2. `power_mw` 가 총발전단인지 순출력인지 정의가 없었고 소내부하가 모델에 없었다.
   순출력을 입력하면 실제 필요 수소량이 소내부하율만큼 과소산정된다.
   여기서는 총발전단을 기준으로 삼고 순출력을 파생값으로 낸다.

3. `storage_kg = flow * 24 * days` 에 사용가능 잔압 비율이 없었다.
   압축가스는 최소사용압력 아래를 뽑을 수 없으므로 설치 저장량은 이 값을
   usable_fraction 으로 나눈 것이어야 한다. 빠지면 저장설비가 과소산정된다.

4. `storage_density_kg_m3` 기본값 30 은 대략 450~500 bar 에 해당한다.
   200 bar 15 °C 에서 수소 밀도는 약 15 kg/m³ 다. 밀도를 상수로 두지 않고
   저장압력·온도·압축계수에서 계산한다. Z 는 근거와 함께 주어져야 한다.

모든 함수는 값과 함께 사용한 공식 ID·가정·근거등급을 돌려준다.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_LIB_PATH = os.path.join(os.path.dirname(_HERE), "knowledge", "formula-library-h2.json")

# 기체상수 R = 8.314462 J/(mol·K), M_H2 = 0.002016 kg/mol
RS_H2 = 4124.2          # J/(kg·K)
O2_PER_H2 = 7.9360      # kg O2 / kg H2
H2O_PER_H2 = 8.9360     # kg H2O / kg H2
HOURS_PER_YEAR = 8760


def load_formula_library(path: str = _LIB_PATH) -> dict:
    """공식 라이브러리를 읽는다. 없으면 빈 라이브러리를 돌려주되 조용히 넘어가지 않는다."""
    if not os.path.exists(path):
        return {"formulas": [], "_missing": path}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def formula_ref(library: dict, formula_id: str) -> dict | None:
    for f in library.get("formulas", []):
        if f["formula_id"] == formula_id:
            return {
                "formula_id": f["formula_id"],
                "equation": f.get("equation_ascii"),
                "verification_status": f.get("verification_status"),
                "source_knowledge_id": f.get("source_knowledge_id"),
            }
    return None


def reference_value(library: dict, name: str) -> dict:
    """Return a source-traceable reference value; never silently use a code constant."""
    value = library.get("reference_values", {}).get(name)
    if not value or not isinstance(value.get("value"), (int, float)):
        raise ValueError(f"공식 라이브러리에 기준값이 없습니다: {name}")
    return value


@dataclass
class Traced:
    """값 하나와 그 값이 어디서 왔는지."""
    value: float
    unit: str
    formula_id: str | None = None
    assumptions: list[str] = field(default_factory=list)
    reliability_tier: str = "T4"     # 유도 계산. 입력이 더 나쁘면 호출자가 내려야 한다.


def hydrogen_demand(
    gross_power_mw: float,
    electrical_efficiency_lhv: float,
    parasitic_fraction: float = 0.0,
    capacity_factor: float = 1.0,
    lhv_kwh_per_kg: float | None = None,
) -> dict[str, Traced]:
    """총발전단 출력에서 수소 소비량을 낸다.

    electrical_efficiency_lhv 는 총발전단(Gross AC) / 수소 LHV 입력 기준이다.
    순출력 기준 효율을 넣으면 수소량이 과소산정된다.
    """
    if not 0.05 < electrical_efficiency_lhv < 0.95:
        raise ValueError("효율은 0.05~0.95 사이의 소수여야 합니다 (퍼센트가 아님)")
    if not 0.0 <= parasitic_fraction < 0.5:
        raise ValueError("소내부하율은 0 이상 0.5 미만이어야 합니다")

    library = load_formula_library()
    lhv_reference = reference_value(library, "H2_LHV_KWH_PER_KG")
    lhv = float(lhv_reference["value"] if lhv_kwh_per_kg is None else lhv_kwh_per_kg)
    if lhv <= 0:
        raise ValueError("수소 LHV는 양수여야 합니다")
    fuel_kw = gross_power_mw * 1000.0 / electrical_efficiency_lhv
    flow_kg_h = fuel_kw / lhv
    net_mw = gross_power_mw * (1.0 - parasitic_fraction)
    annual_t = flow_kg_h * HOURS_PER_YEAR * capacity_factor / 1000.0

    return {
        "fuel_input": Traced(fuel_kw, "kW", "FML-H2-001",
                             [f"LHV {lhv:.3f} kWh/kg — 공식 라이브러리 reference_values",
                              f"근거상태 {lhv_reference['verification_status']}",
                              "정상상태 정격운전"]),
        "hydrogen_flow": Traced(flow_kg_h, "kg/h", "FML-H2-001",
                                ["효율은 총발전단 기준"]),
        "net_power": Traced(net_mw, "MW", "FML-H2-002",
                            ["소내부하율 %.3f 적용" % parasitic_fraction]),
        "annual_hydrogen": Traced(annual_t, "t/yr", "FML-H2-003",
                                  ["이용률 %.3f" % capacity_factor]),
        "specific_consumption": Traced(flow_kg_h / gross_power_mw, "kg/MWh", "FML-H2-004", []),
    }


def hydrogen_density(pressure_bar_abs: float, temperature_k: float,
                     compressibility_z: float) -> Traced:
    """압축수소 저장밀도. Z 를 상수로 두지 않는다 — 근거와 함께 주어져야 한다.

    참고: 200 bar / 288 K / Z=1.10 → 약 15.3 kg/m³.
          기존 코드의 기본값 30 kg/m³ 는 대략 450~500 bar 에 해당한다.
    """
    if compressibility_z <= 0:
        raise ValueError("압축계수 Z 는 양수여야 합니다")
    rho = pressure_bar_abs * 1e5 / (RS_H2 * temperature_k * compressibility_z)
    return Traced(rho, "kg/m3", "FML-H2-006",
                  [f"Z={compressibility_z} — 실측표 출처 필요",
                   f"P={pressure_bar_abs} bar(a), T={temperature_k} K"],
                  reliability_tier="T5")


def storage_sizing(
    flow_kg_h: float,
    autonomy_days: float,
    capacity_factor: float = 1.0,
    usable_fraction: float = 0.80,
    density_kg_m3: float | None = None,
) -> dict[str, Traced]:
    """자립일수와 사용가능 잔압을 반영한 저장 산정.

    usable_fraction 을 1.0 으로 두면 잔압분을 무시해 설비가 과소산정된다.
    압축가스 저장은 통상 0.7~0.85 이며 최소사용압력에서 결정된다.
    """
    if not 0.1 < usable_fraction <= 1.0:
        raise ValueError("사용가능 비율은 0.1 초과 1.0 이하여야 합니다")

    deliverable_kg = flow_kg_h * 24.0 * autonomy_days * capacity_factor
    installed_kg = deliverable_kg / usable_fraction
    out = {
        "deliverable": Traced(deliverable_kg, "kg", "FML-H2-005",
                              [f"자립일수 {autonomy_days} day, 이용률 {capacity_factor}"]),
        "installed_inventory": Traced(installed_kg, "kg", "FML-H2-005",
                                      [f"사용가능 비율 {usable_fraction} 적용"],
                                      reliability_tier="T5"),
    }
    if density_kg_m3:
        out["storage_volume"] = Traced(installed_kg / density_kg_m3, "m3", "FML-H2-006",
                                       ["설치 저장량 기준 (인출가능량 아님)"],
                                       reliability_tier="T5")
    return out


def mass_balance(flow_kg_h: float, air_ratio_lambda: float = 2.0) -> dict[str, Traced]:
    """H2 + ½O2 → H2O 화학량론. 정의값이므로 등급이 내려가지 않는다."""
    o2 = flow_kg_h * O2_PER_H2
    return {
        "oxygen_consumed": Traced(o2, "kg/h", "FML-H2-010", [], "T1"),
        "water_produced": Traced(flow_kg_h * H2O_PER_H2, "kg/h", "FML-H2-011", [], "T1"),
        "air_supplied": Traced(o2 / 0.2314 * air_ratio_lambda, "kg/h", "FML-H2-012",
                               [f"공기비 {air_ratio_lambda}"], "T1"),
    }


def choked_release(discharge_coefficient: float, hole_diameter_mm: float,
                   pressure_bar_abs: float, temperature_k: float,
                   gamma: float = 1.41) -> Traced:
    """초크드 오리피스 수소 누출률.

    화염길이는 여기서 산출하지 않는다. 검증된 상관식의 출처와 적용 유효범위,
    그리고 자격자 판정이 있어야 한다 (미션 M065 계열).
    """
    area = math.pi * (hole_diameter_mm / 1000.0) ** 2 / 4.0
    mdot = (discharge_coefficient * area * pressure_bar_abs * 1e5
            * math.sqrt(gamma / (RS_H2 * temperature_k))
            * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0))))
    return Traced(mdot, "kg/s", "FML-H2-014",
                  ["등엔트로피 초크류·이상기체 가정",
                   "200 bar 이상에서는 실기체 보정 필요",
                   "누출공 직경은 시나리오 합의값",
                   "화염길이·안전거리는 이 계산이 정하지 않는다"],
                  reliability_tier="T5")


def feasibility(
    gross_power_mw: float,
    electrical_efficiency_lhv: float = 0.475,
    parasitic_fraction: float = 0.078,
    capacity_factor: float = 0.90,
    autonomy_days: float = 2.0,
    usable_fraction: float = 0.80,
    storage_pressure_bar_abs: float = 200.0,
    storage_temperature_k: float = 288.15,
    compressibility_z: float = 1.10,
) -> dict:
    """예비 검토 한 벌. 모든 결과에 공식 ID 와 가정이 붙는다."""
    lib = load_formula_library()
    lhv_reference = reference_value(lib, "H2_LHV_KWH_PER_KG")
    demand = hydrogen_demand(gross_power_mw, electrical_efficiency_lhv,
                             parasitic_fraction, capacity_factor,
                             float(lhv_reference["value"]))
    rho = hydrogen_density(storage_pressure_bar_abs, storage_temperature_k, compressibility_z)
    storage = storage_sizing(demand["hydrogen_flow"].value, autonomy_days,
                             capacity_factor, usable_fraction, rho.value)
    balance = mass_balance(demand["hydrogen_flow"].value)

    results = {**demand, "storage_density": rho, **storage, **balance}
    used = sorted({t.formula_id for t in results.values() if t.formula_id})

    return {
        "status": "preliminary",
        "disclaimer": "예비 검토용 결과이며 설계·허가·시공 결정을 대체하지 않습니다.",
        "basis": {
            "power_reference": "gross (총발전단)",
            "heating_value": lhv_reference,
            "formula_library_version": lib.get("library_version"),
            "formula_library_missing": lib.get("_missing"),
        },
        "results": {k: asdict(v) for k, v in results.items()},
        "formulas_used": [formula_ref(lib, fid) for fid in used],
        "lowest_reliability_tier": max(
            (t.reliability_tier for t in results.values()), default="T4"),
        "note": "최저 근거등급이 T5 이면 가정 기반입니다. 기준선으로 승격할 수 없습니다.",
    }


if __name__ == "__main__":
    import pprint
    pprint.pp(feasibility(20.0))

