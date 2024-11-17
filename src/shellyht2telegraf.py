#!/usr/bin/env python

import paho.mqtt.client as mqtt
import json
import sys
from argparse import ArgumentParser


def get_path(path, data):
    result = data
    for key in path.split("."):
        result = result.get(key)
        if result is None:
            break
    return result


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Adapter to import Shelly H&T data from MQTT into InfluxDB"
    )
    parser.add_argument(
        "--mqtt-host",
        help="The hostname or IP address of the MQTT broker",
        required=True,
    )
    parser.add_argument(
        "--mqtt-port", help="The port number of the MQTT broker", type=int, default=1883
    )
    args = parser.parse_args()

    def on_connect(client, userdata, flags, reason_code):
        client.subscribe("shellyplusht/+/events/rpc")

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            data = {
                "humidity": get_path("params.humidity:0.rh", payload),
                "temperature": get_path("params.temperature:0.tC", payload),
                "battery_percent": get_path(
                    "params.devicepower:0.battery.percent", payload
                ),
                "battery_voltage": get_path("params.devicepower:0.battery.V", payload),
            }
            if not any(value is None for value in data.values()):
                room = msg.topic.split("/")[1]
                values = ",".join(f"{name}={value}" for (name, value) in data.items())
                print(
                    f"thermometer,room={room} {values}"
                )  # TODO: Could we also extract the timestamp of the message?
                sys.stdout.flush()
        except Exception as e:
            print(f"Could not get data from message: {e}", file=sys.stderr)

    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(args.mqtt_host, args.mqtt_port, 60)

    mqttc.loop_forever()
