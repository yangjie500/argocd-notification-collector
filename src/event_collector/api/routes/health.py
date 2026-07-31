from fastapi import APIRouter, Response, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
async def readiness(response: Response) -> dict[str, str]:
    ready = True

    # Add inexpensive dependency checks here when required.
    # For example, verify that a database pool has been initialized.
    #
    # Avoid calling every downstream service on every readiness request.

    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready"}

    return {"status": "ready"}
