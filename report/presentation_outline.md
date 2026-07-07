# Presentation Outline - 6 Slides

## Slide 1: Title

**Smart Campus IoT Simulation and Analytics Platform**

- Master of IT - Internet of Things
- Simulation-only project
- Team members: Osama Haider, Saba Al-wesabi
- Date: July 2026

## Slide 2: Problem and Scenario

- Campus rooms need monitoring for comfort, safety, and energy efficiency.
- Hardware sensors are replaced with Python virtual devices.
- Seven simulated locations:
  - Hall 1.1, Hall 1.2, Hall 1.3, Hall 1.4
  - Server Room
  - Lab 1
  - Office 1

## Slide 3: System Architecture

- Virtual devices generate telemetry.
- MQTT broker transfers data using publish/subscribe.
- Python subscriber validates and analyzes telemetry.
- Node-RED Dashboard shows live values, alerts, and charts.

## Slide 4: Simulation and MQTT Design

- Telemetry every 5 seconds.
- Topic format: `campus/{building}/{room}/{deviceId}/telemetry`
- Payload includes temperature, humidity, occupancy, light, air quality, battery, and status.
- Zigbee-like model includes packet loss, delay, RSSI, link quality, energy use, and battery drain.

## Slide 5: Dashboard, Alerts, and Testing

- Dashboard displays:
  - Latest temperature
  - Humidity
  - Occupancy
  - Alerts
  - Temperature chart
- Alert rules:
  - Temperature > 35
  - Empty room with lights on
  - Air quality > 120
  - Humidity > 80
- Test cases cover normal data, missing fields, abnormal temperature, and broker disconnection.

## Slide 6: Results, Challenges, and Conclusion

- The platform demonstrates a complete IoT workflow without hardware.
- MQTT wildcard subscription simplifies data collection.
- Zigbee-like simulation supports realistic low-power network behavior.
- Challenges include public broker dependency and simulated data realism.
- Future work: database storage, authentication, web dashboard, and predictive analytics.
