from __future__ import annotations

import asyncio
import csv
import logging
from argparse import ArgumentParser
from asyncio import DatagramProtocol, transports
from datetime import datetime
from pathlib import Path
from typing import List, Callable, Any

log = logging.getLogger('filealertserver')


async def log_received_data_to_stderr(data: bytes) -> None:
    log.debug('Received data = ' + data.decode('utf-8'))


def store_received_data_in_csv(path: Path) -> Callable[[bytes], None]:
    async def _store_received_data_in_csv(data: bytes) -> None:
        csv_file_exists = path.exists() and path.stat().st_size > 0

        with open(path, 'a' if csv_file_exists else 'w') as f:
            writer = csv.DictWriter(f, ['ts', 'data'])
            if not csv_file_exists:
                writer.writeheader()
            writer.writerow({'ts': datetime.utcnow().isoformat(), 'data': data.decode('utf-8')})

    return _store_received_data_in_csv


async def send_push_notification(data: bytes):
    log.debug('Push notification')


class HandleUdp(DatagramProtocol):
    def __init__(self, listeners: List[Callable[[bytes], None]]):
        self._listeners = listeners

    def connection_made(self, transport: transports.DatagramTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        for listener in self._listeners:
            asyncio.create_task(listener(data))


async def start_server(listeners: List[Callable[[bytes], None]]) -> None:
    args = create_args_from_argparse()
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: HandleUdp(listeners), local_addr=(args.bind_address, args.bind_port))

    try:
        await asyncio.sleep(3600 * 24 * 365 * 100)
    finally:
        transport.close()


def create_args_from_argparse():
    parser = ArgumentParser()
    parser.add_argument('--bind-address', required=True)
    parser.add_argument('--bind-port', required=True, type=int)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


def main():
    args = create_args_from_argparse()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    asyncio.run(start_server([
        log_received_data_to_stderr,
        store_received_data_in_csv(Path('.') / 'data' / 'raw.csv'),
        send_push_notification]))


if __name__ == '__main__':
    main()
