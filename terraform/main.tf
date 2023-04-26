provider "aws" {
  region = var.aws_region
}

locals {
  resource_name = "tailscale2telegram"
}