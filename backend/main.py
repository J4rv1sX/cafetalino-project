from fastapi import FastAPI

from app.routers import routing

app = FastAPI(title="Cafetalino API")
app.include_router(routing.router)
