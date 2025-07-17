import pytest
from datetime import datetime, timedelta
from app.services import create_match, MatchConflictError
from app.models import Team, Match
from mongoengine import connect, disconnect

@pytest.fixture(scope='module')
def db():
    # Disconnect any previous connection, then connect to the test MongoDB database
    disconnect()
    connect('areena_match_making_test_db')  # MongoDB test database
    yield
    # Disconnect after all tests in the module complete
    disconnect()

@pytest.fixture(scope='function')
def clear_matches(db):
    # Clear all matches before and after each test to ensure test isolation
    Match.objects.delete()
    yield
    Match.objects.delete()

@pytest.fixture(scope='module')
def teams(db):
    # Ensure test teams exist, create them if they don't
    team_a = Team.objects(name="Fortaleza").first()
    team_b = Team.objects(name="Ceará").first()
    if not team_a:
        team_a = Team(name="Fortaleza").save()
    if not team_b:
        team_b = Team(name="Ceará").save()
    return team_a, team_b

def test_create_valid_match(teams, clear_matches):
    team_a, team_b = teams

    start_time = datetime(2025, 7, 26, 18, 0, 0)  # Saturday, 6pm–8pm (valid slot)
    end_time = start_time + timedelta(hours=2)

    match = create_match(team_a.id, team_b.id, start_time, end_time)

    assert match is not None
    assert match.home_team == team_a
    assert match.away_team == team_b
    assert match.start_time == start_time
    assert match.end_time == end_time

def test_create_overlapping_match_raises(teams, clear_matches):
    team_a, team_b = teams

    start_time = datetime(2025, 7, 26, 18, 0, 0)  # Saturday, 6pm–8pm (valid slot)
    end_time = start_time + timedelta(hours=2)

    create_match(team_a.id, team_b.id, start_time, end_time)

    # Attempt to create a match overlapping by at least 30 minutes (should raise)
    with pytest.raises(MatchConflictError):
        create_match(
            team_a.id, team_b.id,
            start_time + timedelta(minutes=30),
            end_time + timedelta(minutes=30)
        )

def test_create_match_respecting_66h_rule(teams, clear_matches):
    team_a, team_b = teams

    # First valid match
    start_time = datetime(2025, 7, 27, 11, 0, 0)  # Sunday, 11am–1pm
    end_time = start_time + timedelta(hours=2)
    create_match(team_a.id, team_b.id, start_time, end_time)

    # Attempt to create a match too soon (violating 66-hour rest rule)
    too_soon_start = datetime(2025, 7, 28, 20, 0, 0)  # Monday, 8pm–10pm (valid slot but too close)
    too_soon_end = too_soon_start + timedelta(hours=2)

    with pytest.raises(MatchConflictError):
        create_match(team_a.id, team_b.id, too_soon_start, too_soon_end)
