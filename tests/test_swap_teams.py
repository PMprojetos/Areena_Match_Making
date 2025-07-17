import pytest
from datetime import datetime, timedelta
from app.models import Team
from app.services import create_match

@pytest.fixture
def clear_db():
    # Clear teams and matches for isolated tests
    Team.objects.delete()
    # If you have a Match model, clear it here as well:
    # Match.objects.delete()

@pytest.fixture
def test_teams(clear_db):
    # Create test teams
    ceara = Team(name="Ceará").save()
    fortaleza = Team(name="Fortaleza").save()
    return ceara, fortaleza

def test_swap_teams_correctly(test_teams, clear_db):
    team_a, team_b = test_teams

    # Valid match: Saturday 18:00 - 20:00 (according to ALLOWED_SLOTS)
    saturday_start = datetime(2025, 7, 26, 18, 0)
    saturday_end = saturday_start + timedelta(hours=2)
    match = create_match(team_a.id, team_b.id, saturday_start, saturday_end)

    # Asserts to ensure the match was created correctly
    assert match.home_team.id == team_a.id
    assert match.away_team.id == team_b.id
    assert match.start_time == saturday_start
    assert match.end_time == saturday_end
