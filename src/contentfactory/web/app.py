"""The dashboard app.

Run it with:  uvicorn --factory contentfactory.web.app:create_app --port 8000
(or `factory web` once the CLI wires it up). Without DASHBOARD_TOKEN it only
answers requests from localhost.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..pipeline import Factory
from . import api, pages
from .auth import AuthMiddleware
from .deps import STATIC_DIR, templates
from .jobs import JobRunner

log = logging.getLogger(__name__)

ERROR_STATUS: list[tuple[type[BaseException], int]] = [
    (PermissionError, 403),
    (KeyError, 404),
    (ValueError, 400),
]


def _message(exc: BaseException) -> str:
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc) or type(exc).__name__


def _handler(status: int):
    async def handle(request: Request, exc: Exception):
        msg = _message(exc)
        if request.url.path.startswith("/api/"):
            return JSONResponse({"error": msg, "type": type(exc).__name__}, status_code=status)
        if request.method == "POST":
            return pages.back(request, "/", err=msg)
        return templates.TemplateResponse(request, "error.html", {"status": status, "message": msg},
                                          status_code=status)
    return handle


async def _unexpected(request: Request, exc: Exception):
    """Publishing / LLM / render failures that aren't one of the mapped types."""
    log.exception("Unhandled error on %s", request.url.path)
    msg = f"{type(exc).__name__}: {exc}"
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": msg, "type": type(exc).__name__}, status_code=500)
    if request.method == "POST":
        return pages.back(request, "/", err=msg[:400])
    return templates.TemplateResponse(request, "error.html", {"status": 500, "message": msg}, status_code=500)


async def _validation(request: Request, exc: RequestValidationError):
    details = "; ".join(f"{'.'.join(str(x) for x in e.get('loc', []))}: {e.get('msg')}" for e in exc.errors())
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": f"Invalid request: {details}", "details": exc.errors()}, status_code=422)
    if request.method == "POST":
        return pages.back(request, "/", err=f"Invalid form: {details}")
    return templates.TemplateResponse(request, "error.html", {"status": 422, "message": details}, status_code=422)


def _include_business(app: FastAPI) -> None:
    """Mount the business module's routers when it is installed."""
    try:
        from ..business.routes import public_router, router  # type: ignore[attr-defined]
    except ImportError as e:
        log.info("Business routes not available: %s", e)
        app.state.business_enabled = False
        return
    app.include_router(router)
    app.include_router(public_router)
    app.state.public_paths += [r.path_regex for r in public_router.routes if hasattr(r, "path_regex")]
    app.state.business_enabled = True


def _include_funnel(app: FastAPI) -> None:
    """Mount the funnel (link page, signups, webhooks) when installed."""
    try:
        from ..funnel.routes import public_router, router
    except ImportError:
        app.state.funnel_enabled = False
        return
    app.include_router(router)
    app.include_router(public_router)
    app.state.public_paths += [r.path_regex for r in public_router.routes if hasattr(r, "path_regex")]
    app.state.funnel_enabled = True


def _include_community(app: FastAPI) -> None:
    """Mount the comment inbox (drafts replies; a human sends each one)."""
    try:
        from ..community.routes import router
    except ImportError:
        return
    app.include_router(router)


def create_app(factory: Factory | None = None) -> FastAPI:
    """Build the dashboard around a Factory (default: Factory.create() from env)."""
    factory = factory or Factory.create()
    jobs = JobRunner()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        jobs.shutdown()

    app = FastAPI(title="Content Factory", lifespan=lifespan, docs_url="/api/docs",
                  openapi_url="/api/openapi.json", redoc_url=None)
    app.state.factory = factory
    app.state.jobs = jobs
    app.state.public_paths = []

    app.add_middleware(AuthMiddleware)
    for exc_type, status in ERROR_STATUS:
        app.add_exception_handler(exc_type, _handler(status))
    app.add_exception_handler(RequestValidationError, _validation)
    app.add_exception_handler(Exception, _unexpected)

    app.include_router(api.router)
    from . import fastreview
    app.include_router(fastreview.router)  # before pages: /review/fast must win over /review/{...}
    app.include_router(pages.router)
    _include_business(app)
    _include_funnel(app)
    _include_community(app)

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    factory.settings.output_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=factory.settings.output_dir), name="media")
    return app
