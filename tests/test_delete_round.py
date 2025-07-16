import pytest
from datetime import datetime, timedelta
from app.models import Match
from app.services import create_round, delete_round
from mongoengine import connect, disconnect

@pytest.fixture(scope="module")
def db():
    disconnect()
    connect("areena_match_making_test_db")
    yield
    disconnect()

@pytest.fixture(autouse=True)
def clear_matches():
    Match.objects.delete()
    yield
    Match.objects.delete()

def test_delete_round_removes_matches_correctly(db):
    base_date = datetime(2025, 7, 26)

    # Criar rodada
    created_matches = create_round(base_date)
    assert len(created_matches) == 10

    # Garantir que as partidas existem no banco
    existing = Match.objects(
        start_time__gte=base_date,
        start_time__lt=base_date.replace(hour=23, minute=59) + timedelta(days=3)
    )
    assert existing.count() == 10

    # Deletar a rodada
    deleted_count = delete_round(base_date)
    assert deleted_count == 10

    # Verificar se foram realmente removidas
    remaining = Match.objects(
        start_time__gte=base_date,
        start_time__lt=base_date.replace(hour=23, minute=59) + timedelta(days=3)
    )
    assert remaining.count() == 0
