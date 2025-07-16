from app.models import Team
from app.services import create_match, MatchConflictError
from datetime import timedelta, datetime, time
import pytz

ALLOWED_SLOTS = {
    5: [  # Saturday
        (time(18, 0), time(20, 0)),
        (time(20, 30), time(22, 30)),
    ],
    6: [  # Sunday
        (time(11, 0), time(13, 0)),
        (time(16, 0), time(18, 0)),
        (time(20, 30), time(22, 30)),
    ],
    0: [  # Monday
        (time(20, 0), time(22, 0)),
    ],
    2: [  # Wednesday
        (time(20, 30), time(22, 30)),
        (time(21, 30), time(23, 30)),
    ],
    3: [  # Thursday
        (time(20, 30), time(22, 30)),
        (time(21, 30), time(23, 30)),
    ],
}

def schedule_next_match(start_after, duration=timedelta(hours=2)):
    if start_after.tzinfo is None:
        start_after = start_after.replace(tzinfo=pytz.UTC)
    else:
        start_after = start_after.astimezone(pytz.UTC)

    teams = list(Team.objects.all())
    n = len(teams)

    current_day = start_after.date()
    max_days = 30  # tentativas futuras

    for day_offset in range(max_days):
        day = current_day + timedelta(days=day_offset)
        weekday = day.weekday()

        if weekday not in ALLOWED_SLOTS:
            continue

        for slot_start, slot_end in ALLOWED_SLOTS[weekday]:
            proposed_start = datetime.combine(day, slot_start, tzinfo=pytz.UTC)
            proposed_end = datetime.combine(day, slot_end, tzinfo=pytz.UTC)

            if proposed_start < start_after:
                continue  # ignora slots já passados

            for i in range(n):
                for j in range(i + 1, n):
                    home_team = teams[i]
                    away_team = teams[j]

                    try:
                        return create_match(home_team.id, away_team.id, proposed_start, proposed_end)
                    except MatchConflictError:
                        continue
                    except Exception:
                        continue

    return None  # nenhuma combinação válida encontrada
