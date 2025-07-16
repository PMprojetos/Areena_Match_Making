import pytest
from app.models import Team

@pytest.fixture(scope='module')
def seeded_teams():
    team_names = [
        "Flamengo", "Cruzeiro", "Bragantino", "Bahia", "Palmeiras", "Botafogo",
        "Fluminense", "Atlético-MG", "Ceará", "Mirassol", "Corinthians", "Grêmio",
        "Internacional", "Vasco", "São Paulo", "Santos", "Juventude", "Vitória",
        "Fortaleza", "Sport"
    ]
    teams = []

    for name in team_names:
        team = Team.objects(name=name).first()
        if not team:
            team = Team(name=name)
            team.save()
        teams.append(team)

    return teams
