#!/bin/bash

until $(curl --output /dev/null --silent --head --fail http://172.24.2.3:9200); do
    printf '.'
    sleep 5
done

curl -X POST http://172.24.2.3:9200/zones/_doc -H 'Content-Type: application/json' -d '{"mappings": {"_doc": {"properties" : {"hostname" : {"type" : "text"},"TTL" : {"type" : "text"},"IP" : {"type" : "text"},"index" : {"type" : "integer"}}}}}'

curl -X POST http://172.24.2.3:9200/zones/_doc/1 -H 'Content-Type: application/json' -d '{"hostname":"www.google.com","TTL":"5","IP":"10.0.5.2","index":0}'

curl -X POST http://172.24.2.3:9200/zones/_doc/2 -H 'Content-Type: application/json' -d '{"hostname":"www.youtube.com","TTL":"10","IP":"10.0.5.8, 192.168.20.58","index":0}'

curl -X POST http://172.24.2.3:9200/zones/_doc/3 -H 'Content-Type: application/json' -d '{"hostname":"www.github.com","TTL":"15","IP":"201.204.122.10","index":0}'