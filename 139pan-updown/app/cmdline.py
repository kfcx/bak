import os
import sys
import logging
from app import server
from app.config import STATIC_ROOT, IP, PORT


def setup_logging():
    formatter = logging.Formatter('%(asctime)s %(message)s', '%H:%M:%S')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    server.logger.setLevel(logging.INFO)
    server.logger.addHandler(handler)


def create_and_change_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    os.chdir(dir_name)


def main():
    from aiohttp.web import run_app

    setup_logging()

    overwrite_duplicates = False
    create_and_change_dir(STATIC_ROOT)
    app = server.make_app(overwrite_duplicates=overwrite_duplicates)

    run_app(app, host=IP, port=PORT)
