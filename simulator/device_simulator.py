"""
Smart Campus IoT device simulator.

This script creates four virtual devices and publishes JSON telemetry to MQTT.
The wireless behavior is simulated as IEEE 802.15.4 / Zigbee-like communication:
small packets, low power, possible packet loss, random delay, RSSI, and battery drain.
"""

import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt


CONFIG_PATH = Path(__file__).with_name("config.json")
TOPIC_PART_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def sanitize_topic_part(value):
    """Allow only safe MQTT topic characters used by the project policy."""
    value = str(value).strip().replace(" ", "_")
    if not TOPIC_PART_PATTERN.match(value):
        raise ValueError(f"Unsafe topic value: {value}")
    return value


def build_topic(base_topic, building, room, device_id):
    return (
        f"{sanitize_topic_part(base_topic)}/"
        f"{sanitize_topic_part(building)}/"
        f"{sanitize_topic_part(room)}/"
        f"{sanitize_topic_part(device_id)}/telemetry"
    )


class VirtualDevice:
    def __init__(self, device_config, simulation_config):
        self.device_id = device_config["deviceId"]
        self.building = device_config["building"]
        self.room = device_config["room"]
        self.battery_level = float(device_config.get("initial_battery_level", 100))
        self.simulation_config = simulation_config
        self.total_energy_mwh = 0.0

    def generate_sensor_values(self):
        """Generate understandable ranges with occasional abnormal values."""
        if self.device_id == "server_room_401":
            temperature = random.uniform(21, 39)
            occupancy = random.choice([0, 0, 0, 1])
            light_level = random.uniform(20, 75)
            air_quality = random.uniform(40, 135)
        elif self.device_id == "lab_201":
            temperature = random.uniform(22, 36.5)
            occupancy = random.randint(0, 12)
            light_level = random.uniform(35, 95)
            air_quality = random.uniform(55, 150)
        else:
            temperature = random.uniform(20, 34)
            occupancy = random.randint(0, 35)
            light_level = random.uniform(10, 100)
            air_quality = random.uniform(35, 125)

        return {
            "temperature": round(temperature, 2),
            "humidity": round(random.uniform(35, 86), 2),
            "occupancy": occupancy,
            "light_level": round(light_level, 2),
            "air_quality": round(air_quality, 2),
        }

    def apply_zigbee_like_model(self):
        """Return network metrics and update energy/battery values."""
        delay_ms = random.randint(
            self.simulation_config["random_delay_ms_min"],
            self.simulation_config["random_delay_ms_max"],
        )
        time.sleep(delay_ms / 1000)

        link_quality = random.randint(55, 100)
        rssi = random.randint(-88, -42)

        energy = float(self.simulation_config["energy_per_message_mwh"])
        self.total_energy_mwh += energy
        self.battery_level = max(
            0.0,
            self.battery_level - float(self.simulation_config["battery_drain_per_message"]),
        )

        return {
            "random_delay_ms": delay_ms,
            "link_quality": link_quality,
            "rssi": rssi,
            "estimated_energy_consumption_mwh": round(self.total_energy_mwh, 4),
        }

    def create_payload(self):
        sensor_values = self.generate_sensor_values()
        wireless_values = self.apply_zigbee_like_model()

        status = "LOW_BATTERY" if self.battery_level < 20 else "OK"
        payload = {
            "deviceId": self.device_id,
            "building": self.building,
            "room": self.room,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": sensor_values["temperature"],
            "humidity": sensor_values["humidity"],
            "occupancy": sensor_values["occupancy"],
            "light_level": sensor_values["light_level"],
            "air_quality": sensor_values["air_quality"],
            "battery_level": round(self.battery_level, 2),
            "status": status,
            "wireless": {
                "model": "IEEE 802.15.4 / Zigbee-like",
                "packet_loss_rate": self.simulation_config["packet_loss_rate"],
                **wireless_values,
            },
        }
        return payload


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[MQTT] Connected to broker")
    else:
        print(f"[MQTT] Connection failed with code: {reason_code}")


def main():
    config = load_config()
    mqtt_config = config["mqtt"]
    simulation_config = config["simulation"]

    client_id = f"{mqtt_config['client_id_prefix']}-{random.randint(1000, 9999)}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect

    if mqtt_config.get("username"):
        client.username_pw_set(mqtt_config["username"], mqtt_config.get("password", ""))

    client.connect(mqtt_config["broker"], int(mqtt_config["port"]), int(mqtt_config["keepalive"]))
    client.loop_start()

    devices = [VirtualDevice(device, simulation_config) for device in config["devices"]]
    print("[SIM] Smart Campus simulator started. Press Ctrl+C to stop.")

    try:
        while True:
            for device in devices:
                if random.random() < simulation_config["packet_loss_rate"]:
                    print(f"[ZIGBEE] Simulated packet loss for {device.device_id}")
                    continue

                payload = device.create_payload()
                topic = build_topic(
                    mqtt_config["base_topic"],
                    device.building,
                    device.room,
                    device.device_id,
                )

                client.publish(topic, json.dumps(payload), qos=0)
                print(
                    f"[PUBLISH] {topic} | temp={payload['temperature']}C "
                    f"humidity={payload['humidity']}% battery={payload['battery_level']}%"
                )

            time.sleep(int(simulation_config["publish_interval_seconds"]))

    except KeyboardInterrupt:
        print("\n[SIM] Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
