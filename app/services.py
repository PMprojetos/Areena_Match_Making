from app.models import Match, Team
from datetime import datetime, timedelta
from app.models import Match, Team, Venue
import random

class MatchConflictError(Exception):
    pass

# Allowed match time slots by weekday
ALLOWED_SLOTS = {
    "Saturday": [(18, 0, 20, 0), (20, 30, 22, 30)],
    "Sunday": [(11, 0, 13, 0), (16, 0, 18, 0), (20, 30, 22, 30)],
    "Monday": [(20, 0, 22, 0)],
    "Wednesday": [(20, 30, 22, 30), (21, 30, 23, 30)],
    "Thursday": [(20, 30, 22, 30), (21, 30, 23, 30)],
}

def is_valid_timeslot(start_time, end_time):
    """
    Check if the given start and end times fall within an allowed slot for that weekday.
    """
    day_name = start_time.strftime('%A')
    allowed_slots = ALLOWED_SLOTS.get(day_name, [])

    for slot_start_hour, slot_start_min, slot_end_hour, slot_end_min in allowed_slots:
        expected_start = start_time.replace(hour=slot_start_hour, minute=slot_start_min, second=0, microsecond=0)
        expected_end = start_time.replace(hour=slot_end_hour, minute=slot_end_min, second=0, microsecond=0)
        if start_time == expected_start and end_time == expected_end:
            return True
    return False

def create_match(home_team_id, away_team_id, start_time, end_time, venue_id):
    """
    Creates a match between two teams at the given time if there are no conflicts.
    """
    if not is_valid_timeslot(start_time, end_time):
        raise MatchConflictError("Match must be scheduled in an allowed time slot and day.")

    home_team = Team.objects(id=home_team_id).first()
    away_team = Team.objects(id=away_team_id).first()
    venue = Venue.objects(id=venue_id).first()
    if not home_team or not away_team:
        raise ValueError("One or both teams not found")

    # Check for time overlap with other matches involving either team
    conflicting_matches = Match.objects.filter(
        start_time__lt=end_time,
        end_time__gt=start_time,
        __raw__={
            "$or": [
                {"home_team": home_team.id},
                {"away_team": home_team.id},
                {"home_team": away_team.id},
                {"away_team": away_team.id}
            ]
        }
    )
    if conflicting_matches:
        raise MatchConflictError("One or both teams are already scheduled for another match during this time.")

    # Check 66-hour rest rule for both teams
    cutoff_start = start_time - timedelta(hours=66)
    cutoff_end = end_time + timedelta(hours=66)

    recent_matches = Match.objects.filter(
        __raw__={
            "$and": [
                {
                    "$or": [
                        {"home_team": home_team.id},
                        {"away_team": home_team.id},
                        {"home_team": away_team.id},
                        {"away_team": away_team.id}
                    ]
                },
                {
                    "$or": [
                        {"end_time": {"$gte": cutoff_start, "$lte": start_time}},
                        {"start_time": {"$gte": end_time, "$lte": cutoff_end}}
                    ]
                }
            ]
        }
    )
    if recent_matches:
        raise MatchConflictError("One or both teams have a match too close to this one (66h rest rule).")

    match = Match(
        home_team=home_team,
        away_team=away_team,
        start_time=start_time,
        end_time=end_time,
        venue = venue
    )
    match.save()
    return match

def create_round(base_date: datetime):
    """
    Creates a full round of 10 matches using the allowed weekend slots.
    """
    teams = list(Team.objects.all())
    if len(teams) < 20:
        raise ValueError("A full round requires at least 20 teams.")

    random.shuffle(teams)
    pairs = list(zip(teams[::2], teams[1::2]))

    weekend_slots = [
        ("Saturday", ALLOWED_SLOTS["Saturday"][0]),
        ("Saturday", ALLOWED_SLOTS["Saturday"][1]),
        ("Saturday", ALLOWED_SLOTS["Saturday"][0]),
        ("Saturday", ALLOWED_SLOTS["Saturday"][1]),
        ("Sunday", ALLOWED_SLOTS["Sunday"][0]),
        ("Sunday", ALLOWED_SLOTS["Sunday"][1]),
        ("Sunday", ALLOWED_SLOTS["Sunday"][2]),
        ("Sunday", ALLOWED_SLOTS["Sunday"][0]),
        ("Sunday", ALLOWED_SLOTS["Sunday"][1]),
        ("Monday", ALLOWED_SLOTS["Monday"][0]),
    ]

    if len(pairs) != len(weekend_slots):
        raise ValueError("Mismatch between number of matches and time slots")

    matches = []
    for (home, away), (day, slot) in zip(pairs, weekend_slots):
        date = base_date
        while date.strftime('%A') != day:
            date += timedelta(days=1)

        h_start, m_start, h_end, m_end = slot
        start = date.replace(hour=h_start, minute=m_start, second=0, microsecond=0)
        end = date.replace(hour=h_end, minute=m_end, second=0, microsecond=0)

        match = create_match(home.id, away.id, start, end)
        matches.append(match)

    return matches

def delete_round(base_date: datetime):
    """
    Deletes all matches scheduled between the given date and 7 days after.
    """
    round_days = ["Saturday", "Sunday", "Monday"]
    start_of_round = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_round = start_of_round + timedelta(days=7)

    matches = Match.objects(
        start_time__gte=start_of_round,
        start_time__lt=end_of_round
    )

    count = matches.count()
    matches.delete()
    return count

def delete_match(match_id):
    """
    Deletes a match by its ID.
    """
    match = Match.objects(id=match_id).first()
    if not match:
        raise ValueError("Match not found")
    match.delete()
    return True

def swap_teams(team_a_id, team_b_id):
    """
    Swaps all occurrences of team A and team B in existing matches.
    """
    team_a = Team.objects(id=team_a_id).first()
    team_b = Team.objects(id=team_b_id).first()
    if not team_a or not team_b:
        raise ValueError("One or both teams not found")

    matches = Match.objects.filter(
        __raw__={
            "$or": [
                {"home_team": team_a.id},
                {"away_team": team_a.id},
                {"home_team": team_b.id},
                {"away_team": team_b.id},
            ]
        }
    )

    swapped = []
    for match in matches:
        updated = False
        if match.home_team == team_a:
            match.home_team = team_b
            updated = True
        elif match.home_team == team_b:
            match.home_team = team_a
            updated = True

        if match.away_team == team_a:
            match.away_team = team_b
            updated = True
        elif match.away_team == team_b:
            match.away_team = team_a
            updated = True

        if updated:
            match.save()
            swapped.append(match)

    return swapped
