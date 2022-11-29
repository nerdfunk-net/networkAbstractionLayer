from fastapi import Depends, FastAPI
from fastapi.security.api_key import APIKey
from .internal import admin
from .routers import getconfig, getdevice, onboarding, getter, hldm
from .auth import auth


description = """

The Network Abstraction Layer (nal) is the layer between our mini python apps
and nautobot respectively our mini aps and other sources of truth

"""

# start app with
#
# uvicorn nal.main:app --port 8000 --host 127.0.0.1 (--reload)
#
# in the upper directory
app = FastAPI(
    title="Network Abstraction Layer",
    description=description,
    version="0.0.1",)

app.include_router(getconfig.router)
app.include_router(hldm.router)
app.include_router(getdevice.router)
app.include_router(onboarding.router)
app.include_router(getter.router)

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
