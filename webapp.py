# Copyright © 2021 TerminalWarlord
# Encoding = 'utf-8'
# Licensed under MIT License
# https://github.com/TerminalWarlord/

from fastapi import FastAPI
from main import *
import uvicorn
from flask import *
import requests

app = FastAPI()


@app.get("/animepahe.mp4")
async def root():
    full_url = request.full_path
    link = full_url.split('/animepahe.mp4?url=')[1]
    headers = {'Content-Type': 'video/mp4'}
    custom_response = Response("", status=302, headers=headers)
    custom_response.headers['Location'] = link
    return custom_response


if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
