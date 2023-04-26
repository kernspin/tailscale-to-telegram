import hmac
import hashlib
import logging
import os
import re
import requests
import time

SIGNATURE_PATTERN = re.compile(r't=(\d+),v1=(\w+)')
TAILSCALE_KEY = os.environ.get('TAILSCALE_KEY')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY')


def webhook(event, _):
    # extract event and signature 
    event_body = event['body']
    match = SIGNATURE_PATTERN.match(event['headers']['tailscale-webhook-signature'])
    timestamp = match.group(1)
    signature = match.group(2)

    # check authentication: validate HMAC, timestamp should not be older than 5 minutes
    if generateHmac(TAILSCALE_KEY, timestamp, event_body) != signature or time.time() - int(timestamp) > 300:
        logging.warn('Authentication error')
        return {
            'statusCode': 401,
            'body': 'Authentication error'
    }

    # TODO: build Telegram message

    # send to Telegram webhook
    send_message(event_body, TELEGRAM_API_KEY, TELEGRAM_CHAT_ID)

    # send resposne

    body = "hello"
    response = {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {"Content-Type": "text/json; charset=utf-8"},
        "body": body
        }

    return response

def generateHmac(key, timestamp, body):
    message = bytes(f'{timestamp}.{body}', 'utf-8')
    hmac_key = bytes(key, 'utf-8')
    digest = hmac.new(hmac_key, message, hashlib.sha256).hexdigest()
    return digest


def send_message(message, api_key, chat_id):
    url = f"https://api.telegram.org/bot{api_key}/sendMessage"
    params = {
       "chat_id": chat_id,
       "text": message,
    }
    resp = requests.get(url, params=params)

    # Throw an exception if Telegram API fails
    resp.raise_for_status()
    