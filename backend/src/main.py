import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.main import api_router
from api.routes.program import lifespan
from conf.config import get_program_config

# setup_logger(reset=True)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    # mount routers
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
if not get_program_config().dev_mode:
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
    app.mount("/images", StaticFiles(directory="dist/images"), name="images")
    templates = Jinja2Templates(directory="dist")

    @app.get("/{path:path}")
    async def serve_spa(request: Request, path: str):
        context = {"request": request}
        if not path:
            return templates.TemplateResponse("index.html", context)

        dist_dir = Path("dist").resolve()
        file_path = (dist_dir / path).resolve()

        if file_path.is_relative_to(dist_dir) and file_path.is_file():
            return FileResponse(file_path)
        return templates.TemplateResponse("index.html", context)

else:

    @app.get("/", status_code=302, tags=["html"])
    def index():
        return RedirectResponse("/docs")


if __name__ == "__main__":

    uvicorn_logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": logger.handlers,
        "loggers": {
            "uvicorn": {
                "level": logger.level,
            },
            "uvicorn.access": {
                "level": "WARNING",
            },
        },
    }
    if os.getenv("IPV6"):
        host = "::"
    else:
        host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        app,
        host=host,
        port=get_program_config().webui_port,
        log_config=uvicorn_logging_config,
    )
