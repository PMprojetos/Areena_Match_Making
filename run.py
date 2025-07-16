from flask import Flask
from flask_graphql import GraphQLView
from app.schema import schema
from app.scheduler import schedule_next_match
from datetime import datetime
import pytz
import webbrowser
import threading

app = Flask(__name__)

# Endpoint GraphQL
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Interface web para testes
    )
)

def open_browser():
    webbrowser.open_new("http://localhost:5000/graphql")

if __name__ == '__main__':
    # Abre o navegador em outra thread para não bloquear
    threading.Timer(1.0, open_browser).start()

    # Agenda a próxima partida começando agora (UTC)
    utc_now = datetime.now(pytz.UTC)
    match = schedule_next_match(utc_now)

    if match:
        print(f"Match scheduled: {match.home_team.name} vs {match.away_team.name} at {match.start_time}")
    else:
        print("No valid match found to schedule.")

    # Roda o servidor Flask
    app.run(debug=True)
