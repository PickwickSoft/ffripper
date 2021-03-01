import logging
from rich.logging import RichHandler

FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("rich")