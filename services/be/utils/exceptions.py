from starlette.responses import JSONResponse
from fastapi import status, Request


def exception_handler(request: Request, exc):
    """Global AuthJWTException Handler for FastAPI app"""
    if not hasattr(exc, "status_code"):
        exc_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        exc_status_code = exc.status_code
    if not hasattr(exc, "message"):
        exc_detail = "Unknown Exception Occurred"
    else:
        exc_detail = exc.message
    return JSONResponse(status_code=exc_status_code, content={"detail": exc_detail})
