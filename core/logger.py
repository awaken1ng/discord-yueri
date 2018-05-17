import os
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, config: dict):
        formatter = logging.Formatter(fmt='{asctime} | {levelname:.1} | {name} | {message}', style='{')

        # Setup logging to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Setup logging to file
        logs_location = config['location']
        if not os.path.exists(logs_location):
            os.mkdir(logs_location)
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(logs_location, config['name']),
            when=config['interval']['type'],
            interval=config['interval']['value']
        )
        file_handler.setFormatter(formatter)

        self.handlers = (console_handler, file_handler)
        self.level = config['level']

    def get_logger(self, name: str):
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        for handler in self.handlers:
            logger.addHandler(handler)
        return logger
