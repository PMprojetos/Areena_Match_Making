
from mongoengine import Document, StringField, DateTimeField, ReferenceField

class Team(Document):
    name = StringField(required=True, unique=True)

class Match(Document):
    home_team = ReferenceField(Team, required=True)
    away_team = ReferenceField(Team, required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
