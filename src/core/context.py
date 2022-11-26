from gino import api, Gino

from . import settings


class Context:
    db: api.Gino = Gino(bind=settings.db)

    on_run: bool = False


context = Context()
