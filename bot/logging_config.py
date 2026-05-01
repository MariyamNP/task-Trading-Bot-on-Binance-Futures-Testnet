import logging
import logging.handlers
import os


def setup_logging(log_file='trading_bot.log', level=logging.DEBUG):
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger('trading_bot')
    root_logger.setLevel(level)

    if root_logger.handlers:
        return

    fmt = logging.Formatter(
        fmt='%(asctime)s [%(levelname)-8s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding='utf-8'
    )
    fh.setLevel(level)
    fh.setFormatter(fmt)
    root_logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)
    root_logger.addHandler(ch)

    root_logger.info('Logging initialised. File: %s', os.path.abspath(log_file))
