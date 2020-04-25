import time
import argparse
import registry
import threading
import paho.mqtt.publish as publish

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MQTT device simulator.")
    parser.add_argument("--registry-host",
                        default="localhost",
                        help="Device registry hostname.")
    parser.add_argument("--registry-port",
                        default=33001, type=int,
                        help="Device registry port.")
    parser.add_argument("--mqtt-host",
                        default="localhost",
                        help="MQTT adapter hostname.")
    parser.add_argument("--mqtt-port",
                        default=32001, type=int,
                        help="MQTT adapter port.")
    parser.add_argument("-t", "--tenant",
                        default="MY_TENANT",
                        help="Tenant name of the device.")
    parser.add_argument("-d", "--device",
                        help="Device identifier",
                        required=True)
    parser.add_argument("-p", "--passwd",
                        help="Device password",
                        required=True)
    parser.add_argument("--event-freq",
                        default=10, type=int,
                        help="How often should it send event data. 0 means publishing without any wait. ")
    parser.add_argument("--telemetry-freq",
                        default=5, type=int,
                        help="How often should it send telemetry data. 0 means publishing without any wait.")
    parser.add_argument("--threads",
                        default=1, type=int,
                        help="How many threads should be spawned for each message type.")

    # Create device in case it doesn't exist
    args = parser.parse_args()
    factory = registry.mk_api_factory(args.registry_host, args.registry_port)

    print("Creating device %s@%s..." % (args.device, args.tenant))
    factory(registry.mk_tenant)(args.tenant)
    factory(registry.mk_device)(args.tenant, args.device)
    factory(registry.set_passwd)(args.tenant, args.device, args.device, args.passwd)

    def send_message(ty, sleep):
        auth = {
            "username": "%s@%s" % (args.device, args.tenant),
            "password": args.passwd
        }
        counter = 0
        while True:
            counter += 1
            payload = "[%d] %s %d" % (threading.get_ident(), ty, counter)
            time.sleep(sleep)
            publish.single(
                ty, payload=payload,
                hostname=args.mqtt_host, port=args.mqtt_port,
                qos=1, auth=auth)
            print("Published '%s'" % payload)

    print("Starting publishing threads...")
    for _ in range(args.threads):
        threading.Thread(target=send_message, daemon=True, args=("telemetry", args.telemetry_freq)).start()
        threading.Thread(target=send_message, daemon=True, args=("event", args.event_freq)).start()

    while True:
        time.sleep(1)
