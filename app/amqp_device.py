from __future__ import print_function
from proton import Message
from proton.utils import BlockingConnection
from proton.handlers import IncomingMessageHandler
from proton.reactor import SenderOption, AtLeastOnce, AtMostOnce
import time
import argparse
import registry
import threading

import amqp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AMQP device simulator.")
    parser.add_argument("--registry-host",
                        default="localhost",
                        help="Device registry hostname.")
    parser.add_argument("--registry-port",
                        default=33001, type=int,
                        help="Device registry port.")
    parser.add_argument("--amqp-host",
                        default="localhost",
                        help="AMQP adapter hostname.")
    parser.add_argument("--amqp-port",
                        default=32002, type=int,
                        help="AMQP adapter port.")
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

    # Read some initial data from args.
    args = parser.parse_args()
    host = "%s:%d" % (args.amqp_host, args.amqp_port)
    auth = {
        "username": "%s@%s" % (args.device, args.tenant),
        "password": args.passwd
    }

    # Create device in case it doesn't exist
    factory = registry.mk_api_factory(args.registry_host, args.registry_port)
    print("Creating device %s@%s..." % (args.device, args.tenant))
    factory(registry.mk_tenant)(args.tenant)
    factory(registry.mk_device)(args.tenant, args.device)
    factory(registry.set_passwd)(args.tenant, args.device, args.device, args.passwd)

    def mk_conn(host=host, auth=auth):
        return BlockingConnection(
            host,
            allowed_mechs="PLAIN",
            user=auth["username"],
            password=auth["password"]
        )

    def send(ty, sleep, auth=auth, args=args, host=host):
        sender = mk_conn().create_sender(address=None)
        counter = 0
        while True:
            counter += 1
            payload = "[%d] %s %d" % (threading.get_ident(), ty, counter)
            time.sleep(sleep)
            try:
                sender.send(Message(address=ty, body=payload))
                print("Published '%s'" % payload)
            except Exception as e:
                print(e)

    def recv():
        receiver = mk_conn().create_receiver("command")
        while True:
            msg = receiver.receive(timeout=None)
            # No need to sleep. reveiver.accepts() is blocking.
            receiver.accept()
            payload = msg.body
            print(payload)

    print("Starting publishing threads...")
    thread = lambda f, args=[]: threading.Thread(target=f, daemon=True, args=args).start()
    thread(recv)
    for _ in range(args.threads):
        thread(send, ["telemetry", args.telemetry_freq])
        thread(send, ["event", args.event_freq])

    while(True):
        time.sleep(1)
