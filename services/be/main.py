from http import server
from logging.config import dictConfig
from fastapi import FastAPI
import uvicorn
from api import ping, user, authentication, questionare, services
from config import create_dirs, log_config, custom_openapi
from db import models
from fastapi import HTTPException
from db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from utils.exceptions import exception_handler


def create_application() -> FastAPI:
    application = FastAPI()
    origins = ["*"]
    application.add_middleware(  # Allow cross origin
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(AuthJWTException, exception_handler)
    application.add_exception_handler(Exception, exception_handler)
    application.include_router(ping.router)
    application.include_router(user.router, prefix="/user", tags=["users"])
    application.include_router(authentication.router, prefix="/user", tags=["users"])
    application.include_router(
        questionare.router, prefix="/question", tags=["questions"]
    )
    application.include_router(services.router, prefix="/services", tags=["services"])
    return application


app = create_application()
app.openapi_schema = custom_openapi(app)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    create_dirs()
    dictConfig(log_config())
    models.Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="debug", reload=True)
