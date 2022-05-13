#!/bin/bash

switch=$1
host_name=$2
ip_name=$3

root_id=`/usr/bin/curl "http://192.168.10.11/Tractor/monitor?q=login&user=root"|jq -r .tsid`

echo "http://192.168.10.11/Tractor/ctrl?q=battribute&tsid=${root_id}&b=${host_name}/${ip_name}&nimby=${switch}"
curl "http://192.168.10.11/Tractor/ctrl?q=battribute&tsid=${root_id}&b=${host_name}/${ip_name}&nimby=${switch}"
echo "nimby Okay"

