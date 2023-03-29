from fastapi import FastAPI

from hotdag.__about__ import __version__
from hotdag.server.routers import cloud, manifest, url


def get_application():
    app = FastAPI(
        title="HotDAG",
        version=__version__,
    )

    routers = [manifest.router, url.router, cloud.router]
    for router in routers:
        app.include_router(router)

    return app
