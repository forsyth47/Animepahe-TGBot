from flask import Flask

from threading import Thread

app = Flask('')


@app.route('/')
def home():
  fline = ""
  with open ('log.txt','r') as f:
    for line in f.readlines():
      fline += line + "<br>"
  return fline


def run():

  app.run(host='0.0.0.0', port=8080)


def keep_alive():

  t = Thread(target=run)

  t.start()