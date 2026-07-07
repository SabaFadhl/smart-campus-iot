"""
Generate Word (.docx) documents for the Smart Campus IoT project reports.
Run this script from inside the report/ folder or from the project root.
"""

from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


REPORT_DIR = Path(__file__).parent


# ── helpers ─────────────────────────────────────────────────────────────────

def set_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    if level == 1:
        run.font.color.rgb = RGBColor(0x1F, 0x45, 0x88)   # dark blue
    elif level == 2:
        run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)   # mid blue
    else:
        run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light List Accent 1"

    # header row
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True

    # data rows
    for r_idx, row in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val

    doc.add_paragraph()   # spacing after table


def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.style = "No Spacing"
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    # light grey shading
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2")
    p._p.get_or_add_pPr().append(shd)
    doc.add_paragraph()


# ── Final Report ─────────────────────────────────────────────────────────────

def build_final_report():
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin   = Inches(1.2)
        section.right_margin  = Inches(1.2)

    # ── Title page ──
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Smart Campus IoT\nSimulation and Analytics Platform")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(0x1F, 0x45, 0x88)

    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run(
        "Course: Internet of Things\n"
        "Program: Master of IT\n"
        "University: Sana'a University\n"
        "Supervisor: Dr. Ammar Zahary\n\n"
        "Team Members:\n"
        "1. Osama Haider\n"
        "2. Saba Al-wesabi\n\n"
        "Date: July 2026"
    ).font.size = Pt(12)
    doc.add_page_break()

    # ── Abstract ──
    set_heading(doc, "Abstract", 1)
    doc.add_paragraph(
        "This project presents a simulation-only Internet of Things platform for smart campus "
        "monitoring. Instead of using physical sensors and hardware boards, the system uses Python "
        "virtual devices to generate realistic telemetry from campus rooms. The simulated devices "
        "publish data to an MQTT broker using a structured topic hierarchy. A Python subscriber "
        "receives the data, validates the payload, calculates derived analytics values, and prints "
        "alerts for abnormal conditions. A Node-RED Dashboard flow visualizes live temperature, "
        "humidity, occupancy, alerts, and temperature trends.\n\n"
        "The selected wireless model is IEEE 802.15.4 / Zigbee-like, suitable for indoor campus "
        "sensor networks that send small periodic messages at low power. The simulator includes "
        "packet loss, random delay, RSSI, link quality, estimated energy consumption, and battery "
        "drain to make the communication model realistic."
    )

    # ── Problem Statement ──
    set_heading(doc, "1. Problem Statement and Scenario", 1)
    doc.add_paragraph(
        "University campuses include many spaces that require continuous monitoring. Classrooms "
        "need acceptable temperature and lighting. Labs may need air quality monitoring. Offices "
        "benefit from occupancy-based energy saving. Server rooms need fast detection of high "
        "temperature to protect equipment.\n\n"
        "This project uses software simulation to demonstrate a full IoT workflow without "
        "physical hardware. The scenario is a smart campus with 7 monitored locations:"
    )
    add_table(doc,
        ["Device ID", "Label", "Building", "Monitoring Purpose"],
        [
            ["hall_1_1",    "Hall 1.1",    "floor_1",              "Teaching – comfort & occupancy"],
            ["hall_1_2",    "Hall 1.2",    "floor_1",              "Teaching – comfort & occupancy"],
            ["hall_1_3",    "Hall 1.3",    "floor_1",              "Teaching – comfort & occupancy"],
            ["hall_1_4",    "Hall 1.4",    "floor_1",              "Teaching – comfort & occupancy"],
            ["server_room", "Server Room", "it_building",          "High-temperature risk monitoring"],
            ["lab1",        "Lab 1",       "engineering_building", "Lab comfort & air quality"],
            ["office1",     "Office 1",    "admin_building",       "Energy saving & occupancy"],
        ]
    )

    # ── Architecture ──
    set_heading(doc, "2. IoT Architecture", 1)
    doc.add_paragraph(
        "The project follows a four-layer IoT architecture:"
    )
    for layer in [
        ("Perception Layer",   "Python virtual devices simulate sensors for temperature, humidity, occupancy, light level, air quality, battery level, and device status."),
        ("Network Layer",      "MQTT protocol transfers telemetry using a structured topic hierarchy through the HiveMQ Public Broker. Communication is modeled as IEEE 802.15.4 / Zigbee-like."),
        ("Processing Layer",   "processing/subscriber.py subscribes using a wildcard topic, validates each message, computes derived values, and evaluates alert rules."),
        ("Application Layer",  "A Node-RED Dashboard displays live gauges, alert text, and a temperature line chart for all devices."),
    ]:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(layer[0] + ": ").bold = True
        p.add_run(layer[1])

    # ── Wireless ──
    set_heading(doc, "3. Wireless Communication Choice", 1)
    doc.add_paragraph(
        "The selected wireless model is IEEE 802.15.4 / Zigbee-like. Campus room sensors send "
        "small packets at regular intervals and are often battery-powered, making Zigbee-like "
        "low-power communication the best fit."
    )
    set_heading(doc, "Comparison with Other Wireless Types", 2)
    add_table(doc,
        ["Feature", "Zigbee-like (Selected)", "Wi-Fi", "LoRaWAN"],
        [
            ["Range",           "Short–medium indoor",   "Medium indoor",      "Very long outdoor"],
            ["Power",           "Low ✓",                 "Higher",             "Very low"],
            ["Data rate",       "Low–moderate",          "High",               "Very low"],
            ["Best use",        "Indoor sensors ✓",      "High-bandwidth",     "Outdoor wide-area"],
            ["Suitability",     "High ✓",                "Medium",             "Low–medium"],
        ]
    )

    # ── MQTT ──
    set_heading(doc, "4. MQTT Topic Design and Payload Format", 1)
    doc.add_paragraph("Topic hierarchy:")
    add_code_block(doc, "campus/{building}/{room}/{deviceId}/telemetry")
    doc.add_paragraph("Example:")
    add_code_block(doc, "campus/floor_1/hall_1_1/hall_1_1/telemetry")
    doc.add_paragraph("Example JSON payload:")
    add_code_block(doc,
        '{\n'
        '  "deviceId": "hall_1_1",\n'
        '  "label": "Hall 1.1",\n'
        '  "building": "floor_1",\n'
        '  "room": "hall_1_1",\n'
        '  "timestamp": "2026-07-07T09:00:00+00:00",\n'
        '  "temperature": 26.4,\n'
        '  "humidity": 58.2,\n'
        '  "occupancy": 22,\n'
        '  "light_level": 70.5,\n'
        '  "air_quality": 67.3,\n'
        '  "battery_level": 94.8,\n'
        '  "status": "OK",\n'
        '  "wireless": {\n'
        '    "model": "IEEE 802.15.4 / Zigbee-like",\n'
        '    "packet_loss_rate": 0.05,\n'
        '    "random_delay_ms": 180,\n'
        '    "link_quality": 88,\n'
        '    "rssi": -63,\n'
        '    "estimated_energy_consumption_mwh": 0.036\n'
        '  }\n'
        '}'
    )

    # ── Processing ──
    set_heading(doc, "5. Processing Logic and Rules", 1)
    set_heading(doc, "Derived Values", 2)
    add_table(doc,
        ["Derived Value", "Description"],
        [
            ["comfort_index",      "temperature + (humidity / 100 × 5)"],
            ["occupancy_status",   "EMPTY or OCCUPIED"],
            ["high_temp_flag",     "True when temperature > 35"],
            ["air_quality_status", "GOOD / MODERATE / POOR"],
        ]
    )
    set_heading(doc, "Alert Rules", 2)
    add_table(doc,
        ["Alert", "Condition"],
        [
            ["High temperature",          "temperature > 35"],
            ["Empty room with lights on", "occupancy = 0 AND light_level > 60"],
            ["Poor air quality",          "air_quality > 120"],
            ["Abnormal humidity",         "humidity > 80"],
            ["Low battery",               "battery_level < 20"],
        ]
    )

    # ── Dashboard ──
    set_heading(doc, "6. Dashboard Design", 1)
    doc.add_paragraph(
        "The Node-RED Dashboard (dashboard/node_red_flow.json) contains:"
    )
    for item in [
        "Temperature gauge (live reading)",
        "Humidity gauge (live reading)",
        "Occupancy gauge (live reading)",
        "Alert text widget (latest active alert per device)",
        "Temperature line chart (historical trend for all devices)",
    ]:
        doc.add_paragraph(item, style="List Bullet")
    doc.add_paragraph(
        "\nTo import: open Node-RED → Menu → Import → paste node_red_flow.json content → Deploy.\n"
        "Dashboard URL: http://localhost:1880/ui"
    )

    # ── Security ──
    set_heading(doc, "7. Security and Reliability", 1)
    set_heading(doc, "Security Controls", 2)
    for ctrl in [
        "Input validation: subscriber rejects payloads with missing or invalid fields.",
        "Topic naming policy: only the expected topic format is accepted (campus/+/+/+/telemetry).",
        "Sanitized logs: values are cleaned before printing to reduce log injection risk.",
        "Optional MQTT credentials: username/password fields in config.json for private brokers.",
        "Limited topic structure: predictable hierarchy prevents arbitrary topic publishing.",
    ]:
        doc.add_paragraph(ctrl, style="List Bullet")
    set_heading(doc, "Reliability Features", 2)
    for item in [
        "Packet loss simulation (5% drop rate).",
        "Random transmission delay (50–350 ms).",
        "Battery drain tracking per device.",
        "Disconnection event logging.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    # ── Testing ──
    set_heading(doc, "8. Testing and Results", 1)
    add_table(doc,
        ["Test Case", "Description", "Expected Result", "Status"],
        [
            ["TC-1: Normal Telemetry",    "Start simulator and subscriber",          "[DATA] lines printed with derived values", "Pass"],
            ["TC-2: Missing Field",        "Publish JSON with only partial fields",   "[VALIDATION] Rejected message",           "Pass"],
            ["TC-3: Abnormal Temperature", "Publish temp=38 for server_room",         "[ALERT] Server Room: High temperature",   "Pass"],
            ["TC-4: Broker Disconnection", "Change broker address to invalid host",   "Connection failure reported",             "Pass (manual)"],
        ]
    )

    # ── Challenges ──
    set_heading(doc, "9. Challenges and Limitations", 1)
    doc.add_paragraph(
        "The main challenge is balancing realism with simplicity. A real Zigbee network includes "
        "routing, interference, mesh topology, and device association. This project models only "
        "the most important educational aspects: packet loss, delay, RSSI, link quality, energy, "
        "and battery drain.\n\n"
        "Another limitation is the use of a public MQTT broker (HiveMQ). A production system "
        "would require a private broker with TLS, authentication, and access control."
    )

    # ── Conclusion ──
    set_heading(doc, "10. Conclusion and Future Work", 1)
    doc.add_paragraph(
        "This project demonstrates a complete IoT workflow without physical hardware. Python virtual "
        "devices simulate 7 campus locations. MQTT provides lightweight publish/subscribe "
        "communication. The subscriber validates data, computes analytics, and triggers alerts. "
        "Node-RED Dashboard provides live visualization.\n\n"
        "Future improvements:"
    )
    for fw in [
        "Store telemetry in SQLite or InfluxDB for historical analysis.",
        "Add TLS and authenticated MQTT clients.",
        "Build a custom web dashboard with real-time charts.",
        "Add device registration and role-based access control.",
        "Implement predictive analytics for temperature and air quality.",
    ]:
        doc.add_paragraph(fw, style="List Bullet")

    # ── References ──
    set_heading(doc, "11. References", 1)
    for ref in [
        "MQTT Organization. MQTT Protocol Documentation. https://mqtt.org/",
        "Eclipse Paho. Paho MQTT Python Client. https://eclipse.dev/paho/",
        "Node-RED Documentation. https://nodered.org/docs/",
        "HiveMQ Public MQTT Broker. https://www.hivemq.com/mqtt/public-mqtt-broker/",
        "IEEE 802.15.4 Standard Overview. https://standards.ieee.org/ieee/802.15.4/11041/",
        "Connectivity Standards Alliance Zigbee. https://csa-iot.org/all-solutions/zigbee/",
    ]:
        doc.add_paragraph(ref, style="List Number")

    out_path = REPORT_DIR / "final_report.docx"
    doc.save(out_path)
    print(f"[OK] Saved: {out_path.name}")


# ── Proposal ─────────────────────────────────────────────────────────────────

def build_proposal():
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin   = Inches(1.2)
        section.right_margin  = Inches(1.2)

    # Title
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("Smart Campus IoT Simulation and Analytics Platform\nProject Proposal")
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = RGBColor(0x1F, 0x45, 0x88)

    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(
        "Course: Internet of Things  |  Program: Master of IT\n"
        "Supervisor: Dr. Ammar Zahary  |  Sana'a University\n\n"
        "Team Members:\n"
        "1. Osama Haider\n"
        "2. Saba Al-wesabi"
    ).font.size = Pt(11)
    doc.add_paragraph()

    set_heading(doc, "1. Problem", 1)
    doc.add_paragraph(
        "Modern campuses contain classrooms, labs, offices, and server rooms that need continuous "
        "monitoring for comfort, safety, and energy efficiency. Building a full hardware IoT "
        "prototype is costly and time-consuming for a course project. This project solves that "
        "by creating a simulation-only IoT platform that demonstrates the complete IoT workflow "
        "without physical sensors."
    )

    set_heading(doc, "2. Scenario", 1)
    doc.add_paragraph(
        "Smart Campus Environment Monitoring with 7 virtual devices across a university campus:"
    )
    add_table(doc,
        ["Device ID", "Label", "Building", "Purpose"],
        [
            ["hall_1_1",    "Hall 1.1",    "floor_1",              "Teaching environment monitoring"],
            ["hall_1_2",    "Hall 1.2",    "floor_1",              "Teaching environment monitoring"],
            ["hall_1_3",    "Hall 1.3",    "floor_1",              "Teaching environment monitoring"],
            ["hall_1_4",    "Hall 1.4",    "floor_1",              "Teaching environment monitoring"],
            ["server_room", "Server Room", "it_building",          "High-temperature risk monitoring"],
            ["lab1",        "Lab 1",       "engineering_building", "Lab comfort & air quality"],
            ["office1",     "Office 1",    "admin_building",       "Office energy & occupancy"],
        ]
    )

    set_heading(doc, "3. Selected Tools", 1)
    add_table(doc,
        ["Tool", "Purpose"],
        [
            ["Python 3",        "Virtual device simulator and MQTT subscriber"],
            ["Paho MQTT",       "Python MQTT client library"],
            ["HiveMQ Broker",   "Public MQTT broker for testing"],
            ["Node-RED",        "Dashboard for live visualization"],
            ["python-docx",     "Report generation"],
        ]
    )

    set_heading(doc, "4. Wireless Communication Model", 1)
    doc.add_paragraph(
        "Selected model: IEEE 802.15.4 / Zigbee-like.\n\n"
        "Justification: Campus room sensors send small packets at low frequency and may be "
        "battery-powered. Zigbee-like communication is ideal for short-range indoor sensor "
        "networks with low power requirements.\n\n"
        "The simulator includes: packet loss rate, random delay, RSSI, link quality, "
        "estimated energy consumption, and battery drain per transmission."
    )

    set_heading(doc, "5. System Architecture", 1)
    for layer in [
        "Virtual Device Layer → Python devices generate simulated sensor readings.",
        "Communication Layer → MQTT topics transfer telemetry from devices to subscribers.",
        "Processing Layer → Python subscriber validates, computes derived values, and triggers alerts.",
        "Presentation Layer → Node-RED Dashboard displays live values and trends.",
    ]:
        doc.add_paragraph(layer, style="List Number")

    set_heading(doc, "6. MQTT Topic Design", 1)
    add_code_block(doc, "campus/{building}/{room}/{deviceId}/telemetry")
    doc.add_paragraph("Example:")
    add_code_block(doc, "campus/floor_1/hall_1_1/hall_1_1/telemetry")

    set_heading(doc, "7. Expected Deliverables", 1)
    for d in [
        "Runnable Python simulator (7 virtual devices).",
        "MQTT subscriber with validation, analytics, and alerts.",
        "Node-RED Dashboard flow JSON.",
        "Test cases documentation.",
        "Final technical report (8–12 pages).",
        "Demo video (5–8 minutes).",
        "Short presentation (5–7 slides).",
    ]:
        doc.add_paragraph(d, style="List Bullet")

    out_path = REPORT_DIR / "proposal.docx"
    doc.save(out_path)
    print(f"[OK] Saved: {out_path.name}")


# ── Presentation ──────────────────────────────────────────────────────────────

def build_presentation_doc():
    """
    Creates a Word doc that mimics a 6-slide presentation layout.
    The student can copy/paste these into PowerPoint.
    """
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(1)
        section.right_margin  = Inches(1)

    slides = [
        {
            "title": "Slide 1 – Title",
            "body": [
                "Smart Campus IoT Simulation and Analytics Platform",
                "Course: Internet of Things | Master of IT",
                "Supervisor: Dr. Ammar Zahary | Sana'a University",
                "Team Members: 1. Osama Haider     2. Saba Al-wesabi",
                "Date: July 2026",
            ]
        },
        {
            "title": "Slide 2 – Problem and Scenario",
            "body": [
                "Campus rooms need continuous monitoring (comfort, safety, energy).",
                "Physical hardware is costly → we use Python simulation only.",
                "7 virtual devices: Hall 1.1, Hall 1.2, Hall 1.3, Hall 1.4, Server Room, Lab 1, Office 1.",
                "Sensors: temperature, humidity, occupancy, light level, air quality.",
            ]
        },
        {
            "title": "Slide 3 – System Architecture",
            "body": [
                "Layer 1 – Perception: Python virtual devices generate telemetry every 5 seconds.",
                "Layer 2 – Network: MQTT publish/subscribe via HiveMQ broker.",
                "           Topic: campus/{building}/{room}/{deviceId}/telemetry",
                "Layer 3 – Processing: Python subscriber validates and analyzes data.",
                "Layer 4 – Application: Node-RED Dashboard shows live readings and charts.",
                "Wireless model: IEEE 802.15.4 / Zigbee-like (packet loss, delay, RSSI, battery drain).",
            ]
        },
        {
            "title": "Slide 4 – Simulation and MQTT Design",
            "body": [
                "Each device publishes a JSON payload every 5 seconds.",
                "Payload fields: deviceId, label, timestamp, temperature, humidity,",
                "                occupancy, light_level, air_quality, battery_level, status, wireless.",
                "Zigbee-like simulation: 5% packet loss, 50–350 ms delay, RSSI, link quality, energy use.",
                "Battery drains with each transmission → status becomes LOW_BATTERY below 20%.",
            ]
        },
        {
            "title": "Slide 5 – Dashboard, Alerts, and Testing",
            "body": [
                "Dashboard: temperature gauge, humidity gauge, occupancy gauge,",
                "           alert text widget, temperature history chart.",
                "Alert Rules (5 rules):",
                "  • Temperature > 35°C → High temperature",
                "  • Occupancy = 0 AND light > 60 → Empty room with lights on",
                "  • Air quality > 120 → Poor air quality",
                "  • Humidity > 80% → Abnormal humidity",
                "  • Battery < 20% → Low battery",
                "Test Cases: Normal data, Missing field, Abnormal temperature, Broker disconnection.",
            ]
        },
        {
            "title": "Slide 6 – Results, Challenges, and Conclusion",
            "body": [
                "Results: Full IoT workflow demonstrated without physical hardware.",
                "MQTT wildcard subscription (campus/+/+/+/telemetry) handles all devices.",
                "Zigbee-like model adds realistic low-power wireless behavior.",
                "Challenges: Public broker dependency, simulated data realism.",
                "Future work: Database storage, TLS authentication, web dashboard, predictive analytics.",
            ]
        },
    ]

    for slide in slides:
        set_heading(doc, slide["title"], 1)
        for line in slide["body"]:
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(line)
        doc.add_paragraph()

    out_path = REPORT_DIR / "presentation_slides.docx"
    doc.save(out_path)
    print(f"[OK] Saved: {out_path.name}")


# ── Run all ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating Word documents...")
    build_proposal()
    build_final_report()
    build_presentation_doc()
    print("\nDone! All 3 files saved in the report/ folder.")
