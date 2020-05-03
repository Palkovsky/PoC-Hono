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
                        default=1, type=int,
                        help="How often should it send event data. 0 means publishing without any wait. ")
    parser.add_argument("--telemetry-freq",
                        default=1, type=int,
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

    def send_message(args, auth, ty, sleep):
        host = "%s:%d" % (args.amqp_host, args.amqp_port)
        conn = BlockingConnection(host,
                            allowed_mechs="PLAIN",
                            user=auth["username"],
                            password=auth["password"])
        sender = conn.create_sender(address=None)
        counter = 0
        while True:
            counter += 1
            payload = "[%d] %s %d" % (threading.get_ident(), ty, counter)
            time.sleep(sleep)
            sender.send(Message(address=ty, body=payload))
            print("Published '%s'" % payload)


    def receiv_message(args, auth):
        host = "%s:%d" % (args.amqp_host, args.amqp_port)
        conn = BlockingConnection(host,
                            allowed_mechs="PLAIN",
                            user=auth["username"],
                            password=auth["password"])
        receiver = conn.create_receiver("command")
        while True:
            msg = receiver.receive(timeout=None)
            receiver.accept()
            payload = str(msg.payload)
            print(payload)

    auth = {
        "username": "%s@%s" % (args.device, args.tenant),
        "password": args.passwd
    }

    # Receive messages from application
    print("Subscribing to commands...")
    threading.Thread(target=receiv_message, daemon=True, args=(args, auth)).start()

    print("Starting publishing threads...")
    for _ in range(args.threads):
        threading.Thread(target=send_message, daemon=True, args=(args, auth, "telemetry", args.telemetry_freq)).start()
        threading.Thread(target=send_message, daemon=True, args=(args, auth, "event", args.event_freq)).start()
    

    while True:
        time.sleep(1)