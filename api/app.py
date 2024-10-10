from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/home")
async def home():
    return {"message": "Welcome in Home"}
