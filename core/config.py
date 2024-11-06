import yaml

config = dict()

with open("config_dev.yml", "r") as f:
    config.update(yaml.load(f, Loader=yaml.FullLoader))
    ENV = config['env']
