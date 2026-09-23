import os


BACKEND_URL = os.getenv(
    "AUTOAI_BACKEND_URL",
    "http://127.0.0.1:8000",
)

USER_ID = int(
    os.getenv(
        "AUTOAI_USER_ID",
        "1",
    )
)

HEARTBEAT_INTERVAL = int(
    os.getenv(
        "AUTOAI_HEARTBEAT_INTERVAL",
        "30",
    )
)


GREENHOUSE_BOARDS = [
    board.strip()
    for board in os.getenv(
        "AUTOAI_GREENHOUSE_BOARDS",
        "",
    ).split(",")
    if board.strip()
]
