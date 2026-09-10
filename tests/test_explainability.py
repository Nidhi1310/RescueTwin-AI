from app.models.simulation import RainfallScenario
from app.services.district_service import get_district
from app.services.hospital_recommendation import recommend_hospital
from app.services.shelter_recommendation import recommend_shelter
from app.services.team_allocation import allocate_team


def _assert_reasoning(candidate, explanation: str, selected_name: str) -> None:
    assert explanation.strip()
    assert selected_name in explanation
    assert candidate.rationale.strip()
    assert candidate.reasoning_factors
    assert all(factor.factor.strip() and factor.value.strip() for factor in candidate.reasoning_factors)
    assert abs(sum(factor.contribution for factor in candidate.reasoning_factors) - candidate.suitability_score) < 0.2


def test_all_recommendations_are_explainable_and_aligned() -> None:
    district = get_district()
    scenario = RainfallScenario.MODERATE

    hospital = recommend_hospital(district, "team-01", scenario)
    assert hospital.selected_hospital is not None
    _assert_reasoning(hospital.selected_hospital, hospital.explanation, hospital.selected_hospital.hospital_name)

    shelter = recommend_shelter(district, "team-01", scenario)
    assert shelter.selected_shelter is not None
    _assert_reasoning(shelter.selected_shelter, shelter.explanation, shelter.selected_shelter.shelter_name)

    team = allocate_team(district, "zone-05", scenario)
    assert team.selected_team is not None
    _assert_reasoning(team.selected_team, team.explanation, team.selected_team.team_name)
