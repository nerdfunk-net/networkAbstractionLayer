import os
from fastapi import Depends, FastAPI
from fastapi.security.api_key import APIKey
from .internal import admin
from .routers import getconfig, getdevice, onboarding, getter, hldm, lldm
from .auth import auth
from dotenv import load_dotenv, dotenv_values


description = """

The Network Abstraction Layer (nal) is the layer between the mini python apps
and nautobot respectively the mini apps and other sources of truth

"""

# start app with
#
# uvicorn nal.main:app --port 8000 --host 127.0.0.1 (--reload)
#
# in the upper directory

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))
# Connect the path with the '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))
# you can get the env variable by using var = os.getenv('varname')

app = FastAPI(
    title="Network Abstraction Layer",
    description=description,
    version="0.0.1",)

app.include_router(getconfig.router)
app.include_router(hldm.router)
app.include_router(lldm.router)
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
