from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controllers import auth_controller, user_controller
from db import init_db

app = FastAPI()

init_db()

app.include_router(auth_controller.router)
app.include_router(user_controller.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mientras prueban en local, permití todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Api funcionando"}
