import logging

from sqlmodel import Session

from app.core.db import engine, init_db
from app.core.object_store import store, init_store


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)
    # Init the object store by creating the right buckets
    init_store(store)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
