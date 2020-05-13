import time
import argparse
import registry
import threading
import requests
from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MQTT device simulator.")
    parser.add_argument("--registry-host",
                        default="localhost",
                        help="Device registry hostname.")
    parser.add_argument("--registry-port",
                        default=33001, type=int,
                        help="Device registry port.")
    parser.add_argument("--http-host",
                        default="localhost",
                        help="HTTP adapter hostname.")
    parser.add_argument("--http-port",
                        default=32000, type=int,
                        help="HTPP adapter port.")
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

    # Get data from arguments.
    args = parser.parse_args()
    factory = registry.mk_api_factory(args.registry_host, args.registry_port)
    auth = HTTPBasicAuth("%s@%s" % (args.device, args.tenant), args.passwd)
    host = "%s:%s" % (args.http_host, args.http_port)

    # Create device in case it doesn't exist
    print("Creating device %s@%s..." % (args.device, args.tenant))
    factory(registry.mk_tenant)(args.tenant)
    factory(registry.mk_device)(args.tenant, args.device)
    factory(registry.set_passwd)(args.tenant, args.device, args.device, args.passwd)

    def send(ty, sleep, auth=auth, host=host):
        addr = "http://%s/%s" % (host, ty)
        counter = 0
        while True:
            counter += 1
            payload = {ty: counter}
            try:
                time.sleep(sleep)
                requests.post(addr, data=payload, auth=auth)
                print("Published '%s'" % payload)
            except Exception as e:
                print(e)

    def recv(ttd=20, auth=auth, host=host):
        addr = "http://%s/event?hono-ttd=%d" % (host, ttd)
        data = {"temp": 5}
        while True:
            res = requests.post(addr, data=data, auth=auth, timeout=ttd*2)
            if res.status_code == 200:
                print("Command '%s'" % res.text)
            else:
                print(res)

    print("Starting publishing threads...")
    thread = lambda f, args=[]: threading.Thread(target=f, daemon=True, args=args).start()
    thread(recv, [])
    for _ in range(args.threads):
        thread(send, ["telemetry", args.telemetry_freq])
        thread(send, ["event", args.event_freq])

    while True:
        time.sleep(1)
