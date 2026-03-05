from __future__ import annotations

import os
import loguru
from loguru import logger

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools import Metrics

metrics = Metrics(namespace="hush_api")

lambda_logger = Logger(log_uncaught_exceptions=True)

PASSPHRASE_NAME: str = os.getenv("PASSPHRASE_NAME", "NOP")

SALT_NAME = os.getenv("SALT_NAME", "NOP")

AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "NOP")

lambda_logger.remove_keys(["location", "function_arn"])


def loguru_sink(message: loguru.Message) -> None:
    record = message.record
    keys_list = ["message", "exception", "function", "line", "name"]
    log_message = {k: v for k, v in record.items() if k in keys_list and v is not None}

    level = record["level"].name
    match level:
        case "DEBUG":
            lambda_logger.debug(log_message, extra=record["extra"])
        case "INFO":
            lambda_logger.info(log_message, extra=record["extra"])
        case "WARNING":
            lambda_logger.warning(log_message, extra=record["extra"])
        case "ERROR":
            lambda_logger.error(log_message, extra=record["extra"])
        case "CRITICAL":
            lambda_logger.critical(log_message, extra=record["extra"])
        case _:
            lambda_logger.exception(log_message, extra=record["extra"])


logger.remove()
logger.add(loguru_sink, format="{message}", colorize=False, serialize=True)
