from fastapi import Depends, FastAPI
from fastapi.security.api_key import APIKey
from .internal import admin
from .routers import getconfig, getdevice
from .auth import auth

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

@app.get("/secure")
async def info(api_key: APIKey = Depends(auth.get_api_key)):
    return {
        "default variable": api_key
    }
