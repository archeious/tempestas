#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
from datetime import datetime
from dateutil.tz import tzlocal
import json
from Adafruit_BME280 import *
from elasticsearch import Elasticsearch 

with open('/etc/tempestas.json') as json_data_file:
    config = json.load(json_data_file) 

es = Elasticsearch([{'host': config["elasticsearch"]["host"], 'port': config["elasticsearch"]["port"]}]) 

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

while True:
    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print 'Temp      = {0:0.3f} deg C'.format(degrees)
    print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
    print 'Humidity  = {0:0.2f} %'.format(humidity)

    e1={
        "@timestamp"  : datetime.now(tzlocal()).isoformat(),
        "sensor"      : config['name'],
        "sensor-type" : "BME_280",
        "device-type" : "rPi",
        "temperature" : degrees,
        "pressure"    : hectopascals,
        "humidity"    : humidity,
        "version"     : "0.0.3",
    }

    print e1 
    res = es.index(index=config["elasticsearch"]["index"],body=e1)    

    time.sleep(int(config['frequency']))

