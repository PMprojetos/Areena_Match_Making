import pytest
from datetime import datetime, timedelta
from app.models import Team, Match
from app.services import create_round, MatchConflictError
from mongoengine import connect, disconnect
from collections import Counter

@pytest.fixture(scope="module")
def db():
    # Disconnect any previous connection, then connect to test database
    disconnect()
    connect('areena_match_making_test_db')
    yield
    # Disconnect after tests complete
    disconnect()

@pytest.fixture(scope="module")
def all_teams(db):
    # Retrieve all teams, skip tests if fewer than 20
    teams = list(Team.objects.all())
    if len(teams) < 20:
        pytest.skip("Not enough teams in DB (requires 20).")
    return teams

def test_create_round_creates_correct_number_of_matches(all_teams):
    base_date = datetime(2025, 7, 26)  # Saturday

    try:
        matches = create_round(base_date)
    except MatchConflictError as e:
        pytest.fail(f"Unexpected conflict during round creation: {e}")

    # Expect 10 matches (20 teams / 2)
    assert len(matches) == 10

    # Allowed match dates: Saturday, Sunday, Monday
    allowed_dates = {base_date.date(), (base_date + timedelta(days=1)).date(), (base_date + timedelta(days=2)).date()}

    # Count matches per day
    date_counts = Counter(match.start_time.date() for match in matches)

    for match in matches:
        assert match.home_team in all_teams
        assert match.away_team in all_teams
        assert match.start_time.date() in allowed_dates, f"Match date {match.start_time.date()} not in allowed dates"
        assert match.home_team != match.away_team, "A team cannot play against itself"

    # Verify exactly 1 match is scheduled on Monday (28th July)
    assert date_counts[(base_date + timedelta(days=2)).date()] == 1, "There should be exactly 1 match on 28th July"
