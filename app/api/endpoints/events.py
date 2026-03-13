from fastapi import APIRouter

# FIXME: This is a set of mock data. Implement database.
events_mock = [
    {
        "title": "Comic Square 9",
        "description": "Comic Square returns once again! Buy and collect goods from your favourite circles!",
    },
    {
        "title": "ANIMONIUM 2026",
        "description": "Bringing Anime Dreams to Life",
    },
    {
        "title": "NIPPON HAKU BANGKOK",
        "description": "Step into Japan—Right in the Heart of Bangkok!\nCelebrate the 10th anniversary of the ultimate Japanese expo that brings together every passion in one place—education, travel, arts, food, lifestyle, technology, and hobbies.\nExplore booths from across Japan and exhibitions by leading organizations from both Japan and Thailand.\nEnjoy exclusive activities and special appearances by Japanese artists.\nFree admission!",
    },
    {
        "title": "Comic Avenue 10",
        "description": "Lorem ipsum, I don't know what to use as mock text.",
    },
]

router = APIRouter()


@router.get("/")
def get_events():
    return events_mock
