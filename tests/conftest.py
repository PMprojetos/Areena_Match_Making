import pytest
from mongoengine import connect
from app.models import Team, Match

TEAM_NAMES = [
    "Flamengo", "Cruzeiro", "Bragantino", "Bahia", "Palmeiras",
    "Botafogo", "Fluminense", "Atlético-MG", "Ceará", "Mirassol",
    "Corinthians", "Grêmio", "Internacional", "Vasco", "São Paulo",
    "Santos", "Juventude", "Vitória", "Fortaleza", "Sport"
]

@pytest.fixture(scope="session", autouse=True)
def mongo_connection():
    connect('areena_match_making_test_db', alias='default')

@pytest.fixture(scope="session", autouse=True)
def seed_teams():
    for name in TEAM_NAMES:
        # Remove duplicatas
        duplicates = Team.objects(name=name)
        if duplicates.count() > 1:
            for duplicate in duplicates[1:]:
                duplicate.delete()

        if not Team.objects(name=name).first():
            Team(name=name).save()

@pytest.fixture(autouse=True)
def clear_matches():
    Match.objects.delete()
