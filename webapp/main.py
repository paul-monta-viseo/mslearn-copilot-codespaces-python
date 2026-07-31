from os.path import abspath, dirname, join

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from webapp.app.middleware import InProcessRateLimiter, RateLimitMiddleware
from webapp.app.routers import token, users

current_dir = dirname(abspath(__file__))
static_path = join(current_dir, "static")

app = FastAPI(
    title="Token API",
    description="Generate tokens and manage users.",
)
app.state.rate_limiter = InProcessRateLimiter()
app.add_middleware(RateLimitMiddleware)
app.mount("/ui", StaticFiles(directory=static_path), name="ui")

app.include_router(token.router)
app.include_router(users.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return a consistent, human-readable response for known API errors."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Explain invalid request data without exposing an internal traceback."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Return a safe generic response for unexpected server failures."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


@app.get("/", response_class=FileResponse)
async def root() -> FileResponse:
    """Serve the web application's landing page."""
    html_path = join(static_path, "index.html")
    return FileResponse(html_path)
