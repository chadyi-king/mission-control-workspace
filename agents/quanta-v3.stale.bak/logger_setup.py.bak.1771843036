import logging


def build_logger(log_file: str) -> logging.Logger:
    try:
        logger = logging.getLogger("quanta-v3")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger
    except Exception:
        raise
