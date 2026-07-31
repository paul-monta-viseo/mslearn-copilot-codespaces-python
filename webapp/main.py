from os.path import abspath, dirname, join

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from webapp.app.routers import token, users

current_dir = dirname(abspath(__file__))
static_path = join(current_dir, "static")

app = FastAPI()
app.mount("/ui", StaticFiles(directory=static_path), name="ui")

app.include_router(token.router)
app.include_router(users.router)


@app.get("/")
def root():
    html_path = join(static_path, "index.html")
    return FileResponse(html_path)