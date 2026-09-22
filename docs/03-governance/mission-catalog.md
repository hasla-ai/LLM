# Forge H2 미션 카탈로그

문서 ID: FHZ-MISSION-001  
버전: 0.1  
목적: 수소발전소 사업을 실행 가능한 함수형 미션으로 분해하고, AI 오케스트레이터가 순서·병렬성·차단조건을 판단하도록 한다.

## 1. 공통 미션 계약

```json
{
  "mission_id": "M-001",
  "name": "capture_intent",
  "version": "0.1.0",
  "owner_role": "Product Owner",
  "input_schema": "ProjectIntent.RawBrief.v1",
  "output_schema": "ProjectIntent.v1",
  "preconditions": [],
  "risk_class": "B",
  "review_role": "PMO",
  "gate": "G0"
}
```

실행 함수:

```text
run_mission(mission_definition, input, context) -> MissionResult
```

반환 상태:

- `PASS`: 출력과 근거가 검증됨
- `BLOCKED`: 필수 입력·선행조건·외부회신 부족
- `HUMAN_REVIEW`: 전문 검토 또는 승인 필요
- `FAIL`: 입력 오류·계산 오류·정책 위반
- `SUPERSEDED`: 후속 기준선으로 대체됨

## 2. 핵심 데이터 계약

### 2.1 ProjectIntent

```json
{
  "project_id": "FHZ-001",
  "jurisdiction": {"country": "KR", "region": "", "authority": ""},
  "site": {"address": "", "lat": null, "lon": null, "parcel_ids": []},
  "power": {"target_mw": null, "plant_type": "", "annual_hours": null},
  "hydrogen": {"source_type": "", "pressure_bar": null, "purity": null, "supply_kg_h": null},
  "offtake": {"buyer": "", "contract_type": "", "target_date": null},
  "commercial": {"budget_krw": null, "funding_status": "", "currency": "KRW"},
  "raw_brief": "",
  "assumptions": [],
  "completeness": 0.0
}
```

### 2.2 Evidence

```json
{
  "evidence_id": "EVD-0001",
  "type": "law|standard|drawing|vendor|survey|test|decision|measurement",
  "title": "",
  "source_uri": "",
  "source_owner": "",
  "issued_at": null,
  "effective_from": null,
  "effective_to": null,
  "content_hash": "",
  "reliability_tier": "T0-T5",
  "verification_status": "unverified|verified|superseded|rejected",
  "reviewer": null,
  "used_by_missions": [],
  "notes": ""
}
```

### 2.3 Gate

```json
{
  "gate_id": "G1",
  "entry_conditions": [],
  "required_missions": [],
  "required_evidence": [],
  "decision_options": ["PASS", "CONDITIONAL", "HOLD", "STOP"],
  "approvers": [],
  "decision": null,
  "decision_record_id": null
}
```

## 3. 미션 실행 규칙

1. 입력은 항상 원문과 정규화값을 함께 보존한다.
2. 단위·범위·좌표·버전을 검증한 뒤 실행한다.
3. 선행 미션이 `PASS` 또는 승인된 `CONDITIONAL`이 아니면 실행하지 않는다.
4. AI 추정값은 `assumption`으로만 저장하고 기준선 값으로 승격하지 않는다.
5. 고위험 미션은 계산 결과와 별도로 전문 검토 미션을 생성한다.
6. 외부기관 회신이 필요한 미션은 `BLOCKED`로 유지한다.
7. 출력은 다음 미션의 입력 스키마를 만족해야 한다.
8. 미션 재실행 시 기존 결과를 삭제하지 않고 새 실행번호를 만든다.
9. 기준선이 바뀌면 영향받는 미션을 자동으로 `REVIEW_REQUIRED`로 표시한다.
10. 미션 완료는 출력물·근거·검토자·다음 단계가 모두 존재할 때만 인정한다.

### 3.1 병렬 실행과 재기준선

- `parallel_group`이 같은 미션은 선행조건이 통과했고 공통 입력을 서로 변경하지 않을 때 병렬 실행할 수 있다.
- 병렬 미션도 각각 독립 실행번호·입력 해시·Evidence·검토자를 가진다. 일부 트랙이 실패하면 Gate 통합은 멈추며 성공한 트랙만으로 추정 통과하지 않는다.
- 인허가 준비·조달 준비·현장조사처럼 병렬 가능한 작업은 `orchestration_rules.parallel_tracks`에 등록한다.
- 변경·예외·외부 조건 변경은 `REVIEW_REQUIRED` 전파 규칙을 작동시킨다. 영향을 받는 결과를 무효화하거나 재검토한 뒤 새 기준선으로 승격한다.
- `HOLD`, `REOPEN`, `CHANGE_IMPACT_REQUIRED`는 실패가 아니라 통제된 프로젝트 상태이며, 변경 로그·재실행·인간 승인이 없으면 자동으로 다음 Gate로 이동하지 않는다.

