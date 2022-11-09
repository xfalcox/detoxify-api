from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route

from pydantic import BaseModel, Field, ValidationError, typing
from pydantic.typing import Literal

from detoxify import Detoxify

AVAILABLE_MODELS = Literal['original', 'unbiased', 'multilingual']

models = {i: Detoxify(i) for i in typing.get_args(AVAILABLE_MODELS)}


class Parameters(BaseModel):
    model: AVAILABLE_MODELS
    content: str = Field(..., max_length=85000)


async def formatResponse(classification):
    return dict(map(lambda x: (x[0], int(x[1]*100)), classification.items()))


async def classify(request):
    params = await request.json()

    try:
        parsed_params = Parameters(**params)
    except ValidationError as e:
        return JSONResponse({"error": str(e)}, status_code=422)

    results = models[parsed_params.model].predict(params['content'])

    return JSONResponse(await formatResponse(results))

routes = [
    Route('/api/v1/classify', methods=['POST'], endpoint=classify)
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['POST'])
]

app = Starlette(routes=routes, middleware=middleware)
