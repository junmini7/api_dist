from fastapi import FastAPI
import time

import asyncio

app = FastAPI()
@app.get("/a")
async def a():
    print('a')
    asyncio.sleep(1)
    return 'a'
@app.get("/b")
async def b():
    print('b')
    time.sleep(10)
    asyncio.sleep(10)
    return 'b'
