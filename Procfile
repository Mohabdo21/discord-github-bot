worker: python main.py
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker bot.bot:app
