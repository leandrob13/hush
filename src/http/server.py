import asyncio
from fastapi import FastAPI, APIRouter
from gunicorn.app.base import BaseApplication

from src.http.config import APP_PORT, APP_WORKERS
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from loguru import logger as loguru_logger, Logger
from src.app.adapters.http.errors import DtoValidationErrors


class Server(BaseApplication):

    app: FastAPI = FastAPI()

    logger: Logger = loguru_logger

    options = {
        "bind": f"0.0.0.0:{APP_PORT}",
        "workers": APP_WORKERS,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }

    def __init__(self, r: APIRouter) -> None:
        super().__init__()
        self.app.include_router(r)
        # self.cfg = Config(self.usage, prog=self.prog)

    @classmethod
    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(
        cls, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        cls.logger.error(f"Bad Request for {request.url}: {exc}")
        return JSONResponse(
            status_code=400,
            content=DtoValidationErrors.from_request_validation_error(exc).dict(),
        )

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> FastAPI:
        return self.app

    def run(self) -> None:
        self.logger.info("Starting server.")
        super().run()

    def shutdown(self) -> None:
        loop = asyncio.get_event_loop()
        self.logger.info(f"CLOSING LOOP: {loop}")
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
