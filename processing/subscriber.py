"""
Smart Campus MQTT subscriber and analytics processor.

Subscribes to campus/+/+/+/telemetry, validates each payload, calculates derived
values, and prints clear alerts for abnormal conditions.
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


CONFIG_PATH = Path(__file__).resolve().parents[1] / "simulator" / "config.json"
SUBSCRIBE_TOPIC = "campus/+/+/+/telemetry"
TOPIC_POLICY = re.compile(r"^campus/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/telemetry$")

# Excel output — single persistent file, rows are always appended
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)
EXCEL_PATH = DATA_DIR / "campus_telemetry.xlsx"

EXCEL_HEADERS = [
    "recorded_at", "deviceId", "label", "building", "room",
    "temperature_C", "humidity_%", "occupancy", "light_level",
    "air_quality_raw", "battery_%", "status",
    "comfort_index", "occupancy_status", "air_quality_status",
    "abnormal_temp", "alerts",
]

REQUIRED_FIELDS = {
    "deviceId": str,
    "building": str,
    "room": str,
    "timestamp": str,
    "temperature": (int, float),
    "humidity": (int, float),
    "occupancy": int,
    "light_level": (int, float),
    "air_quality": (int, float),
    "battery_level": (int, float),
    "status": str,
}


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _init_excel():
    """Create the Excel file with a styled header row — only if it does not exist yet."""
    if EXCEL_PATH.exists():
        print(f"[EXCEL] Appending to existing file: {EXCEL_PATH.name}")
        return  # file already has headers — just keep appending

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Telemetry"

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(fill_type="solid", fgColor="1F4E79")
    header_align = Alignment(horizontal="center", vertical="center")

    for col, header in enumerate(EXCEL_HEADERS, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    # Set sensible column widths
    widths = [22, 14, 14, 22, 14, 14, 12, 10, 12, 16, 10, 12, 14, 16, 18, 14, 40]
    for col, width in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

    wb.save(EXCEL_PATH)
    print(f"[EXCEL] Created new file: {EXCEL_PATH.name}")


def save_to_excel(payload, derived, alerts):
    """Append one row of telemetry data (with local timestamp) to the Excel file.

    Retries up to 3 times if the file is locked (e.g. open in Excel).
    All error messages are ASCII-only to avoid cp1252 encoding errors on Windows.
    """
    recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        recorded_at,
        payload["deviceId"],
        payload.get("label", payload["deviceId"]),
        payload["building"],
        payload["room"],
        payload["temperature"],
        payload["humidity"],
        payload["occupancy"],
        payload["light_level"],
        payload["air_quality"],
        payload["battery_level"],
        payload["status"],
        derived["comfort_index"],
        derived["occupancy_status"],
        derived["air_quality_status"],
        derived["abnormal_temperature_flag"],
        ", ".join(alerts) if alerts else "None",
    ]

    for attempt in range(1, 4):
        try:
            wb = openpyxl.load_workbook(EXCEL_PATH)
            ws = wb.active
            ws.append(row)
            wb.save(EXCEL_PATH)
            return  # success
        except PermissionError:
            if attempt < 3:
                print(f"[EXCEL] File locked (attempt {attempt}/3), retrying...")
                time.sleep(0.5)
            else:
                print("[EXCEL] File still locked after 3 attempts — row skipped.")
                return
        except Exception:
            print("[EXCEL] Unexpected error while saving row — skipping.")
            return


def safe_text(value):
    """Sanitize values before printing them in logs."""
    return re.sub(r"[^A-Za-z0-9_ .:/@+-]", "_", str(value))[:120]


def validate_payload(payload):
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return False, f"missing fields: {', '.join(missing)}"

    for field, expected_type in REQUIRED_FIELDS.items():
        if not isinstance(payload[field], expected_type):
            return False, f"invalid type for {field}"

    if payload["occupancy"] < 0:
        return False, "occupancy cannot be negative"
    if not 0 <= payload["battery_level"] <= 100:
        return False, "battery_level must be between 0 and 100"
    if not 0 <= payload["humidity"] <= 100:
        return False, "humidity must be between 0 and 100"

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False, "invalid timestamp format"

    return True, "valid"


def calculate_derived_values(payload):
    temperature = float(payload["temperature"])
    humidity = float(payload["humidity"])
    occupancy = int(payload["occupancy"])
    air_quality = float(payload["air_quality"])

    comfort_index = round(temperature + (humidity / 100 * 5), 2)
    occupancy_status = "EMPTY" if occupancy == 0 else "OCCUPIED"

    if air_quality <= 80:
        air_quality_status = "GOOD"
    elif air_quality <= 120:
        air_quality_status = "MODERATE"
    else:
        air_quality_status = "POOR"

    return {
        "comfort_index": comfort_index,
        "occupancy_status": occupancy_status,
        "abnormal_temperature_flag": temperature > 35,
        "air_quality_status": air_quality_status,
    }


def evaluate_alerts(payload):
    alerts = []
    if payload["temperature"] > 35:
        alerts.append("High temperature")
    if payload["occupancy"] == 0 and payload["light_level"] > 60:
        alerts.append("Empty room with lights on")
    if payload["air_quality"] > 120:
        alerts.append("Poor air quality")
    if payload["humidity"] > 80:
        alerts.append("Abnormal humidity")
    if payload["battery_level"] < 20:
        alerts.append("Low battery")
    return alerts


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MQTT] Connected. Subscribing to {SUBSCRIBE_TOPIC}")
        client.subscribe(SUBSCRIBE_TOPIC)
    else:
        print(f"[MQTT] Connection failed with code: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    print(f"[MQTT] Disconnected. reason_code={reason_code}")


def on_message(client, userdata, message):
    topic = message.topic
    if not TOPIC_POLICY.match(topic):
        print(f"[SECURITY] Rejected message from invalid topic: {safe_text(topic)}")
        return

    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"[VALIDATION] Rejected invalid JSON on {safe_text(topic)}")
        return

    is_valid, reason = validate_payload(payload)
    if not is_valid:
        print(f"[VALIDATION] Rejected payload from {safe_text(topic)}: {safe_text(reason)}")
        return

    derived = calculate_derived_values(payload)
    alerts = evaluate_alerts(payload)
    device_id = safe_text(payload["deviceId"])
    label = safe_text(payload.get("label", payload["deviceId"]))

    print(
        f"[DATA] {label} | temp={payload['temperature']}C "
        f"humidity={payload['humidity']}% occupancy={payload['occupancy']} "
        f"comfort_index={derived['comfort_index']} "
        f"air_quality={derived['air_quality_status']}"
    )

    for alert in alerts:
        print(f"[ALERT] {label}: {alert}")

    save_to_excel(payload, derived, alerts)


def main():
    config = load_config()
    mqtt_config = config["mqtt"]
    _init_excel()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="smart-campus-processor")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    if mqtt_config.get("username"):
        client.username_pw_set(mqtt_config["username"], mqtt_config.get("password", ""))

    print("[PROCESSOR] Starting subscriber...")
    client.connect(mqtt_config["broker"], int(mqtt_config["port"]), int(mqtt_config["keepalive"]))
    client.loop_forever()


if __name__ == "__main__":
    main()
