#!/bin/bash

usage() {
cat << EOF
Usage: ${0##*/} [-h SERVER=localhost] [-p PORT] [-t TENANT]

Connect to MQTT dispatch router and start accepting messages from specified tenant.
        -h SERVER    Service hostname
        -p PORT      Service port
        -t TENANT    Tenant name
        -c           Command mode
        -d DEVICE_ID Device id for command execution
EOF
}

HOST=localhost
PORT=33000
TENANT=MY_TENANT
USERNAME=consumer@HONO
PASSWD=verysecret
PROFILE=receiver
DEVICE_ID=0

while getopts "h:p:t:u:d:c" opt; do
    case "$opt" in
        h) HOST=${OPTARG}       ;;
        p) PORT=${OPTARG}       ;;
        t) TENANT=${OPTARG}     ;;
        d) DEVICE_ID=${OPTARG}  ;;
        c) PROFILE=command      ;;
        *) usage && exit 1      ;;
    esac
done

([ "$TENANT" = "" ] || [ "$PORT" = "" ]) && usage && exit 1;
([ "$PROFILE" = command ] && [ "$DEVICE_ID" = "" ]) && echo "Missing device id" && exit 2;

echo "Connecting to $HOST:$PORT as $USERNAME in $PROFILE mode..."

java -jar ${BASH_SOURCE%/*}/hono-cli.jar \
     --hono.client.host=$HOST \
     --hono.client.port=$PORT \
     --hono.client.username=$USERNAME \
     --hono.client.password=$PASSWD \
     --tenant.id=$TENANT \
     --device.id=$DEVICE_ID \
     --spring.profiles.active=$PROFILE
