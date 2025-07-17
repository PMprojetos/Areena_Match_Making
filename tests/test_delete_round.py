import pytest
from datetime import datetime, timedelta
from app.models import Match
from app.services import create_round, delete_round
from mongoengine import connect, disconnect

@pytest.fixture(scope="module")
def db():
    # Disconnect any previous connection, then connect to the test MongoDB database
    disconnect()
    connect("areena_match_making_test_db")
    yield
    # Disconnect after tests complete
    disconnect()

@pytest.fixture(autouse=True)
def clear_matches():
    # Clear all matches before and after each test to ensure test isolation
    Match.objects.delete()
    yield
    Match.objects.delete()

def test_delete_round_removes_matches_correctly(db):
    base_date = datetime(2025, 7, 26)

    # Create a round of matches
    created_matches = create_round(base_date)
    assert len(created_matches) == 10

    # Ensure matches exist in the database
    existing = Match.objects(
        start_time__gte=base_date,
        start_time__lt=base_date.replace(hour=23, minute=59) + timedelta(days=3)
    )
    assert existing.count() == 10

    # Delete the round
    deleted_count = delete_round(base_date)
    assert deleted_count == 10

    # Verify matches were actually removed
    remaining = Match.objects(
        start_time__gte=base_date,
        start_time__lt=base_date.replace(hour=23, minute=59) + timedelta(days=3)
    )
    assert remaining.count() == 0
