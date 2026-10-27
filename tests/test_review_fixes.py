"""Regression tests for the issues found in the project review.

Each test pins one fix so the original loophole cannot silently return.
"""

from __future__ import annotations

import threading

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.simulation import RainfallScenario as S
from app.services import flood_prediction
from app.services.district_service import get_district
from app.services.dispatch_ledger import get_ledger
from app.services.flood_prediction import FloodPredictionService, train_baseline_model
from app.services.hospital_recommendation import recommend_hospital
from app.services.routing_service import build_routing_graph, find_safe_route, get_routing_graph
from app.services.shelter_recommendation import recommend_shelter
from app.services.synthetic_data import generate_training_records, write_training_dataset
from app.services.team_allocation import allocate_team
from tests._images import MUDDY, make_image

API = "/api/v1"
D = get_district()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _decide(client, zone="zone-03", **extra):
    return client.post(f"{API}/decision-engine", data={"incident_zone_id": zone, **extra})


# ---------------------------------------------------------------- 1. no help for worst-hit zones
def test_extreme_scenario_isolated_zone_reports_isolation_and_fallback(client):
    data = _decide(client, "zone-01", scenario="extreme").json()
    assert data["incident_isolated"] is True
    assert data["team_allocation"]["status"] == "no_suitable_team"
    assert data["team_route"] is None
    fallback = data["team_allocation"]["fallback"]
    assert fallback and fallback["mode"] == "water_or_air_access" and fallback["straight_line_km"] > 0
    assert "NOT a routed path" in fallback["advice"]
    assert data["hospital_recommendation"]["fallback"] is not None
    assert data["shelter_recommendation"]["fallback"] is not None
    assert any("cut off" in w for w in data["warnings"])


def test_fallback_not_offered_when_a_road_option_exists(client):
    data = _decide(client, "zone-03", scenario="moderate").json()
    assert data["team_allocation"]["status"] == "success"
    assert data["team_allocation"]["fallback"] is None and data["incident_isolated"] is False


# ---------------------------------------------------------------- 2/3. ML + inputs
def test_ml_severity_changes_scoring_and_priority(client):
    low = recommend_hospital(D, "zone-03", S.SEVERE, incident_severity=5)
    high = recommend_hospital(D, "zone-03", S.SEVERE, incident_severity=95)
    assert low.selected_hospital and high.selected_hospital
    low_w = {f.factor: f.weight for f in low.selected_hospital.reasoning_factors}
    high_w = {f.factor: f.weight for f in high.selected_hospital.reasoning_factors}
    assert high_w["Safe-route distance"] > low_w["Safe-route distance"]
    assert round(sum(high_w.values()), 2) == 1.0 and round(sum(low_w.values()), 2) == 1.0

    t_low = allocate_team(D, "zone-03", S.MODERATE, incident_severity=5)
    t_high = allocate_team(D, "zone-03", S.MODERATE, incident_severity=95)
    assert t_low.selected_team.suitability_score != t_high.selected_team.suitability_score
    assert all(t.suitability_score <= 100 for t in t_high.ranked_teams)

    assert _decide(client, "zone-09", scenario="moderate").json()["priority"] == "routine"
    assert _decide(client, "zone-03", scenario="severe").json()["priority"] == "urgent"
    assert _decide(client, "zone-02", scenario="extreme").json()["priority"] == "critical"


def test_prediction_confidence_reflects_input_support(client):
    inside = client.post(f"{API}/predict", json=dict(rainfall_mm=160, elevation_m=80, drainage_score=5, previous_water_level_m=1.0)).json()
    outside = client.post(f"{API}/predict", json=dict(rainfall_mm=2, elevation_m=80, drainage_score=5, previous_water_level_m=1.0)).json()
    assert inside["confidence"] == "high" and inside["out_of_support_inputs"] == []
    assert outside["confidence"] == "low" and "rainfall_mm" in outside["out_of_support_inputs"]
    assert inside["expected_error_points"] is not None and inside["model_basis"] == "synthetic_training_data"


