import sys

from loguru import logger


logger.add(sys.stdout, format="{message}", colorize=True, serialize=True)
