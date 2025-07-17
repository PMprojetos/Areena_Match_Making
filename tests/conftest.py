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
    # Connect to the test MongoDB database once per test session
    connect('areena_match_making_test_db', alias='default')

@pytest.fixture(scope="session", autouse=True)
def seed_teams():
    # Seed the database with predefined teams before tests run
    for name in TEAM_NAMES:
        # Remove duplicates if any exist
        duplicates = Team.objects(name=name)
        if duplicates.count() > 1:
            for duplicate in duplicates[1:]:
                duplicate.delete()

        # Create the team if it does not exist yet
        if not Team.objects(name=name).first():
            Team(name=name).save()

@pytest.fixture(autouse=True)
def clear_matches():
    # Clear all matches before each test to ensure isolation
    Match.objects.delete()
