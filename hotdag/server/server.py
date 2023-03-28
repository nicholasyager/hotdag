from fastapi import FastAPI

from hotdag.__about__ import __version__
from hotdag.server.routers import manifest, url


def get_application():
    app = FastAPI(
        title="HotDAG",
        version=__version__,
    )

    routers = [manifest.router, url.router]
    for router in routers:
        app.include_router(router)

    return app
