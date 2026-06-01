from collections.abc import Iterable, Iterator
from datetime import datetime

from stravalib import Client
from stravalib.model import SummaryActivity


def list_activities(
    client: Client,
    after: datetime,
    sport_types: Iterable[str] | None = None,
) -> Iterator[SummaryActivity]:
    """Yield Strava activities since `after`, optionally filtered by sport type.

    `sport_types` is matched against `Activity.sport_type.root` (e.g. 'Run',
    'Tennis', 'WeightTraining'). We use `sport_type` rather than the legacy
    `type` field because newer sports like Tennis are bucketed under
    `Workout` in `type` but surface as `Tennis` in `sport_type`. Filtering is
    client-side because stravalib's get_activities does not support a
    server-side type filter.
    """
    allowed = set(sport_types) if sport_types is not None else None
    for activity in client.get_activities(after=after):
        if allowed is None or activity.sport_type.root in allowed:
            yield activity
