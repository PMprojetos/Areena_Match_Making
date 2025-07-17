import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Team
from mongoengine import connect

def seed_teams():
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

    print(f"✅ Seeded {len(teams)} teams.")

if __name__ == "__main__":
    connect("areena_match_making")  # ou o nome do seu banco de produção
    seed_teams()
