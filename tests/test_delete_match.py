import pytest
from bson import ObjectId
from datetime import datetime
from app.models import Team, Match
from app.services import delete_match
from mongoengine import connect, disconnect

@pytest.fixture(scope="module")
def db():
    disconnect()
    connect('areena_match_making_test_db')
    yield
    disconnect()

@pytest.fixture(scope="module")
def test_teams(db):
    teams = list(Team.objects.all())
    if len(teams) < 2:
        pytest.skip("Not enough teams in DB (requires at least 2).")
    return teams[:2]  # retorna dois times para usar nos testes

@pytest.fixture(scope="function")
def clear_matches(db):
    Match.objects.delete()
    yield
    Match.objects.delete()

def test_delete_existing_match(clear_matches, test_teams):
    team_a, team_b = test_teams

    # Criar um jogo para deletar
    match = Match(
        home_team=team_a,
        away_team=team_b,
        start_time=datetime(2025, 7, 26, 18, 0),
        end_time=datetime(2025, 7, 26, 20, 0)
    )
    match.save()

    # Verificar que existe
    assert Match.objects(id=match.id).first() is not None

    # Deletar o jogo
    delete_match(match.id)

    # Verificar que foi deletado
    assert Match.objects(id=match.id).first() is None

def test_delete_nonexistent_match(clear_matches):
    fake_id = ObjectId()

    # Espera-se ValueError porque não existe o jogo
    with pytest.raises(ValueError, match="Match not found"):
        delete_match(fake_id)
