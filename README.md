# Smart Campus IoT Simulation and Analytics Platform

This is a complete **Internet of Things** course project for **Master of IT** students. The project is simulation-only and does not require any physical hardware. Python is used to simulate virtual IoT devices that publish telemetry through MQTT to a Python subscriber and a Node-RED Dashboard.

## 1. Project Creation Commands on Windows PowerShell

If the project folders already exist, these commands are still safe because `-Force` will not delete existing files.

```powershell
New-Item -ItemType Directory -Force -Path smart-campus-iot
New-Item -ItemType Directory -Force -Path smart-campus-iot\simulator
New-Item -ItemType Directory -Force -Path smart-campus-iot\processing
New-Item -ItemType Directory -Force -Path smart-campus-iot\dashboard
New-Item -ItemType Directory -Force -Path smart-campus-iot\dashboard\screenshots
New-Item -ItemType Directory -Force -Path smart-campus-iot\tests
New-Item -ItemType Directory -Force -Path smart-campus-iot\report
```

## 2. Project Idea

The system simulates a smart campus with four monitored locations:

- `classroom_101`
- `lab_201`
- `office_301`
- `server_room_401`

Each virtual device publishes JSON telemetry every 5 seconds. The data is sent using MQTT publish/subscribe through the HiveMQ Public Broker. A Python subscriber receives the data, validates it, calculates derived values, and prints alerts. A Node-RED flow is also included to visualize live telemetry on a dashboard.

## 3. Required Tools

- Python 3.10 or newer
- pip
- Internet connection for the HiveMQ public MQTT broker
- Node.js and Node-RED for the dashboard
- Node-RED Dashboard package
- Mosquitto clients, optional, for manual testing with `mosquitto_pub`

## 4. Installation

Open PowerShell inside the project folder:

```powershell
cd smart-campus-iot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell script execution is blocked on your machine, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 5. Run the MQTT Subscriber

Open the first PowerShell window:

```powershell
cd smart-campus-iot
.\.venv\Scripts\Activate.ps1
python .\processing\subscriber.py
```

The subscriber listens to:

```text
campus/+/+/+/telemetry
```

It performs the following tasks:

- Validates incoming JSON payloads.
- Rejects missing or invalid fields.
- Calculates `comfort_index`.
- Calculates `occupancy_status`.
- Calculates `abnormal_temperature_flag`.
- Calculates `air_quality_status`.
- Prints clear alerts.

## 6. Run the Simulator

Open a second PowerShell window:

```powershell
cd smart-campus-iot
.\.venv\Scripts\Activate.ps1
python .\simulator\device_simulator.py
```

Each virtual device publishes one telemetry message every 5 seconds.

## 7. MQTT Topics

General topic format:

```text
campus/{building}/{room}/{deviceId}/telemetry
```

Examples:

```text
campus/main_building/classroom_101/classroom_101/telemetry
campus/engineering_building/lab_201/lab_201/telemetry
campus/admin_building/office_301/office_301/telemetry
campus/it_building/server_room_401/server_room_401/telemetry
```

## 8. JSON Telemetry Format

```json
{
  "deviceId": "classroom_101",
  "building": "main_building",
  "room": "classroom_101",
  "timestamp": "2026-06-24T12:00:00+00:00",
  "temperature": 25.4,
  "humidity": 55.2,
  "occupancy": 18,
  "light_level": 72.5,
  "air_quality": 65.7,
  "battery_level": 95.8,
  "status": "OK",
  "wireless": {
    "model": "IEEE 802.15.4 / Zigbee-like",
    "packet_loss_rate": 0.05,
    "random_delay_ms": 180,
    "link_quality": 92,
    "rssi": -61,
    "estimated_energy_consumption_mwh": 0.018
  }
}
```

## 9. Zigbee-like Wireless Simulation

The selected wireless communication model is **IEEE 802.15.4 / Zigbee-like** because it is suitable for indoor IoT sensor networks:

- Low power consumption.
- Suitable for small periodic messages.
- Good fit for smart rooms and smart buildings.
- Supports concepts such as RSSI and link quality.

The simulator includes:

- `packet_loss_rate`
- `random_delay_ms`
- `estimated_energy_consumption_mwh`
- Battery drain
- `rssi`
- `link_quality`

## 10. Alert Rules

| Rule | Condition |
|---|---|
| High temperature | `temperature > 35` |
| Empty room with lights on | `occupancy = 0` and `light_level > 60` |
| Poor air quality | `air_quality > 120` |
| Abnormal humidity | `humidity > 80` |
| Low battery | `battery_level < 20` |

## 11. Security Controls

The project includes simple security controls suitable for an academic IoT simulation:

- Input validation in `subscriber.py`.
- Rejection of messages with missing fields.
- Rejection of MQTT topics that do not match the topic naming policy.
- Sanitized logs to avoid printing unsafe values directly.
- MQTT username/password fields in `simulator/config.json`.
- Topic naming policy that allows only letters, numbers, underscores, and hyphens.

Note: HiveMQ Public Broker does not require username/password. If you use a private Mosquitto broker, you can configure username and password in `simulator/config.json`.

## 12. Run the Node-RED Dashboard

Install Node-RED:

```powershell
npm install -g --unsafe-perm node-red
```

Run Node-RED:

```powershell
node-red
```

Open:

```text
http://localhost:1880
```

Install Node-RED Dashboard nodes:

```text
Menu -> Manage palette -> Install -> node-red-dashboard
```

Import the flow:

```text
Menu -> Import -> Clipboard
```

Then paste the content of:

```text
dashboard/node_red_flow.json
```

After clicking Deploy, open the dashboard:

```text
http://localhost:1880/ui
```

## 13. Tests

The test plan is available in:

```text
tests/test_cases.md
```

It covers:

- Normal telemetry
- Missing field
- Abnormal temperature
- Broker disconnection

Manual test example using Mosquitto:

```powershell
mosquitto_pub -h broker.hivemq.com -t "campus/it_building/server_room_401/server_room_401/telemetry" -m '{\"deviceId\":\"server_room_401\",\"building\":\"it_building\",\"room\":\"server_room_401\",\"timestamp\":\"2026-06-24T12:00:00+00:00\",\"temperature\":38,\"humidity\":55,\"occupancy\":0,\"light_level\":30,\"air_quality\":70,\"battery_level\":90,\"status\":\"OK\"}'
```

## 14. Project Structure

```text
smart-campus-iot/
│
├── simulator/
│   ├── device_simulator.py
│   └── config.json
│
├── processing/
│   └── subscriber.py
│
├── dashboard/
│   ├── node_red_flow.json
│   └── screenshots/
│
├── tests/
│   └── test_cases.md
│
├── report/
│   ├── proposal.md
│   ├── final_report.md
│   └── presentation_outline.md
│
├── requirements.txt
└── README.md
```

## 15. Presentation Notes

- Start by explaining that the project is simulation-only.
- Run the subscriber first, then run the simulator.
- Open the Node-RED Dashboard to show live telemetry.
- Explain that the Zigbee-like model is simulated in Python, not implemented with physical wireless hardware.
- Explain why MQTT is suitable: lightweight, publish/subscribe, and clear topic hierarchy.
- Show the alert rules in `subscriber.py`.
