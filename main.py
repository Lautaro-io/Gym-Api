from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controllers import (
    auth_controller,
    user_controller,
    sport_profile_controller,
    routine_controller,
    payment_controller,
    exercise_controller,
    routine_exercise_controller,
)
from db import init_db

app = FastAPI()

init_db()

app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(sport_profile_controller.router)
app.include_router(routine_controller.router)
app.include_router(payment_controller.router)
app.include_router(exercise_controller.router)
app.include_router(routine_exercise_controller.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Api funcionando"}
