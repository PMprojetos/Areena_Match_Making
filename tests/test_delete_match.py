import pytest
from bson import ObjectId
from datetime import datetime
from app.models import Team, Match
from app.services import delete_match
from mongoengine import connect, disconnect

@pytest.fixture(scope="module")
def db():
    # Disconnect any existing connection and connect to the test MongoDB
    disconnect()
    connect('areena_match_making_test_db')
    yield
    # Disconnect after tests complete
    disconnect()

@pytest.fixture(scope="module")
def test_teams(db):
    # Fetch two teams from DB, skip tests if fewer than 2 teams available
    teams = list(Team.objects.all())
    if len(teams) < 2:
        pytest.skip("Not enough teams in DB (requires at least 2).")
    return teams[:2]

@pytest.fixture(scope="function")
def clear_matches(db):
    # Clear matches before and after each test to ensure isolation
    Match.objects.delete()
    yield
    Match.objects.delete()

def test_delete_existing_match(clear_matches, test_teams):
    team_a, team_b = test_teams

    # Create a match to delete
    match = Match(
        home_team=team_a,
        away_team=team_b,
        start_time=datetime(2025, 7, 26, 18, 0),
        end_time=datetime(2025, 7, 26, 20, 0)
    )
    match.save()

    # Confirm match exists before deletion
    assert Match.objects(id=match.id).first() is not None

    # Delete the match
    delete_match(match.id)

    # Confirm match no longer exists
    assert Match.objects(id=match.id).first() is None

def test_delete_nonexistent_match(clear_matches):
    fake_id = ObjectId()

    # Expect ValueError when trying to delete a non-existent match
    with pytest.raises(ValueError, match="Match not found"):
        delete_match(fake_id)
