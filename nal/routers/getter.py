from fastapi import FastAPI, APIRouter, Path
from ..git import git

# define router
router = APIRouter(
    prefix="/get",
    tags=["getter"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{repo}/{filePath:path}", tags=["getconfig"])
async def get_file(repo: str, filePath: str, update: bool=True):
    return git.get_file(repo, filePath, update)