def test_contradictory_inputs_are_rejected(client):
    assert _decide(client, "zone-05", scenario="moderate", elevation_m="56").status_code == 422   # real: 91 m
    assert _decide(client, "zone-05", scenario="moderate", drainage_score="1").status_code == 422  # real: 8
    assert _decide(client, "zone-05", scenario="extreme", rainfall_mm="5").status_code == 422
    assert _decide(client, "zone-05").status_code == 422  # neither scenario nor rainfall
    ok = _decide(client, "zone-05", scenario="severe", rainfall_mm="150", elevation_m="91", drainage_score="8")
    assert ok.status_code == 200 and ok.json()["input_basis"] == "user_supplied"


def test_scenario_only_request_uses_server_presets_and_says_so(client):
    data = _decide(client, "zone-03", scenario="severe").json()
    assert data["input_basis"] == "scenario_preset"
    assert any("not live sensor data" in w for w in data["warnings"])
    presets = client.get(f"{API}/scenarios").json()
    assert set(presets) == {"moderate", "severe", "extreme"}
    assert data["prediction"]["input_factors"]["rainfall_mm"] == presets["severe"]["rainfall_mm"]
    assert data["prediction"]["input_factors"]["elevation_m"] == 78  # taken from district data


# ---------------------------------------------------------------- 4. damage assessment is never silent
def test_rejected_image_in_decision_engine_is_flagged_not_dropped(client):
    r = client.post(f"{API}/decision-engine", data={"incident_zone_id": "zone-03", "scenario": "severe"},
                    files={"file": ("notes.jpg", b"not an image", "image/jpeg")})
    body = r.json()
    assert r.status_code == 200 and body["damage_assessment"] is None
    assert any("rejected" in w for w in body["warnings"])


def test_valid_image_in_decision_engine_is_assessed_and_reported(client):
    r = client.post(f"{API}/decision-engine", data={"incident_zone_id": "zone-03", "scenario": "severe"},
                    files={"file": ("../../scene.png", make_image(MUDDY), "image/png")}).json()
    assert r["damage_assessment"]["filename"] == "scene.png"
    report = client.post(f"{API}/generate-report", json=r).json()["report_content"]
    assert "no statistical confidence" in report and "Confidence**: 9" not in report


