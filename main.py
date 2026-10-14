from fastapi import FastAPI

from controllers import auth_controller, user_controller
from db import init_db

app = FastAPI()

init_db()

app.include_router(auth_controller.router)
app.include_router(user_controller.router)


@app.get("/")
def root():
    return {"message": "Api funcionando"}
