from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.init_data import bootstrap_application
from app.routers.api import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_application()
    yield


class ReflectCORSMiddleware:
    """反射任意 Origin 的原生 ASGI CORS 中间件，在外层优先拦截 OPTIONS。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin", b"").decode()
        method = scope.get("method", "")

        if method == "OPTIONS" and origin:
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"access-control-allow-origin", origin.encode()],
                    [b"access-control-allow-methods", b"DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"],
                    [b"access-control-allow-headers", b"*"],
                    [b"access-control-allow-credentials", b"true"],
                    [b"access-control-max-age", b"600"],
                    [b"content-type", b"text/plain; charset=utf-8"],
                    [b"content-length", b"2"],
                ],
            })
            await send({"type": "http.response.body", "body": b"OK"})
            return

        async def modified_send(message):
            if message["type"] == "http.response.start" and origin:
                headers_list = list(message.get("headers", []))
                has_origin = any(h[0] == b"access-control-allow-origin" for h in headers_list)
                if not has_origin:
                    headers_list.append([b"access-control-allow-origin", origin.encode()])
                    headers_list.append([b"access-control-allow-credentials", b"true"])
                    message["headers"] = headers_list
            await send(message)

        await self.app(scope, receive, modified_send)


def create_application() -> FastAPI:
    docs_enabled = settings.debug
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    # 原生 ASGI 反射 CORS 在最外层，优先拦截所有 OPTIONS 预检
    # 注意：Starlette add_middleware 头部插入，先添加的在列表末尾 = 外层
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(ReflectCORSMiddleware)
    register_exception_handlers(application)
    application.mount(
        "/media/covers",
        StaticFiles(directory=settings.upload_dir / "covers", check_dir=False),
        name="book-covers",
    )
    application.include_router(api_router)
    return application


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
