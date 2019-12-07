#!/usr/bin/env python3

import json

import paho.mqtt.client as mqtt
from rpi_rf import RFDevice
import toml

CONFIG_PATH = "/etc/433-gateway.toml"


class Transmitter:
    def __init__(self, config):
        self.config = config
        self.rfdevice = RFDevice(config["gpio"])
        self.rfdevice.tx_repeat = config["repeat"]

    def start(self,):
        self.rfdevice.enable_tx()

    def send(self, code, pulse_length):
        self.rfdevice.tx_code(
            code, None, pulse_length, self.config["length"]
        )

    def stop(self):
        self.rfdevice.cleanup()


def main():
    with open(CONFIG_PATH, "r") as config_file:
        config = toml.load(config_file)

    transmitter = Transmitter(config["rf"])
    transmitter.start()

    def on_connect(client, userdata, flags, rc):
        client.subscribe(config["mqtt"]["topic"], config["mqtt"]["qos"])
        print(f"subscribed to topic: {config['mqtt']['topic']}")

    def on_message(client, userdata, message):
        if message.topic == config["mqtt"]["topic"]:
            parsed = json.loads(message.payload)
            codes = []
            if "codes" in parsed and parsed["codes"]:
                codes = parsed["codes"]
            elif "code" in parsed and parsed["code"]:
                codes.append(parsed["code"])
            pulse_length = ("pulse-length" in parsed and parsed["pulse-length"]) or config["rf"]["pulse-length"]
            for code in codes:
                print(f"received code: {code} with pulse length {pulse_length}, transmitting...")
                transmitter.send(code, pulse_length)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    username = "username" in config["mqtt"] and config["mqtt"]["username"]
    password = "password" in config["mqtt"] and config["mqtt"]["password"]
    if username or password:
        client.username_pw_set(username, password)
    client.connect(
        config["mqtt"]["broker"]["address"], config["mqtt"]["broker"]["port"]
    )

    client.loop_forever()
    transmitter.stop()


if __name__ == "__main__":
    main()
