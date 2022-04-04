import logging

LOGGER_NAME = 'features'


def configure_logger(level: str = 'info', output_format: str = 'json'):
    """
    Configures the package logger.
    """
    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(logging.INFO)
    if isinstance(level, str):
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    format_str = (
        '{'
        + '"level": "%(levelname)s",'
        + '"filename": "%(filename)s",'
        + '"time": "%(asctime)s",'
        + '"function": "%(funcName)s",'
        + '"line": %(lineno)d,'
        + '"message": "%(message)s"'
        + '}'
    )
    if output_format == 'text':
        format_str = '%(levelname)s | %(asctime)s | %(filename)s.%(funcName)s:%(lineno)d | %(message)s'

    formatter = logging.Formatter(format_str)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