# ---------------------------------------------------------------- 5. routing + concurrency
def test_routing_is_thread_safe_under_concurrent_recommendations_and_rebuilds():
    errors: list[str] = []
    wrong: list[int] = []
    lock = threading.Lock()

    def worker(rebuild: bool):
        for _ in range(120):
            try:
                if rebuild:
                    build_routing_graph(D)
                res = allocate_team(D, "zone-03", S.MODERATE)  # nothing blocked => must always succeed
                if res.status != "success":
                    with lock:
                        wrong.append(1)
            except Exception as exc:  # noqa: BLE001
                with lock:
                    errors.append(type(exc).__name__)

    threads = [threading.Thread(target=worker, args=(i % 4 == 0,)) for i in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert errors == [] and wrong == []


def test_recommenders_do_not_mutate_the_shared_graph():
    graph_before = get_routing_graph(D)
    recommend_hospital(D, "zone-03", S.SEVERE)
    recommend_shelter(D, "zone-03", S.SEVERE)
    allocate_team(D, "zone-03", S.SEVERE)
    assert get_routing_graph(D) is graph_before


def test_route_to_self_is_a_valid_zero_length_route(client):
    data = client.get(f"{API}/route", params=dict(start_id="zone-01", end_id="zone-01", scenario="extreme")).json()
    assert data["status"] == "success" and data["distance_km"] == 0.0 and len(data["path"]) == 1


def test_unreachable_route_is_reported_as_no_route_not_success(client):
    data = _decide(client, "zone-01", scenario="extreme").json()
    # No resource may carry a "success" route with an empty path.
    for key in ("hospital_route", "shelter_route", "team_route"):
        route = data[key]
        assert route is None or (route["status"] == "success" and route["path"])


def test_parallel_roads_between_the_same_zones_are_both_kept():
    from app.models.entities import GeoPoint, Road

    a, b = D.zones[0], D.zones[1]
    extra = Road(id="road-99", name="Parallel", from_zone_id=a.id, to_zone_id=b.id, length_km=5.0,
                 road_class="local", geometry=(a.center, b.center))
    district = D.model_copy(update={"roads": (*D.roads, extra)})
    direct = [r.id for r in D.roads if {r.from_zone_id, r.to_zone_id} == {a.id, b.id}]
    blocked = set(direct)
    path, dist = find_safe_route(a.id, b.id, blocked, district)
    assert path and dist <= 5.0 + 1e-9  # falls back to the parallel road instead of losing it


# ---------------------------------------------------------------- 6. allocation
def test_required_specialty_is_a_hard_constraint():
    res = allocate_team(D, "zone-03", S.MODERATE, required_specialty="paramedic")
    assert res.selected_team.team_id == "team-02"
    assert all("paramedic" in t.specialties for t in res.ranked_teams)
    assert any("lacks the required specialty" in e.reason for e in res.excluded_teams)


def test_specialty_matching_is_case_and_separator_insensitive():
    for variant in ("Boat_Rescue", "boat rescue", " BOAT-RESCUE "):
        assert allocate_team(D, "zone-03", S.MODERATE, required_specialty=variant).selected_team.team_id == "team-01"


def test_unknown_specialty_and_service_are_rejected_with_options(client):
    r = client.get(f"{API}/recommendations/team", params=dict(incident_zone_id="zone-03", required_specialty="helicopter_airlift"))
    assert r.status_code == 422 and "boat_rescue" in r.json()["detail"]
    assert _decide(client, required_specialty="helicopter_airlift", scenario="severe").status_code == 422
    assert client.get(f"{API}/recommendations/hospital", params=dict(start_id="zone-03", required_service="neurosurgery")).status_code == 422


def test_required_hospital_service_is_a_hard_constraint():
    res = recommend_hospital(D, "zone-03", S.MODERATE, required_service="trauma")
    assert res.selected_hospital.hospital_id == "hospital-01"
    assert any("does not offer" in e.reason for e in res.excluded_hospitals)


def test_committed_teams_are_not_double_booked(client):
    ids = []
    for zone in ("zone-03", "zone-05", "zone-09"):
        r = _decide(client, zone, scenario="moderate", commit="true").json()
        assert r["dispatch_committed"] is True
        ids.append(r["team_allocation"]["selected_team"]["team_id"])
    assert len(set(ids)) == 3
    assert len(client.get(f"{API}/dispatch").json()["assignments"]) == 3
    # only 3 teams are AVAILABLE, so a 4th incident has none left
    fourth = _decide(client, "zone-02", scenario="moderate", commit="true").json()
    assert fourth["team_allocation"]["status"] == "no_suitable_team" and fourth["dispatch_committed"] is False


def test_preview_does_not_reserve_and_release_frees_the_team(client):
    team_a = _decide(client, "zone-03", scenario="moderate").json()["team_allocation"]["selected_team"]["team_id"]
    assert client.get(f"{API}/dispatch").json()["assignments"] == []          # preview reserves nothing

    _decide(client, "zone-03", scenario="moderate", commit="true")
    # re-evaluating the SAME incident keeps its own team; a different incident cannot take it
    assert _decide(client, "zone-03", scenario="moderate").json()["team_allocation"]["selected_team"]["team_id"] == team_a
    other = _decide(client, "zone-05", scenario="moderate").json()["team_allocation"]
    assert other["selected_team"]["team_id"] != team_a
    assert any(e["team_id"] == team_a and "committed" in e["reason"] for e in other["excluded_teams"])

    assert client.delete(f"{API}/dispatch/zone-03").status_code == 200
    assert client.delete(f"{API}/dispatch/zone-03").status_code == 404
    assert client.get(f"{API}/dispatch").json()["assignments"] == []
    assert _decide(client, "zone-03", scenario="moderate").json()["team_allocation"]["selected_team"]["team_id"] == team_a


def test_concurrent_commits_never_share_a_team():
    results: list[str | None] = []
    lock = threading.Lock()
    zones = ["zone-03", "zone-05", "zone-09", "zone-02", "zone-04", "zone-08", "zone-10", "zone-06"]

    def commit(zone: str):
        res, _ = get_ledger().commit_allocation(
            zone, lambda reserved: allocate_team(D, zone, S.MODERATE, unavailable_team_ids=reserved),
            lambda r: r.selected_team.team_id if r.selected_team else None)
        with lock:
            results.append(res.selected_team.team_id if res.selected_team else None)

    threads = [threading.Thread(target=commit, args=(z,)) for z in zones]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assigned = [r for r in results if r]
    assert len(assigned) == len(set(assigned)) == 3


def test_capacity_gap_is_surfaced(client):
    warnings = _decide(client, "zone-03", scenario="extreme").json()["warnings"]
    assert any("Capacity gap" in w for w in warnings)


def test_shelter_explanation_describes_the_selected_shelter():
    res = recommend_shelter(D, "zone-03", S.MODERATE)
    top = max(res.selected_shelter.reasoning_factors, key=lambda f: f.contribution)
    assert top.factor.lower() in res.explanation


# ---------------------------------------------------------------- 7. report integrity
def test_forged_or_unsigned_bundles_cannot_produce_reports(client):
    good = _decide(client, "zone-03", scenario="severe").json()
    assert good["signature"]
    assert client.post(f"{API}/generate-report", json=good).status_code == 200

    forged = {**good, "prediction": {**good["prediction"], "predicted_flood_severity": 1.0}}
    assert client.post(f"{API}/generate-report", json=forged).status_code == 400
    renamed = {**good, "incident_zone_id": "zone-99 <script>alert(1)</script>"}
    assert client.post(f"{API}/generate-report", json=renamed).status_code == 400
    unsigned = {k: v for k, v in good.items() if k != "signature"}
    assert client.post(f"{API}/generate-report", json=unsigned).status_code == 400


def test_report_is_well_formed_and_honest(client):
    good = _decide(client, "zone-03", scenario="severe").json()
    report = client.post(f"{API}/generate-report", json=good).json()["report_content"]
    lines = report.splitlines()
    assert lines[0] == "# RescueTwin AI Incident Report"
    assert all(not l.startswith("    ") for l in lines)          # no accidental code-block indentation
    assert "real-time" not in report.lower()
    assert "not live sensor data" in report and "synthetic data" in report


# ---------------------------------------------------------------- 8. security
def test_api_key_is_enforced_when_configured(client, monkeypatch):
    monkeypatch.setenv("RESCUETWIN_API_KEY", "s3cret")
    assert client.get(f"{API}/health").status_code == 200                     # health stays public
    assert client.get(f"{API}/district").status_code == 401
    assert client.get(f"{API}/district", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get(f"{API}/district", headers={"X-API-Key": "s3cret"}).status_code == 200


def test_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.setenv("RESCUETWIN_RATE_LIMIT_PER_MIN", "3")
    codes = [client.get(f"{API}/district").status_code for _ in range(6)]
    assert codes[:3] == [200, 200, 200] and codes[3:] == [429, 429, 429]
    assert client.get(f"{API}/district").headers.get("retry-after")
    assert client.get(f"{API}/health").status_code == 200                     # health exempt


def test_oversized_request_is_rejected_early(client):
    r = client.post(f"{API}/decision-engine", data={"incident_zone_id": "zone-03", "scenario": "severe"},
                    files={"file": ("a.jpg", b"\xff\xd8" + b"0" * (9 * 1024 * 1024), "image/jpeg")})
    assert r.status_code == 413


# ---------------------------------------------------------------- 9. model artifact
def test_artifact_is_native_json_with_integrity_check(tmp_path):
    csv_path, artifact = tmp_path / "t.csv", tmp_path / "model.json"
    write_training_dataset(csv_path, generate_training_records(sample_count=400))
    train_baseline_model(csv_path, artifact)
    FloodPredictionService(artifact)                                      # loads fine
    artifact.write_text(artifact.read_text().replace("0", "1", 1))        # tamper
    with pytest.raises(ValueError, match="integrity"):
        FloodPredictionService(artifact)


def test_non_json_artifact_path_is_refused(tmp_path):
    csv_path = tmp_path / "t.csv"
    write_training_dataset(csv_path, generate_training_records(sample_count=400))
    with pytest.raises(ValueError, match=r"\.json"):
        train_baseline_model(csv_path, tmp_path / "model.joblib")


def test_default_paths_are_not_hardcoded_to_docker():
    assert str(flood_prediction.DEFAULT_DATASET_PATH) != "/app/data/flood_training.csv"
    assert flood_prediction.DEFAULT_DATASET_PATH.exists()
    assert flood_prediction.DEFAULT_ARTIFACT_PATH.exists()
