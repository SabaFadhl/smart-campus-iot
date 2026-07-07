# Test Cases

## Test Case 1: Normal Telemetry

**Objective:** Verify that valid telemetry is accepted and processed.

**Steps:**
1. Start the subscriber.
2. Start the simulator.
3. Watch console output for `[DATA]` lines.

**Expected Result:**
- Subscriber accepts the message.
- Derived values are printed, including comfort index and air quality status.
- No validation rejection appears.

## Test Case 2: Missing Field

**Objective:** Verify that incomplete JSON payloads are rejected.

**Manual publish example:**

```powershell
mosquitto_pub -h broker.hivemq.com -t "campus/floor_1/hall_1_1/hall_1_1/telemetry" -m '{\"deviceId\":\"hall_1_1\",\"temperature\":25}'
```

**Expected Result:**
- Subscriber prints a `[VALIDATION] Rejected message` message.
- The reason includes missing fields.

## Test Case 3: Abnormal Temperature

**Objective:** Verify high temperature alert rule.

**Manual publish example:**

```powershell
mosquitto_pub -h broker.hivemq.com -t "campus/it_building/server_room/server_room/telemetry" -m '{\"deviceId\":\"server_room\",\"building\":\"it_building\",\"room\":\"server_room\",\"timestamp\":\"2026-07-07T12:00:00+00:00\",\"temperature\":38,\"humidity\":55,\"occupancy\":0,\"light_level\":30,\"air_quality\":70,\"battery_level\":90,\"status\":\"OK\"}'
```

**Expected Result:**
- Subscriber prints `[ALERT] Server Room: High temperature`.

## Test Case 4: Broker Disconnection

**Objective:** Verify system behavior when MQTT broker connectivity is interrupted.

**Steps:**
1. Start subscriber and simulator.
2. Disconnect the network temporarily or change broker address in `simulator/config.json` to an invalid host.
3. Run the application again.

**Expected Result:**
- Subscriber or simulator reports connection failure/disconnection.
- No invalid data is processed during broker outage.
- After restoring broker configuration, messages resume normally.

## Additional Alert Checks

| Rule | Test Input | Expected Alert |
|---|---|---|
| Empty room with lights on | `occupancy = 0`, `light_level > 60` | Empty room with lights on |
| Poor air quality | `air_quality > 120` | Poor air quality |
| Abnormal humidity | `humidity > 80` | Abnormal humidity |
