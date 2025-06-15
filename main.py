"""
Main application module for the FastAPI web application.
This module sets up the FastAPI application, configures CORS middleware,
and includes all the necessary routers for the API endpoints.
"""

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.features.auth import auth_controller
from src.features.contacts import contacts_controller
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle rate limit exceeded exceptions.
    
    Args:
        request (Request): The incoming request
        exc (RateLimitExceeded): The rate limit exception
        
    Returns:
        JSONResponse: A 429 status code response with an error message
    """
    return JSONResponse(
        status_code=429,
        content={"error": "rate limit exceeded. Try again later"},
    )


app.include_router(contacts_controller.router, prefix="/api")
app.include_router(auth_controller.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
