"""Health checks.

/health       liveness: the process is up. Used by Docker and the load balancer.
/health/ready readiness: MongoDB and Redis are reachable too.
"""

from fastapi import APIRouter, Request, Response, status

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness(request: Request, response: Response) -> dict[str, object]:
    conns = request.app.state.connections
    checks: dict[str, str] = {}

    try:
        await conns.mongo.admin.command("ping")
        checks["mongo"] = "ok"
    except Exception:
        checks["mongo"] = "down"

    try:
        await conns.redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "down"

    healthy = all(v == "ok" for v in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if healthy else "degraded", "checks": checks}
