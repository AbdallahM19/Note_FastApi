"""__init__.py"""

from fastapi import FastAPI, Request
from api.app import router
from api.routers.user_api import router as user_router
from api.routers.note_api import router as note_router
from api.database import create_database, create_tables, drop_db

app = FastAPI()

app.include_router(router)
app.include_router(user_router, prefix='/api')
app.include_router(note_router, prefix='/api')


@app.on_event("startup")
async def before_first_request():
    """This function is called when the application is Starting down"""
    print("Starting app")
    create_database()
    create_tables()
    print("Application startup complete")

@app.on_event("shutdown")
async def before_close_app():
    """This function is called when the application is shutting down"""
    print("Closing app")
    # drop_db()
    print("Application shutdown complete")
