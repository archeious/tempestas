#!/usr/bin/env python
import time
from datetime import datetime, date, time, timezone
import json
from elasticsearch import Elasticsearch 
import pprint
import requests
import xml.etree.ElementTree as ET


config_path = "./tempestas.json"

with open(config_path) as json_data_file:
    config = json.load(json_data_file) 

es = Elasticsearch([{'host': config["elasticsearch"]["host"], 'port': config["elasticsearch"]["port"]}]) 
pp = pprint.PrettyPrinter(indent=4)


while True:    
    session = requests.Session()

    now = datetime.now()
    current_date = now.strftime("%y%m%d")

    print("date string = ", current_date)
    data_url = '10.0.0.157/cgi-bin/datalog.xml?sdate=' + current_date + '&days=2'

    s = session.get('http://10.0.0.157/cgi-bin/datalog.xml?sdate=210330&days=2')

    root = ET.fromstring(s.text)
    print(root.tag)


    for record in root.iter('record'):
        record_date = record.find('date').text
        for probe in record.iter('probe'):
            e1={
                "@timestamp" : datetime.strptime(record_date, '%m/%d/%Y %H:%M:%S').isoformat(),
                "device"     : config['name'],
                "location"   : config['location'],
                "version"     : "0.0.1",
            }
            probe_name  = probe.find('name').text
            probe_type  = probe.find('type').text
            probe_value = probe.find('value').text

            if (probe_type == "Temp"):
                probe_type = "TempF"

            if (probe_type =="pwr"):
                probe_type = "Watts"

            print(record_date,probe_name, probe_type,probe_value)
            e1["type"] = probe_type
            e1["name"] = probe_name
            e1["value"]= probe_value,
            pp.pprint(e1)
            res = es.index(index=config["elasticsearch"]["index"],body=e1)    
            pp.pprint(res)      

    time.sleep(int(config['frequency']))

