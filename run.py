import logging
from core.yueri import Yueri
from config import token


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=20,  # 50 - critical, 40 - error, 30 - warning, 20 - info, 10 - debug
        style='{',
        format='{asctime} | {levelname:8} | {name} | {message}'
    )
    logger = logging.getLogger(__name__)

    logging.info('Starting up')
    client = Yueri()
    client.run(token)
