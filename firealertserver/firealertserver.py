from __future__ import annotations

import asyncio
import csv
import logging
from argparse import ArgumentParser
from asyncio import DatagramProtocol, transports
from collections.abc import Coroutine
from datetime import datetime
from pathlib import Path
from typing import List, Callable, Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from firealertserver.pushnotification import PushNotification, FileTokenStorage

app = FastAPI()
log = logging.getLogger('filealertserver')
push_notification = PushNotification(token_storage=FileTokenStorage(
    Path('.') / 'data' / 'user-token.json'
))


async def log_received_data_to_stderr(data: bytes) -> None:
    log.debug('Received data = ' + data.decode('utf-8'))


def store_received_data_in_csv(path: Path) -> Callable[[bytes], Coroutine[Any, Any, None]]:
    async def _store_received_data_in_csv(data: bytes) -> None:
        csv_file_exists = path.exists() and path.stat().st_size > 0

        with open(path, 'a' if csv_file_exists else 'w') as f:
            writer = csv.DictWriter(f, ['ts', 'data'])
            if not csv_file_exists:
                writer.writeheader()
            writer.writerow({'ts': datetime.utcnow().isoformat(), 'data': data.decode('utf-8')})

    return _store_received_data_in_csv


def create_send_push_notification_func(push_notification: PushNotification):
    async def _send_push_notification(payload: bytes):
        def _should_fire_alert_from_client_payload():
            if payload:
                payload_str = payload.decode('utf-8').strip()
                if payload_str == '1':
                    return True
            return False

        if _should_fire_alert_from_client_payload():
            log.info('Push notification requested. Proceeding')
            push_notification.push({'action': 'fire-alert'})
        else:
            log.debug(f'Push notification requested and filtered. Payload: {payload.decode("utf-8")}')

    return _send_push_notification


class HandleUdp(DatagramProtocol):
    def __init__(self, listeners: List[Callable[[bytes], None]]):
        self._listeners = listeners

    def connection_made(self, transport: transports.DatagramTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        for listener in self._listeners:
            asyncio.create_task(listener(data))


async def start_incoming_alerts_server(listeners: List[Callable[[bytes], None]]) -> None:
    args = create_args_from_argparse()
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: HandleUdp(listeners), local_addr=(args.udp_bind_address, args.udp_bind_port))
    log.info('Incoming alerts server started at %s:%d' % (args.udp_bind_address, args.udp_bind_port))

    try:
        await asyncio.sleep(3600 * 24 * 365 * 100)
    finally:
        transport.close()


def create_args_from_argparse():
    parser = ArgumentParser()
    parser.add_argument('--udp-bind-address', required=True)
    parser.add_argument('--udp-bind-port', required=True, type=int)
    parser.add_argument('--http-bind-address', required=True)
    parser.add_argument('--http-bind-port', required=True, type=int)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


class UserToken(BaseModel):
    userToken: str


@app.post("/user-token")
async def userToken(userToken: UserToken):
    push_notification.update_user_token(userToken.userToken)
    return {"errorCode": "OK"}


@app.on_event('startup')
async def startup():
    global push_notification
    asyncio.create_task(start_incoming_alerts_server([
        log_received_data_to_stderr,
        store_received_data_in_csv(Path('.') / 'data' / 'raw.csv'),
        create_send_push_notification_func(push_notification)]))


def main():
    args = create_args_from_argparse()
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level,
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    uvicorn.run("firealertserver.firealertserver:app", host=args.http_bind_address,
                port=args.http_bind_port, log_level="info")


if __name__ == '__main__':
    main()
