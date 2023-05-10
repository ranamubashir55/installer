import logging, os, re, inspect
from functools import lru_cache
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from pydantic import (  # BaseSettings automatically reads from environment variables for config settings
    AnyUrl, BaseSettings)

log = logging.getLogger("uvicorn")


# environment-specific configuration variables
class Settings(BaseSettings):  # environment: str = "dev" is equivalent to environment: str = os.getenv("ENVIRONMENT", "dev")
    environment: str = "dev"  # e.g. dev, stage, prod
    testing: bool = bool(0)  # whether or not we're in test mode
    database_url: AnyUrl = None


@lru_cache()  # use lru_cache to cache the settings so get_settings is only called once
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()


def create_dirs():
    folders = ['/logs', '/uploads']
    for dir in folders:
        isExist = os.path.exists(os.getcwd() + dir)
        if not isExist:
            os.makedirs(os.getcwd() + dir)


def log_config():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "[%(filename)s:%(lineno)d]:%(asctime)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "level": "INFO",
                "filename": "logs/omniroom.log",
                "mode": "a",
                "encoding": "utf-8",
                "maxBytes": 500000,
                "backupCount": 4
            }
        },
        "loggers": {
            "omniroom-logger": {"handlers": ["console", "file"], "level": "INFO"},
        },
    }
    return logging_config


def custom_openapi(app):
    """Code only for Testing, Searches all endpoint functions which has
    jwt dependency in it's body (including function definition line)
    Then it adds Authorization header to all those endpoints, so we don't have to
    use postman, and we can use Authorize Button just like we were using for
    oauth2_scheme = OAuth2PasswordBearer"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OMNI ROOM- CUSTOM SWAGGER UI",
        version="1.0",
        description="An API with an Authorize Button, ENJOY IT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }
    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]
    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]
        for method in methods:
            # access_token
            if (
                    re.search("Depends\\(authenticate\\)", inspect.getsource(endpoint)) or
                    re.search("jwt_required", inspect.getsource(endpoint)) or
                    re.search("jwt_refresh_token_required", inspect.getsource(endpoint)) or
                    re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema
