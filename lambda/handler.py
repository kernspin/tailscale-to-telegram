import hmac
import hashlib
import logging
import os
import re
import requests
import time

SIGNATURE_PATTERN = re.compile(r't=(\d+),v1=(\w+)')
TAILSCALE_KEY = os.environ.get('TAILSCALE_KEY', 'tskey-webhook-kitiAp4CNTRL-kYxQk3rYbx2a24fvfyTEx2HoQZLNL6jj9')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY')

# event = {'version': '2.0', 'routeKey': '$default', 'rawPath': '/', 'rawQueryString': '', 'headers': {'content-length': '137', 'x-amzn-tls-cipher-suite': 'ECDHE-RSA-AES128-GCM-SHA256', 'x-amzn-tls-version': 'TLSv1.2', 'x-amzn-trace-id': 'Root=1-64440559-78a75dd3296de1357a528f11', 'x-forwarded-proto': 'https', 'host': '7v64tbb24tywqe466by2nqit7a0scvui.lambda-url.eu-central-1.on.aws', 'x-forwarded-port': '443', 'content-type': 'application/json', 'x-forwarded-for': '2a05:d014:972:5a00:433:fd30:9c39:e163', 'tailscale-webhook-signature': 't=1682179417,v1=025e690ee53356ac2efb65b4e44620ee306f9f3009178e0bf93b7e67d285c82a', 'accept-encoding': 'gzip', 'user-agent': 'Go-http-client/1.1'}, 'requestContext': {'accountId': 'anonymous', 'apiId': '7v64tbb24tywqe466by2nqit7a0scvui', 'domainName': '7v64tbb24tywqe466by2nqit7a0scvui.lambda-url.eu-central-1.on.aws', 'domainPrefix': '7v64tbb24tywqe466by2nqit7a0scvui', 'http': {'method': 'POST', 'path': '/', 'protocol': 'HTTP/1.1', 'sourceIp': '2a05:d014:972:5a00:433:fd30:9c39:e163', 'userAgent': 'Go-http-client/1.1'}, 'requestId': 'f4f09b16-77e2-48be-a8e1-269dc2f94439', 'routeKey': '$default', 'stage': '$default', 'time': '22/Apr/2023:16:03:37 +0000', 'timeEpoch': 1682179417501}, 'body': '[{"timestamp":"2023-04-22T16:03:37.061963715Z","version":1,"type":"test","tailnet":"mfaltin@gmail.com","message":"This is a test event"}]', 'isBase64Encoded': False}


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

    # build Telegram message
    

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











