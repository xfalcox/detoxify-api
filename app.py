from starlette.applications import Starlette
from starlette.responses import JSONResponse

from detoxify import Detoxify

model = Detoxify('unbiased')

def formatResponse(classification):
    return dict(map(lambda x: (x[0], int(x[1]*100)), classification.items()))


app = Starlette()

@app.route('/api/v1/classify', methods=['POST'])
async def classify(request):
    content = await request.json()
    results = model.predict(content['content'])
    return JSONResponse(formatResponse(results))