## 4. 100개 미션 인덱스

### Phase 0 — 사업 입력과 실행 통제

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-001 | `capture_intent` | RawBrief | ProjectIntent | Product Owner | G0 |
| M-002 | `normalize_units` | ProjectIntent | NormalizedIntent | Data Lead | G0 |
| M-003 | `classify_plant_archetype` | Intent | PlantArchetype | Chief Engineer | G0 |
| M-004 | `resolve_jurisdiction` | Site·국가·지역 | Jurisdiction | Regulatory | G0 |
| M-005 | `map_authorities` | Jurisdiction·Archetype | AuthorityMatrix | PMO | G0 |
| M-006 | `check_completeness` | Intent | MissingFieldList | PMO | G0 |
| M-007 | `register_assumptions` | MissingFields·Defaults | AssumptionRegister | PMO | G0 |
| M-008 | `triage_hazards` | Archetype·H2·Capacity | InitialHazardClass | HSE | G0 |
| M-009 | `set_kill_criteria` | Budget·Schedule·Target | KillCriteria | Sponsor | G0 |
| M-010 | `create_project_graph` | Intent·Assumptions | ProjectState | PMO | G0 |

### Phase 1 — 수요·사업성·금융

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-011 | `forecast_load` | OfftakerData | LoadProfile | Commercial | G1 |
| M-012 | `define_offtake` | Load·Contracts | OfftakeSpec | Commercial | G1 |
| M-013 | `derive_energy_target` | Load·Hours | EnergyTarget | Power Lead | G1 |
| M-014 | `build_dispatch_cases` | Energy·H2Availability | DispatchCases | Power Lead | G1 |
| M-015 | `define_h2_economics` | H2Source·Volume | H2CommercialSpec | Commercial | G1 |
| M-016 | `build_h2_price_scenarios` | Quotes·Transport | PriceScenarios | Finance | G1 |
| M-017 | `build_revenue_case` | Offtake·Dispatch | RevenueCases | Finance | G1 |
| M-018 | `estimate_capex_opex` | Archetype·Capacity·Site | CostRange | Finance | G1 |
| M-019 | `build_finance_case` | Cost·Revenue·Funding | FinanceCase | Finance | G1 |
| M-020 | `business_go_no_go` | FinanceCase·KillCriteria | DevelopmentGate | Sponsor | G1 |

### Phase 2 — 입지·토지·GIS

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-021 | `geocode_site` | Address·Coordinates | CoordinateRef | GIS/Data | G1 |
| M-022 | `load_cadastral_parcels` | Coordinate | ParcelSet | GIS/Data | G1 |
| M-023 | `check_land_use` | Parcel·Zoning | LandConstraintSet | Civil/Regulatory | G1 |
| M-024 | `verify_site_control` | Parcel·RightsDocs | SiteControl | Commercial | G1 |
| M-025 | `analyze_topography` | Elevation·Parcel | CivilBasis | Civil | G1 |
| M-026 | `screen_geology` | Geology·Site | GeotechnicalScreen | Civil | G1 |
| M-027 | `screen_natural_hazards` | HazardLayers | HazardMap | HSE/Civil | G1 |
| M-028 | `screen_protected_areas` | Ecology·CulturalLayers | EnvironmentalScreen | Environment | G1 |
| M-029 | `analyze_access_logistics` | Roads·Equipment | LogisticsScreen | EPC | G1 |
| M-030 | `rank_site_candidates` | Candidates·Constraints·Cost | RankedSites | PMO | G1 |

### Phase 3 — 수소 생산·공급·저장

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-031 | `select_supply_path` | Intent·Site·Market | H2SupplyArchetype | Hydrogen Lead | G2 |
| M-032 | `verify_hydrogen_origin` | SupplierDocs | H2Origin | Regulatory | G2 |
| M-033 | `specify_hydrogen_quality` | Vendor·Supply | H2QualitySpec | Hydrogen Lead | G2 |
| M-034 | `match_supply_demand` | H2Profile·Dispatch | SupplyDemandFit | Hydrogen Lead | G2 |
| M-035 | `size_storage` | H2Profile·Autonomy | StorageSpec | Mechanical | G2 |
| M-036 | `size_compression_regulation` | Pressures·Flow | ConditioningSpec | Mechanical/Piping | G2 |
| M-037 | `plan_transport_route` | Source·Site·Roads | DeliveryPlan | Logistics | G2 |
| M-038 | `design_supply_redundancy` | Demand·Suppliers | ReliabilityCase | Hydrogen Lead | G2 |
| M-039 | `audit_supplier` | Certificates·References | SupplierScore | Procurement | G2 |
| M-040 | `h2_ready_gate` | Supply·Storage·Supplier | H2ReadyDecision | Chief Engineer | G2 |

