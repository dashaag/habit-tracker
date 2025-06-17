from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.controllers import user, auth, habit, tracking_log, analytics # Added analytics
from app.core.seeder import init_roles # Import the seeder function
import asyncio # Though FastAPI handles async event handlers directly

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    """Event handler for application startup."""
    # This will run our role seeder
    await init_roles()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/v1", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(habit.router, prefix="/habits", tags=["habits"])
app.include_router(tracking_log.router, prefix="/tracking-log", tags=["tracking-log"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"]) # Added analytics router


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")
