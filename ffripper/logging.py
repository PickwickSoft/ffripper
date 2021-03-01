import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(asctime)s:%(levelname)s:%(message)s",
    handlers=[RichHandler()]
    )

logger = logging.getLogger("rich")
logger.info("Hello, World!")