#!/usr/bin/env python
import RPi.GPIO as GPIO
import dht11.dht11 as dht11
import time
import datetime
import MySQLdb
import json

with open('/etc/tempestas.json') as json_data_file:
    data = json.load(json_data_file)

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 14
instance = dht11.DHT11(pin=17)

# Open database connection

db = MySQLdb.connect(data['mysql']['host'], data['mysql']['user'], data['mysql']['password'], data['mysql']['database'])

# prepare a cursor object using cursor() method
cursor = db.cursor()

# create table `condition` (id int not null auto_increment, location int , `recorded_on` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,temperature float, humidity float, PRIMARY KEY(id));

while True:
    result = instance.read()
    if result.is_valid():
        temp = result.temperature
        humidity = result.humidity

        # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO `condition` (`temperature`, `humidity`) VALUES (%d, %d)" % (temp, humidity)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()

        # print("Last valid input: " + str(datetime.datetime.now()))
        # print("Temperature: %d C" % result.temperature)
        # print("Humidity: %d %%" % result.humidity)
    
    time.sleep(int(data['frequency']))

# disconnect from server
db.close()
