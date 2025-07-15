from .controller import collect_dataset
from .config import config
from .logger import setup_logger

logger = setup_logger("collect_data")

if __name__ == "__main__":
    logger.info("Starting data collection")
    collect_dataset(config, logger)