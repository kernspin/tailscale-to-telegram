output "webhook_url" {
  value       = aws_lambda_function_url.webhook_lambda_url.function_url
  description = "Public URL of the tailscale2telegram webhook"
}