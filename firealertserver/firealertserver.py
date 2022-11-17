from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Coroutine, Any

from firealertserver.pushnotification import PushNotification

log = logging.getLogger('filealertserver.handleincomingalerts')


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
