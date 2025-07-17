import graphene
from graphene_mongo import MongoengineObjectType
from app.models import Team as TeamModel, Match as MatchModel
from app.db import init_db
from app.services import (
    create_match,
    create_round,
    delete_round,
    delete_match,
    swap_teams,
    MatchConflictError,
)
from bson import ObjectId
from datetime import datetime
import pytz

# Initialize MongoDB connection
init_db()

# GraphQL object type for Team model
class Team(MongoengineObjectType):
    class Meta:
        model = TeamModel

# GraphQL object type for Match model, with custom field mapping
class Match(MongoengineObjectType):
    class Meta:
        model = MatchModel

    startTime = graphene.DateTime(source='start_time')
    endTime = graphene.DateTime(source='end_time')

# Payloads for mutation responses
class CreateMatchPayload(graphene.ObjectType):
    match = graphene.Field(Match)
    success = graphene.Boolean()
    message = graphene.String()

class CreateRoundPayload(graphene.ObjectType):
    matches = graphene.List(Match)
    success = graphene.Boolean()
    message = graphene.String()

class DeleteRoundPayload(graphene.ObjectType):
    deleted_count = graphene.Int()
    success = graphene.Boolean()
    message = graphene.String()

class DeleteMatchPayload(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()

class SwapTeamsPayload(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    swapped_matches = graphene.List(Match)

# Converts a string to a MongoDB ObjectId, or raises a ValueError
def to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise ValueError(f"Invalid ID format: {id_str}")

# Ensures datetime object is timezone-aware and in UTC
def ensure_utc(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    else:
        dt = dt.astimezone(pytz.UTC)
    return dt

# Mutation for creating a match between two teams
class CreateMatch(graphene.Mutation):
    class Arguments:
        home_team_id = graphene.ID(required=True)
        away_team_id = graphene.ID(required=True)
        start_time = graphene.DateTime(required=True)
        end_time = graphene.DateTime(required=True)

    Output = CreateMatchPayload

    def mutate(self, info, home_team_id, away_team_id, start_time, end_time):
        try:
            home_team_id_obj = to_object_id(home_team_id)
            away_team_id_obj = to_object_id(away_team_id)
            start_time_utc = ensure_utc(start_time)
            end_time_utc = ensure_utc(end_time)

            match = create_match(
                home_team_id=home_team_id_obj,
                away_team_id=away_team_id_obj,
                start_time=start_time_utc,
                end_time=end_time_utc,
            )
            return CreateMatchPayload(match=match, success=True, message="Match created successfully")

        except MatchConflictError as e:
            return CreateMatchPayload(match=None, success=False, message=str(e))

        except ValueError as e:
            return CreateMatchPayload(match=None, success=False, message=str(e))

        except Exception:
            return CreateMatchPayload(match=None, success=False, message="Unexpected error occurred.")

# Mutation to automatically create a round of matches starting from a base date
class CreateRound(graphene.Mutation):
    class Arguments:
        base_date = graphene.String(required=False)

    Output = CreateRoundPayload

    def mutate(self, info, base_date=None):
        try:
            base_date = datetime.fromisoformat(base_date) if base_date else datetime(2025, 7, 26)
            matches = create_round(base_date)
            return CreateRoundPayload(success=True, message="Round created successfully", matches=matches)
        except Exception as e:
            return CreateRoundPayload(success=False, message=str(e), matches=[])

# Mutation to delete all matches in a round based on date
class DeleteRound(graphene.Mutation):
    class Arguments:
        base_date = graphene.String(required=False)

    Output = DeleteRoundPayload

    def mutate(self, info, base_date=None):
        try:
            base_date = datetime.fromisoformat(base_date) if base_date else datetime(2025, 7, 26)
            deleted_count = delete_round(base_date)
            return DeleteRoundPayload(success=True, message="Round deleted successfully", deleted_count=deleted_count)
        except Exception as e:
            return DeleteRoundPayload(success=False, message=str(e), deleted_count=0)

# Mutation to delete a single match by its ID
class DeleteMatch(graphene.Mutation):
    class Arguments:
        match_id = graphene.ID(required=True)

    Output = DeleteMatchPayload

    def mutate(self, info, match_id):
        try:
            obj_id = to_object_id(match_id)
            delete_match(obj_id)
            return DeleteMatchPayload(success=True, message="Match deleted successfully.")
        except ValueError as e:
            return DeleteMatchPayload(success=False, message=str(e))
        except Exception:
            return DeleteMatchPayload(success=False, message="Unexpected error occurred.")

# Mutation to swap all scheduled matches between two teams
class SwapTeams(graphene.Mutation):
    class Arguments:
        team_a_id = graphene.ID(required=True)
        team_b_id = graphene.ID(required=True)

    Output = SwapTeamsPayload

    def mutate(self, info, team_a_id, team_b_id):
        try:
            team_a_obj_id = to_object_id(team_a_id)
            team_b_obj_id = to_object_id(team_b_id)
            matches = swap_teams(team_a_obj_id, team_b_obj_id)

            return SwapTeamsPayload(
                success=True,
                message=f"Swapped all matches between team {team_a_id} and {team_b_id}",
                swapped_matches=matches
            )
        except ValueError as e:
            return SwapTeamsPayload(success=False, message=str(e), swapped_matches=[])
        except Exception:
            return SwapTeamsPayload(success=False, message="Unexpected error occurred.", swapped_matches=[])

# Root mutation class
class Mutation(graphene.ObjectType):
    create_match = CreateMatch.Field()
    create_round = CreateRound.Field()
    delete_round = DeleteRound.Field()
    delete_match = DeleteMatch.Field()
    swap_teams = SwapTeams.Field()

# Root query class
class Query(graphene.ObjectType):
    all_matches = graphene.List(Match)
    all_teams = graphene.List(Team)

    def resolve_all_matches(self, info):
        return list(MatchModel.objects.all())

    def resolve_all_teams(self, info):
        return list(TeamModel.objects.all())

# GraphQL schema definition
schema = graphene.Schema(query=Query, mutation=Mutation)
