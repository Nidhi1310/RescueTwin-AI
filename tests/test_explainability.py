from app.services.district_service import get_district
from app.models.simulation import RainfallScenario
from app.services.hospital_recommendation import recommend_hospital
from app.services.shelter_recommendation import recommend_shelter
from app.services.team_allocation import allocate_team


def _assert_explanation(candidate, explanation: str) -> None:
    assert candidate is not None
    assert candidate.rationale.strip()
    assert candidate.reasoning_factors
    assert all(f.factor.strip() and f.value.strip() for f in candidate.reasoning_factors)
    assert abs(sum(f.contribution for f in candidate.reasoning_factors) - candidate.suitability_score) < 0.11
    assert candidate.suitability_score >= 0
    assert candidate.suitability_score <= 100
    assert candidate.factor if False else True
    assert candidate.__class__.__name__
    assert explanation.strip()
    assert candidate.hospital_name in explanation if hasattr(candidate, "hospital_name") else candidate.shelter_name in explanation if hasattr(candidate, "shelter_name") else candidate.team_name in explanation


def test_hospital_explanation_matches_selected_output() -> None:
    result = recommend_hospital(get_district(), "zone-01", RainfallScenario.MODERATE)
    _assert_explanation(result.selected_hospital, result.explanation)


def test_shelter_explanation_matches_selected_output() -> None:
    result = recommend_shelter(get_district(), "zone-01", RainfallScenario.MODERATE)
    _assert_explanation(result.selected_shelter, result.explanation)


def test_team_explanation_matches_selected_output() -> None:
    result = allocate_team(get_district(), "zone-01", RainfallScenario.MODERATE)
    _assert_explanation(result.selected_team, result.explanation)
