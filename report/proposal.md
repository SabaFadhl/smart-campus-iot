# Smart Campus IoT Simulation and Analytics Platform - Proposal

## Problem

Modern campuses contain classrooms, labs, offices, and technical rooms that need continuous monitoring for comfort, safety, and energy efficiency. In many academic environments, building a full hardware IoT prototype is costly and time-consuming. This project solves that problem by creating a simulation-only IoT platform that behaves like a real smart campus monitoring system without using physical sensors.

The platform focuses on temperature, humidity, occupancy, light level, air quality, battery level, and device health. It uses MQTT publish/subscribe messaging to show how IoT devices send telemetry to a processing layer and dashboard.

## Scenario

The scenario is a university campus with four monitored rooms:

| Device ID | Building | Room | Purpose |
|---|---|---|---|
| classroom_101 | main_building | classroom_101 | Teaching environment monitoring |
| lab_201 | engineering_building | lab_201 | Lab comfort and air quality monitoring |
| office_301 | admin_building | office_301 | Office energy and occupancy monitoring |
| server_room_401 | it_building | server_room_401 | High-temperature risk monitoring |

Each virtual device publishes telemetry every 5 seconds to an MQTT topic. A subscriber validates the payload, calculates useful values, and prints alerts.

## Selected Tools

- **Python:** Used to simulate virtual IoT devices and process telemetry.
- **Paho MQTT:** Python MQTT client library.
- **HiveMQ Public Broker:** Public MQTT broker used for quick testing without local broker setup.
- **Node-RED Dashboard:** Visual dashboard for latest sensor values, alerts, and temperature chart.
- **Markdown:** Used for project documentation, proposal, report, and presentation outline.

## Selected Wireless Type

The selected wireless model is **IEEE 802.15.4 / Zigbee-like**. This is suitable because smart campus sensors usually send small packets at regular intervals and should consume low energy. Zigbee-like communication is appropriate for short-range indoor sensor networks, especially when battery-powered nodes are used.

The simulator includes:

- Packet loss rate
- Random network delay
- RSSI
- Link quality
- Estimated energy consumption
- Battery drain

## Architecture

The system architecture has four layers:

1. **Virtual Device Layer:** Python devices generate simulated sensor readings.
2. **Communication Layer:** MQTT topics transfer telemetry from devices to subscribers.
3. **Processing Layer:** Python subscriber validates data, calculates derived values, and detects alerts.
4. **Presentation Layer:** Node-RED Dashboard displays live values and trends.

## MQTT Topic Design

The topic hierarchy is:

```text
campus/{building}/{room}/{deviceId}/telemetry
```

Example:

```text
campus/main_building/classroom_101/classroom_101/telemetry
```

This design is readable, structured, and allows subscribers to use wildcards:

```text
campus/+/+/+/telemetry
```

## Expected Output

The final project will include a runnable simulator, a subscriber analytics processor, a Node-RED dashboard flow, test cases, a final report, and a presentation outline.
