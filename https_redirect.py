import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

app = FastAPI()


@app.route('/{_:path}')
async def https_redirect(request: Request):
    return RedirectResponse(request.url.replace(port=8007,scheme='https'))
#RedirectResponse("https://woowakgood.live/twitch/streamer_watching_streamer")

if __name__ == '__main__':
    uvicorn.run('https_redirect:app', port=8010, host='0.0.0.0')