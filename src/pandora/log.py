import logging 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - (%(filename)s - %(lineno)d) - %(message)s",
)

logger = logging.getLogger(name="pandora")

if __name__ == "__main__":
    logger.info("log module initialized")