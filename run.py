import yaml
from core.yueri import Yueri


if __name__ == '__main__':
    with open('config.yaml') as file:
        config = yaml.load(file)
    client = Yueri(config)
    client.run(config['Client']['token'])