### Phase 4 — 발전기·열·전력계통

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-041 | `select_power_technology` | Capacity·H2·Site | PowerBlockOption | Chief Engineer | G2 |
| M-042 | `simulate_power_performance` | VendorCurves·Dispatch | PerformanceModel | Power Lead | G2 |
| M-043 | `calculate_auxiliary_load` | Power·Cooling·Compression | AuxLoad | Mechanical/Electrical | G2 |
| M-044 | `calculate_heat_water_balance` | Power·Climate·Cooling | UtilityBalance | Mechanical/Environment | G2 |
| M-045 | `screen_grid_points` | Site·GridData·MW | GridPointCandidates | Electrical/Grid | G2 |
| M-046 | `request_grid_preconsultation` | GridPoint·PowerSpec | PreconsultationResult | Electrical/Grid | G2 |
| M-047 | `run_interconnection_study` | GridPoint·SLD·Dispatch | GridStudyPackage | Electrical/Grid | G2 |
| M-048 | `check_power_quality` | Generator·GridRules | GridCompliance | Electrical/Grid | G2 |
| M-049 | `select_market_route` | Size·Offtake·Grid | MarketRoute | Commercial | G2 |
| M-050 | `power_grid_ready_gate` | Power·Grid·Market | PowerReadyDecision | Chief Engineer | G2 |

### Phase 5 — 개념설계

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-051 | `freeze_design_basis` | Project·H2·Power | DesignBasis | Chief Engineer | G3 |
| M-052 | `generate_process_flow` | DesignBasis | PFD | Process Lead | G3 |
| M-053 | `calculate_mass_energy_balance` | PFD·H2·Performance | BalanceModel | Process Lead | G3 |
| M-054 | `generate_plot_plan` | Site·Equipment·Zones | PlotPlan | Civil/Mechanical | G3 |
| M-055 | `classify_hazardous_areas` | Sources·Inventory·Ventilation | HazardousArea | HSE/Process | G3 |
| M-056 | `build_equipment_register` | PFD·DesignBasis | EquipmentRegister | Engineering | G3 |
| M-057 | `route_piping` | PFD·PlotPlan·Pressure | PipingConcept | Piping Lead | G3 |
| M-058 | `generate_single_line_diagram` | Power·Grid | SLD | Electrical Lead | G3 |
| M-059 | `define_icss_safety_concept` | PFD·Hazards | ICSSConcept | ICSS Lead | G3 |
| M-060 | `review_concept_package` | PFD·Balance·Plot·SLD | ConceptReview | Chief Engineer | G3 |

### Phase 6 — 법규·안전·환경·인허가

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-061 | `build_legal_requirement_matrix` | Jurisdiction·Archetype | LegalMatrix | Regulatory | G3 |
| M-062 | `map_kgs_codes` | H2Facilities·Equipment | KGSMatrix | Regulatory/HSE | G3 |
| M-063 | `build_gas_permit_path` | Inventory·Pressure·Facility | GasPermitPlan | Regulatory | G3 |
| M-064 | `build_fire_safety_basis` | Layout·FireLoad·Access | FireSafetyBasis | Fire Lead | G3 |
| M-065 | `run_hazid` | PFD·Plot·Modes | HAZIDRegister | HSE | G3 |
| M-066 | `run_hazop_lopa` | Nodes·Safeguards | SafeguardRegister | HSE/Process | G3 |
| M-067 | `run_consequence_analysis` | LeakCases·Weather·Ignition | ConsequenceModel | HSE | G3 |
| M-068 | `screen_psm_applicability` | Inventory·Process | PSMDecision | HSE/Regulatory | G3 |
| M-069 | `screen_environmental_path` | Site·Capacity·Emissions | EIAPath | Environment | G3 |
| M-070 | `permit_readiness_gate` | Legal·Safety·EIA | PermitReadiness | HSE Authority | G3 |

