# tailscale-to-telegram

Receive Tailscale events and forward the notification to a Telegram chat. Provides a webhook URL on AWS that can be configured as a receiver.

## Terraform

Configures resources on AWS:
- Python Lambda that receives the events, transforms it and sends it as a message to Telegram
- Lambda URL that serves as the webhook for Tailscale
- Cloudwatch log group for debugging

The setup contains three secret variables:

- `tailscale_hmac_key`: Secret key provided by Tailscale. It is used validate the signature of the request.
- `telegram_api_key`: Access key for the Telegram webhook
- `telegram_chat_id`: Chat ID of the Telegram user

You can provide the values interactively or by providing a `.tfvars` file.

## Python

Applying terraform will automatically install the required libs in the `./lambda` folder and build the lambda package.

## Tailscale

Find out more about Tailscale webhooks and how to configure them: https://tailscale.com/kb/1213/webhooks/

## Telegram

Setup a new bot and start a private chat with it. Find out your personal Chat ID to setup the message forwarding.
