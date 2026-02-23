import logging


def build_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("quanta-v3")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    # File handler — primary output destination.
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stream handler only when NOT redirecting to a file (i.e. interactive terminal).
    # When started with  >> logs/quanta.log 2>&1  both stdout and stderr land in
    # the same file, so a stream handler would duplicate every line.
    import sys, os
    if sys.stderr.isatty() or os.getenv("QUANTA_ALSO_LOG_STDERR", ""):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
