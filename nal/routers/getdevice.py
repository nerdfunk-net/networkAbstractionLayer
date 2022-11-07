from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, Request
from ..nautobot.main import getDevices

router = APIRouter(
    prefix="/getdevice",
    tags=["getdevice"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_device(request: Request):
    """
    returns device<p>
    Args:
        <br><b>request:</b> the 'nautobot' filter<p>
        <br><b>examples</b>:
        <br>http://127.0.0.1:8000/getdevice/?name=hostname&model=router<p>
        <br>name=devicename
        <br>role=rolename
        <br>model=device type slug
    <p>Returns:
        the device as json
    """
    request_args = dict(request.query_params)
    if request_args:
        result = {}
        result['filter'] = request_args
        result['count'] = 0  # default if no match
        data = getDevices(request_args)
        if data:
            result['count'] = len(data)
            result['result'] = data
            return result

    return {}
