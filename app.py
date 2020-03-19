import connexion
from connexion import NoContent
import requests
import pykafka
from pykafka import KafkaClient
import datetime
import json
from ast import literal_eval
import yaml
from flask_cors import CORS, cross_origin
import logging
import logging.config

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
try:
    with open('/config/app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())
except:
    with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

HEADERS = {"content-type":"application/json"}

def getOffset(offset):
    kafka = app_config['datastore']['server'] + ':' + app_config['datastore']['port']
    client = KafkaClient(hosts=kafka)
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True)
    counter = 0
    for message in consumer:
        if message is not None:
            data = message.value.decode('utf-8')
            msg = json.loads(data)
            if(msg["type"] == "xrayInfo"):
                if(counter == offset):
                    print(msg["type"], msg["payload"])
                    logger.info(msg["type"], msg["payload"])
                    return msg["payload"], 201
                else:
                    counter += 1

    return NoContent, 201

def getLast():
    kafka = app_config['datastore']['server'] + ':' + app_config['datastore']['port']
    client = KafkaClient(hosts=kafka)
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_group = "1")
    lastOffset = topic.fetch_offset_limits(-1)[0][0][0]

    for message in consumer:
        if message is not None:
            data = message.value.decode('utf-8')
            msg = json.loads(data)
            if(msg["type"] == "surgeryInfo"):
                logger.info(msg["type"], msg["payload"])
                return msg["payload"], 201

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8110)