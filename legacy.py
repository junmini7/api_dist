import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse,PlainTextResponse
from datetime import datetime as dt
app = FastAPI()

@app.middleware("http")
async def logging(request: Request, call_next):
    whattolog = f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} {str(request.client.host)} {request.method} {request.url.path} {request.path_params} {request.query_params}\n'
    with open('redirect_log.txt', 'a') as f:
        f.write(whattolog)
    response = await call_next(request)
    return response



@app.route('/{_:path}')
async def https_redirect(request: Request):

    return RedirectResponse('https://woowakgood.live/twitch/populariswatching?query=')

if __name__ == '__main__':
    uvicorn.run('legacy:app', port=8010, host='0.0.0.0')