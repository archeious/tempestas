#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import datetime
import MySQLdb
import json

from Adafruit_BME280 import *





with open('/etc/tempestas.json') as json_data_file:
    data = json.load(json_data_file)


sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

# Open database connection
db = MySQLdb.connect(data['mysql']['host'], data['mysql']['user'], data['mysql']['password'], data['mysql']['database'])

# prepare a cursor object using cursor() method
cursor = db.cursor()

# create table `condition` (id int not null auto_increment, location int , `recorded_on` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,temperature float, humidity float, PRIMARY KEY(id));

while True:
    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print 'Temp      = {0:0.3f} deg C'.format(degrees)
    print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
    print 'Humidity  = {0:0.2f} %'.format(humidity)

    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO `condition` (`temperature`, `humidity`, `pressure`) VALUES (%0.3f, %0.2f, %0.2f)" % (degrees, humidity, pascals)
    print sql
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    
    time.sleep(int(data['frequency']))

# disconnect from server
db.close()
