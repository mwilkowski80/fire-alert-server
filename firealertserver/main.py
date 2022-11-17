from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI

from firealertserver.appfacade import app_on_user_token, app_on_startup, app_test_push_notification
from firealertserver.parseinputargs import create_args_from_argparse
from firealertserver.user_token import UserToken

app = FastAPI()
log = logging.getLogger('filealertserver.main')


@app.post("/user-token")
async def userToken(userToken: UserToken):
    app_on_user_token(userToken)
    return {"errorCode": "OK"}


@app.post('/test-push-notification')
async def test_push_notification():
    app_test_push_notification()
    return {"errorCode": "OK"}


@app.on_event('startup')
async def startup():
    app_on_startup()


def main():
    args = create_args_from_argparse()
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level,
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    uvicorn.run("firealertserver.main:app", host=args.http_bind_address,
                port=args.http_bind_port, log_level="info")


if __name__ == '__main__':
    main()
