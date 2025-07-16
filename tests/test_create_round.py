import pytest
from datetime import datetime, timedelta
from app.models import Team, Match
from app.services import create_round, MatchConflictError
from mongoengine import connect, disconnect
from collections import Counter

@pytest.fixture(scope="module")
def db():
    disconnect()
    connect('areena_match_making_test_db')
    yield
    disconnect()

@pytest.fixture(scope="module")
def all_teams(db):
    teams = list(Team.objects.all())
    if len(teams) < 20:
        pytest.skip("Not enough teams in DB (requires 20).")
    return teams

def test_create_round_creates_correct_number_of_matches(all_teams):
    base_date = datetime(2025, 7, 26)  # Sábado

    try:
        matches = create_round(base_date)
    except MatchConflictError as e:
        pytest.fail(f"Unexpected conflict during round creation: {e}")

    # Espera-se 10 partidas (20 times / 2)
    assert len(matches) == 10

    allowed_dates = {base_date.date(), (base_date + timedelta(days=1)).date(), (base_date + timedelta(days=2)).date()}

    # Contar partidas por dia
    date_counts = Counter(match.start_time.date() for match in matches)

    for match in matches:
        assert match.home_team in all_teams
        assert match.away_team in all_teams
        assert match.start_time.date() in allowed_dates, f"Match date {match.start_time.date()} not in allowed dates"
        assert match.home_team != match.away_team, "A team cannot play against itself"

    # Validar que só tenha 1 partida no dia 28/07
    assert date_counts[(base_date + timedelta(days=2)).date()] == 1, "There should be exactly 1 match on 28th July"
