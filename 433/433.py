#!/usr/bin/env python3

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

    def send(self, code):
        self.rfdevice.tx_code(
            code, None, self.config["pulse-length"], self.config["length"]
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
            print(f"received code: {message.payload}, transmitting...")
            transmitter.send(int(message.payload))

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
