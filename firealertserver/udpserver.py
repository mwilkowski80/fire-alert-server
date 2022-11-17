from __future__ import annotations

import asyncio
from asyncio import DatagramProtocol, transports
from typing import Tuple, List, Callable, Any

from firealertserver.firealertserver import log


async def start_udp_server(local_addr: Tuple[str, int], listeners: List[Callable[[bytes], None]]) -> None:
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: HandleUdp(listeners), local_addr=local_addr)
    log.info('Incoming alerts server started at %s:%d' % local_addr)

    try:
        await asyncio.sleep(3600 * 24 * 365 * 100)
    finally:
        transport.close()


class HandleUdp(DatagramProtocol):
    def __init__(self, listeners: List[Callable[[bytes], None]]):
        self._listeners = listeners

    def connection_made(self, transport: transports.DatagramTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        for listener in self._listeners:
            asyncio.create_task(listener(data))
