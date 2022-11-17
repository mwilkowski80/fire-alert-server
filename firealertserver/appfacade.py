import asyncio
from pathlib import Path

from firealertserver.firealertserver import log_received_data_to_stderr, \
    store_received_data_in_csv, create_send_push_notification_func, send_fire_alert_push_notification
from firealertserver.udpserver import start_udp_server
from firealertserver.parseinputargs import create_args_from_argparse
from firealertserver.pushnotification import PushNotification, FileTokenStorage
from firealertserver.user_token import UserToken

push_notification = PushNotification(token_storage=FileTokenStorage(
    Path('.') / 'data' / 'user-token.json'
))


def app_test_push_notification():
    send_fire_alert_push_notification(push_notification)


def app_on_user_token(user_token: UserToken):
    push_notification.update_user_token(user_token.userToken)


def app_on_startup():
    args = create_args_from_argparse()

    asyncio.create_task(start_udp_server((args.udp_bind_address, args.udp_bind_port), [
        log_received_data_to_stderr,
        store_received_data_in_csv(Path('.') / 'data' / 'raw.csv'),
        create_send_push_notification_func(push_notification)]))
