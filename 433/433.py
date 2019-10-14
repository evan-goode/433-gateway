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
    def start(self, ):
        self.rfdevice.enable_tx()
    def send(self, code):
        self.rfdevice.tx_code(code,
                              None,
                              self.config["pulse-length"],
                              self.config["length"])
    def stop(self):
        self.rfdevice.cleanup()
        
def main():
    with open(CONFIG_PATH, "r") as config_file:
        config = toml.load(config_file)

    transmitter = Transmitter(config["rf"])
    transmitter.start()

    client = mqtt.Client()
    client.connect(config["mqtt"]["broker"]["address"], config["mqtt"]["broker"]["port"])

    def on_message(client, data, message):
        if message.topic == config["mqtt"]["topic"]:
            print(f"received code: {message.payload}, transmitting...")
            transmitter.send(int(message.payload))
    client.on_message = on_message

    client.subscribe(config["mqtt"]["topic"], config["mqtt"]["qos"])
    print(f"subscribed to topic: {config['mqtt']['topic']}")
    client.loop_forever()
    transmitter.stop()

if __name__ == "__main__":
    main()
