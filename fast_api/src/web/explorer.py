from fastapi import APIRouter

router = APIRouter(prefix="/explorer")


@router.get("/")
def read_root():
    return {"main endpoint of the explorer"}