### Phase 7 — FEED·EPC·조달·투자

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-071 | `define_feed_scope` | Concept·Permit | FEEDScope | PMO/Engineering | G4 |
| M-072 | `run_discipline_calculations` | FEEDScope | CalculationSet | Discipline Leads | G4 |
| M-073 | `generate_vendor_datasheets` | Equipment·DesignBasis | VendorDataSheets | Procurement/Engineering | G4 |
| M-074 | `identify_long_lead_items` | Equipment·Market | LongLeadRegister | Procurement | G4 |
| M-075 | `generate_rfp` | FEED·CommercialTerms | RFP | Commercial/Procurement | G4 |
| M-076 | `evaluate_bids` | Bids·ScoringModel | BidMatrix | Procurement/Engineering | G4 |
| M-077 | `select_epc_strategy` | Risk·Funding | EPCStrategy | Commercial/Sponsor | G4 |
| M-078 | `build_baseline_schedule` | Scope·Procurement·Permits | BaselineSchedule | PMO/EPC | G4 |
| M-079 | `estimate_class_cost` | FEED·Bids·Quantities | CostEstimate | Finance | G4 |
| M-080 | `investment_ntp_gate` | Finance·Permit·EPC | NTPDecision | Sponsor | G4 |

### Phase 8 — 상세설계·시공·품질

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-081 | `issue_ifc_drawings` | FEED·ApprovedChanges | IFCSet | Chief Engineer/EPC | G5 |
| M-082 | `track_permit_conditions` | Permits·IFC | PermitConditionTracker | Regulatory/PMO | G5 |
| M-083 | `execute_civil_works` | Site·Geotech·IFC | CivilWorkPackage | Construction | G5 |
| M-084 | `manage_fat` | Equipment·InspectionPlan | FATRecords | QA/Procurement | G5 |
| M-085 | `install_equipment` | Equipment·Foundation·Lifting | AssetRegister | Construction | G5 |
| M-086 | `run_qa_qc` | Assets·ITP·Inspections | QualityDossier | QA/QC | G5 |
| M-087 | `precommission_systems` | Installation·Quality | PrecommissionStatus | Commissioning | G6 |
| M-088 | `generate_commissioning_plan` | Boundaries·Hazards | CommissioningPlan | Commissioning/HSE | G6 |
| M-089 | `run_performance_safety_tests` | Plan·GridConditions | AcceptanceResults | Commissioning/QA | G6 |
| M-090 | `prepare_cod_handover` | Tests·AsBuilt·O&M | CODPackage | Operations | G7 |

### Phase 9 — 운영·정비·규제·AI 학습

| ID | 함수 | 입력 | 출력 | 담당 | Gate |
|---|---|---|---|---|---|
| M-091 | `build_asset_digital_twin` | AsBuilt·Tags·Sensors | AssetTwin | Operations/Data | G7 |
| M-092 | `ingest_h2_telemetry` | Flow·Pressure·Purity·Alarms | H2Telemetry | Operations/Data | G7 |
| M-093 | `calculate_kpis` | Telemetry·Dispatch·Contracts | KPIStream | Operations/Finance | G7 |
| M-094 | `predict_maintenance` | Twin·Telemetry·Failures | MaintenancePlan | Maintenance/Data | G7 |
| M-095 | `manage_safety_events` | Alarms·Incidents·Procedures | SafetyEvent | Operations/HSE | G7 |
| M-096 | `build_compliance_ledger` | Permits·Inspections·Operations | ComplianceLedger | Regulatory/QA | G7 |
| M-097 | `optimize_dispatch` | H2Price·PowerPrice·Limits | DispatchPlan | Operations/Commercial | G7 |
| M-098 | `run_management_of_change` | ChangeRequest·Impact | MOCDecision | PMO/HSE/Engineering | G7 |
| M-099 | `build_evaluation_dataset` | MissionResults·Reviews | EvaluationDataset | AI Safety/Data | G7 |
| M-100 | `operate_engineering_copilot` | Project·Evidence·LiveData | NextMission/Alert | Product/AI | G7 |

## 5. 미션 상태 전이

```text
DEFINED
  → READY
  → RUNNING
  → PASS
  → REVIEW_REQUIRED
  → APPROVED
  → BASELINED
```

예외 전이:

```text
READY → BLOCKED → READY
RUNNING → FAIL → READY
APPROVED → SUPERSEDED
BASELINED → CHANGE_IMPACT_REQUIRED
```

## 6. 오케스트레이터 우선순위

1. 안전·법규·계통 차단조건
2. 게이트 임계경로
3. 외부기관 회신 대기
4. 장기납기·금융·계약 의존성
5. 분야별 설계 미션
6. 문서 포맷·요약·UI 편의기능

AI는 중요도가 낮은 문서 생성으로 안전·허가 차단 미션을 가리지 않는다.
