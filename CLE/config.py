import os
import yaml


ANCHOR_STATE_IDLE = 0
ANCHOR_STATE_CONFIGURED = 1
ANCHOR_STATE_WORKING = 2
ANCHOR_STATE = (
    (ANCHOR_STATE_IDLE, "idle"),
    (ANCHOR_STATE_CONFIGURED, "configured"),
    (ANCHOR_STATE_WORKING, "working"),
)


class Config:
    config_file = os.environ.get('CLE_POLLER_CONFIG', "poller-config.yml")

    sqldb = {
        "POSTGRES_HOST": "",
        "POSTGRES_PORT": "",
        "POSTGRES_DB": "",
        "POSTGRES_USER": "",
        "POSTGRES_PASSWORD": "",
    }

    influxdb = {

    }

    rabbitmq = {

    }

    def __init__(self):
        self.load_from_yml()

    def load_from_yml(self):
        with open(self.config_file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                self.sqldb.update(data["sqldb"])
                self.influxdb.update(data["influxdb"])
                self.rabbitmq.update(data["rabbitmq"])
            except yaml.YAMLError as exc:
                print(exc)


config = Config()
