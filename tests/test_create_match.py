import pytest
from datetime import datetime, timedelta
from app.services import create_match, MatchConflictError
from app.models import Team, Match
from mongoengine import connect, disconnect

@pytest.fixture(scope='module')
def db():
    disconnect()
    connect('areena_match_making_test_db')  # Banco de testes MongoDB
    yield
    disconnect()

@pytest.fixture(scope='function')
def clear_matches(db):
    # Limpa partidas antes e depois de cada teste
    Match.objects.delete()
    yield
    Match.objects.delete()

@pytest.fixture(scope='module')
def teams(db):
    # Verifica se times existem, senão cria
    team_a = Team.objects(name="Fortaleza").first()
    team_b = Team.objects(name="Ceará").first()
    if not team_a:
        team_a = Team(name="Fortaleza").save()
    if not team_b:
        team_b = Team(name="Ceará").save()
    return team_a, team_b

def test_create_valid_match(teams, clear_matches):
    team_a, team_b = teams

    start_time = datetime(2025, 7, 26, 18, 0, 0)  # Sábado, 18h–20h (válido)
    end_time = start_time + timedelta(hours=2)

    match = create_match(team_a.id, team_b.id, start_time, end_time)

    assert match is not None
    assert match.home_team == team_a
    assert match.away_team == team_b
    assert match.start_time == start_time
    assert match.end_time == end_time

def test_create_overlapping_match_raises(teams, clear_matches):
    team_a, team_b = teams

    start_time = datetime(2025, 7, 26, 18, 0, 0)  # Sábado, 18h–20h (válido)
    end_time = start_time + timedelta(hours=2)

    create_match(team_a.id, team_b.id, start_time, end_time)

    # Tentativa de criar partida que se sobrepõe em pelo menos 30 minutos
    with pytest.raises(MatchConflictError):
        create_match(
            team_a.id, team_b.id,
            start_time + timedelta(minutes=30),
            end_time + timedelta(minutes=30)
        )

def test_create_match_respecting_66h_rule(teams, clear_matches):
    team_a, team_b = teams

    # Primeira partida válida
    start_time = datetime(2025, 7, 27, 11, 0, 0)  # Domingo, 11h–13h
    end_time = start_time + timedelta(hours=2)
    create_match(team_a.id, team_b.id, start_time, end_time)

    # Tentativa de criar partida muito próxima (violando regra de 66 horas)
    too_soon_start = datetime(2025, 7, 28, 20, 0, 0)  # Segunda, 20h–22h (válido, mas dentro do intervalo)
    too_soon_end = too_soon_start + timedelta(hours=2)

    with pytest.raises(MatchConflictError):
        create_match(team_a.id, team_b.id, too_soon_start, too_soon_end)
