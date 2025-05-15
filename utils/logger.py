import logging

def setup_logger():
    logger = logging.getLogger("GoQuantSimulator")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logger()
