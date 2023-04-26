locals {
  lambda_root                  = "../lambda/"
  lambda_description           = "Converts incoming events from Tailscale to Telegram webhook messages"
  lambda_runtime               = "python3.10"
  lambda_handler               = "handler.webhook"
  lambda_timeout               = 10
  lambda_concurrent_executions = 1
  lambda_cw_log_group_name     = "/aws/lambda/${aws_lambda_function.webhook_lambda.function_name}"
  lambda_log_retention_in_days = 7
}

resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${local.lambda_root}/requirements.txt -t ${local.lambda_root}/"
  }

  triggers = {
    dependencies_versions = filemd5("${local.lambda_root}/requirements.txt")
    source_versions       = filemd5("${local.lambda_root}/handler.py")
  }
}

resource "random_uuid" "lambda_src_hash" {
  keepers = {
    for filename in setunion(
      fileset(local.lambda_root, "handler.py"),
      fileset(local.lambda_root, "requirements.txt")
    ) :
    filename => filemd5("${local.lambda_root}/${filename}")
  }
}

data "archive_file" "tailscale_to_telegram_zip" {
  depends_on = [null_resource.install_dependencies]
  excludes = [
    "__pycache__",
    ".venv",
  ]
  source_dir  = local.lambda_root
  output_path = "${random_uuid.lambda_src_hash.result}.zip"
  type        = "zip"
}

data "aws_iam_policy_document" "webhook_lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "webhook_lambda" {
  name               = local.resource_name
  assume_role_policy = data.aws_iam_policy_document.webhook_lambda_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_lambda_function" "webhook_lambda" {
  function_name    = local.resource_name
  source_code_hash = data.archive_file.tailscale_to_telegram_zip.output_base64sha256
  filename         = data.archive_file.tailscale_to_telegram_zip.output_path
  description      = local.lambda_description
  role             = aws_iam_role.webhook_lambda.arn
  handler          = local.lambda_handler
  runtime          = local.lambda_runtime
  timeout          = local.lambda_timeout
  reserved_concurrent_executions = local.lambda_concurrent_executions
  environment {
    variables = {
      TAILSCALE_KEY    = "${var.tailscale_hmac_key}"
      TELEGRAM_API_KEY = "${var.telegram_api_key}"
      TELEGRAM_CHAT_ID = "${var.telegram_chat_id}"
    }
  }
}

resource "aws_lambda_function_url" "webhook_lambda_url" {
  function_name      = aws_lambda_function.webhook_lambda.function_name
  authorization_type = "NONE"
}

resource "aws_cloudwatch_log_group" "webhook_lambda" {
  name              = local.lambda_cw_log_group_name
  retention_in_days = local.lambda_log_retention_in_days
}
