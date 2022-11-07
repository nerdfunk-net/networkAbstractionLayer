from fastapi import Depends, FastAPI
from .internal import admin
from .routers import getconfig, getdevice


# start app with
#
# uvicorn nal.main:app --reload --port 8000
#
# in the upper directory

app = FastAPI()

app.include_router(getconfig.router)
app.include_router(getdevice.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/")
async def root():
    return {'message':'Please read the docs'}

