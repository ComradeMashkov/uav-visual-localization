from .config import config
from .record_video import record_video
from .logger import setup_logger

logger = setup_logger("collect_data")

if __name__ == "__main__":
    logger.info("Starting data collection")
    record_video(config, 'winter', logger)
