from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route
from starlette_exporter import PrometheusMiddleware, handle_metrics

from pydantic import BaseModel, Field, ValidationError, typing
from pydantic.typing import Literal

import os

from detoxify import Detoxify

AVAILABLE_MODELS = Literal["original", "unbiased", "multilingual"]

models = {i: Detoxify(i) for i in typing.get_args(AVAILABLE_MODELS)}


class Parameters(BaseModel):
    model: AVAILABLE_MODELS
    content: str = Field(..., max_length=85000)


class APICheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.apis = set()
        if "API_KEYS" in os.environ:
            self.apis = set(os.getenv("API_KEYS").split("|"))

    async def dispatch(self, request, call_next):
        if request.method == "POST" and self.apis:
            if request.headers.get("X-API-KEY") not in self.apis:
                return JSONResponse({"error": "Invalid API key"}, status_code=401)

        response = await call_next(request)
        return response


async def formatResponse(classification):
    return dict(map(lambda x: (x[0], int(x[1] * 100)), classification.items()))


async def classify(request):
    params = await request.json()

    try:
        parsed_params = Parameters(**params)
    except ValidationError as e:
        return JSONResponse({"error": str(e)}, status_code=422)

    results = models[parsed_params.model].predict(params["content"])

    return JSONResponse(await formatResponse(results))


async def health(request):
    return JSONResponse({"status": "ok"})


routes = [
    Route("/api/v1/classify", methods=["POST"], endpoint=classify),
    Route("/health", methods=["GET"], endpoint=health),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"]),
    Middleware(APICheckMiddleware),
]

app = Starlette(routes=routes, middleware=middleware)
app.add_middleware(
    PrometheusMiddleware, skip_paths=["/health", "/metrics"], app_name="disorder"
)
app.add_route("/metrics", handle_metrics)
