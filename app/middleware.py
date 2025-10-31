import time, uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog
log = structlog.get_logger()
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        rid = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        with structlog.threadlocal.tmp_bind(log, request_id=rid, path=request.url.path, method=request.method):
            try:
                response: Response = await call_next(request)
                return response
            finally:
                dur = time.perf_counter() - start
                log.info("request_done", request_id=rid, duration_s=dur)
