import os
import yaml


try:
    with open(os.getenv('CONFIG_PATH', '../config/config.yaml')) as fin:
        config = yaml.safe_load(fin)
except:
    pass
