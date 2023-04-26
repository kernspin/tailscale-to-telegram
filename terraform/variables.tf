variable "aws_region" {
  default = "eu-central-1"
}

variable "tailscale_hmac_key" {
  description = "Secret key provided by Tailscale. It is used validate the signature of the request."
  type        = string
  sensitive   = true
}

variable "telegram_api_key" {
  description = "Access key for the Telegram webhook"
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Chat ID of the Telegram user"
  type        = string
  sensitive   = true
}
