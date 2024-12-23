import logging
from rich.logging import RichHandler
from rich.console import Console

def init_logger():
    console = Console()
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
    )
    log = logging.getLogger("rich")
    return log, console 