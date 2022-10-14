from starlette.applications import Starlette
from starlette.responses import JSONResponse

from detoxify import Detoxify

model_original = Detoxify('original')
model_unbiased = Detoxify('unbiased')
model_multilingual = Detoxify('multilingual')

async def formatResponse(classification):
    return dict(map(lambda x: (x[0], int(x[1]*100)), classification.items()))


app = Starlette()

@app.route('/api/v1/classify', methods=['POST'])
async def classify(request):
    params = await request.json()
    match params['model']:
        case 'original':
            results = model_original.predict(params['content'])
        case 'unbiased':
            results = model_unbiased.predict(params['content'])
        case 'multilingual':
            results = model_multilingual.predict(params['content'])

    return JSONResponse(await formatResponse(results))
