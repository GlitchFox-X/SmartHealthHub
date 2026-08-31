# Arduino Setup Guide

## Arduino Mega 2560 Configuration for Smart Health Hub

This guide explains how to set up and upload the Arduino firmware for the Smart Health Hub system.

## Prerequisites

- Arduino Mega 2560 microcontroller
- USB cable (Type A to micro-B)
- Arduino IDE installed on computer
- Smart Health Hub project files

## Step 1: Install Arduino IDE

Download and install from: https://www.arduino.cc/en/software

Supported versions: 1.8.x or 2.x

## Step 2: Connect Arduino Mega 2560

1. Connect Arduino Mega to computer using USB cable
2. Wait for Windows/Linux to recognize USB device
3. LED on Arduino should light up

## Step 3: Select Board and Port

In Arduino IDE:

1. **Tools → Board → Arduino Mega 2560 or Mega ADK**
2. **Tools → Port → Select the COM port**
   - On Windows: COM3, COM4, etc.
   - On Mac: /dev/cu.usbmodem*
   - On Linux: /dev/ttyUSB0, /dev/ttyUSB1, etc.

## Step 4: Open Sketch

1. File → Open
2. Navigate to `arduino/sketch.ino`
3. File should open in Arduino IDE

## Step 5: Verify Code

Click **Sketch → Verify/Compile** (checkmark icon)

Should see: "Compilation complete" in green

## Step 6: Upload Code

Click **Sketch → Upload** (arrow icon)

Progress will show in status bar. Wait for: "Upload complete"

## Step 7: Verify Communication

Open **Tools → Serial Monitor**

Set baud rate to **9600**

Arduino should restart and display:
```
{"type":"status","value":"READY"}
```

This means Arduino is working!

## Sensor Wiring

### Analog Inputs (A0-A3)

```
Pulse Sensor Signal   → Arduino A0 (analog input)
LM35 Sensor Output    → Arduino A1 (analog input)
Touch Sensor Signal   → Arduino A2 (analog input)
ECG Module Output     → Arduino A3 (analog input)
```

### Digital Outputs (for ECG reference)

```
ECG LO+ (Reference)   → Arduino D10 (digital input)
ECG LO- (Reference)   → Arduino D11 (digital input)
```

### Power

```
All sensors 5V        → Arduino 5V
All sensors GND       → Arduino GND
```

## Testing the Arduino

### Test 1: Serial Communication

With Serial Monitor open at 9600 baud:

Send command:
```
START_TEST
```

Arduino should respond:
```
{"type":"status","value":"TOUCH_WAIT"}
```

### Test 2: Pulse Sensor

1. Connect pulse sensor to A0
2. Monitor A0 value in Arduino IDE
3. Place finger on sensor - values should change

### Test 3: Temperature Sensor

1. Connect LM35 to A1
2. Monitor A1 value
3. Touch sensor with finger - values should decrease when warm, increase when cold

### Test 4: Touch Sensor

1. Connect touch sensor to A2
2. Send: `START_TEST`
3. Touch and hold sensor pad for 3 seconds
4. Arduino should respond: `{"type":"status","value":"TOUCH_CONFIRMED"}`

### Test 5: ECG Module

1. Connect ECG module output to A3
2. Connect lead-off pins to D10 and D11
3. Send: `START_ECG`
4. Arduino should stream ECG samples:
```
{"type":"ecg","timestamp":1000,"value":512}
{"type":"ecg","timestamp":1010,"value":515}
```
5. Send: `STOP_ECG`

## Command Reference

Send these commands over serial at 9600 baud:

### START_TEST
- Initiates basic health test
- Waits for 3-second touch confirmation
- Then collects 10 seconds of pulse and temperature data
- Responds: `{"type":"basic","pulse":72,"temperature":36.7,"bp":"UNAVAILABLE"}`

### START_ECG
- Begins ECG recording
- Streams samples at ~100 Hz
- Format: `{"type":"ecg","timestamp":X,"value":Y}`

### STOP_ECG
- Stops ECG recording
- Responds: `{"type":"status","value":"ECG_COMPLETE"}`

### RESET
- Resets all counters
- Responds: `{"type":"status","value":"READY"}`

## Serial Protocol Details

All communication uses **JSON format** with one message per line.

**Baud Rate:** 9600
**Data Bits:** 8
**Stop Bits:** 1
**Parity:** None

### Message Types

**Status Messages:**
```json
{"type":"status","value":"<STATUS>"}
```

Status values:
- `READY` - Device initialized
- `TOUCH_WAIT` - Waiting for touch confirmation
- `TOUCH_CONFIRMED` - Touch confirmed, test starting
- `TOUCH_LOST` - Touch lost during confirmation
- `TEST_ONGOING` - Test in progress
- `TEST_COMPLETE` - Test finished
- `ECG_STARTING` - ECG recording started
- `ECG_COMPLETE` - ECG recording finished
- `ECG_LEAD_OFF` - Electrode disconnected

**Basic Test Result:**
```json
{"type":"basic","pulse":72,"temperature":36.7,"bp":"UNAVAILABLE"}
```

**ECG Sample:**
```json
{"type":"ecg","timestamp":1000,"value":512}
```

## Troubleshooting

### Arduino Not Appearing in Port List

**Solution:**
1. Check USB cable (try different cable)
2. Try different USB port on computer
3. Install CH340 driver (some Arduino clones use this)
4. Restart Arduino IDE
5. Restart computer

### "Board not found" Error

**Solution:**
1. Verify correct board selected: **Arduino Mega 2560**
2. Verify correct port selected
3. Try uploading at different baud rate (in Tools → Upload Speed)

### Upload Fails

**Solution:**
1. Press RESET button on Arduino, immediately try uploading
2. Select different USB port
3. Try lower upload speed (57600 instead of 115200)
4. Check if Arduino Mega bootloader is corrupted (rare)

### Serial Monitor Shows Garbage

**Solution:**
1. Verify baud rate is **9600**
2. Check USB cable connection
3. Try different USB port

### Sensors Not Responding

**Solution:**
1. Check wiring connections
2. Verify power (5V) is reaching sensor
3. Check analog pins are correct (A0-A3)
4. Test with multimeter if available
5. Try different sensor if available

## Important Notes

### Real Sensor Data
- All readings are from actual sensors
- No synthetic data generation
- Sensor outage is handled gracefully
- Readings are averaged over buffer period

### Touch Confirmation
- Required 3-second continuous touch
- If touch is lost, timer resets
- Capacitive touch sensor sensitivity may need adjustment

### ECG Sampling
- Samples collected at approximately 100 Hz (10ms intervals)
- Raw ADC values (0-1023)
- No filtering applied in Arduino (raw data preserved)
- Lead-off detection via digital pins

### Temperature Calibration
- Default calibration for LM35
- Adjust in `config.py` if needed
- Formula: `(ADC / 1023.0) * 5.0 * 100`

## Calibration Procedures

### Temperature Sensor Calibration

1. Connect LM35 to Arduino A1
2. Read raw ADC value from Serial Monitor
3. Place in ice water (0°C) - record ADC
4. Place in warm water (37°C) - record ADC
5. Calculate scaling factor
6. Update `TEMPERATURE_MULTIPLIER` in `config.py`

### Pulse Sensor Calibration

1. Connect pulse sensor to Arduino A0
2. Read raw values over 10 seconds
3. Place finger on sensor with known good pulse rate
4. Record minimum and maximum ADC values
5. Adjust `MIN_RAW_VALUE` and `MAX_RAW_VALUE` if needed

## Safety Considerations

### Electrical Safety
- Always verify voltage before connecting sensors
- Use proper 5V regulated power supply
- Don't exceed 5V input on analog pins
- Use protective case for Arduino in medical environment

### Signal Safety
- ECG is for monitoring only, not diagnosis
- Electrodes should not carry harmful voltage
- AD8232 module has built-in protection
- Lead-off detection prevents false readings

### Data Safety
- All data is local (Raspberry Pi storage)
- No data transmitted during test (only after)
- USB connection is data-only (no power over USB to sensors)

## Arduino IDE Tips

### Libraries Required
- **NONE** - This sketch uses only Arduino core functions
- No external libraries to install
- Compatible with all Mega 2560 boards

### Debugging
Enable serial output by uncommenting debug lines if needed:
- Currently no debug lines in production code
- Can add Serial.print() for development

### Performance
- Sketch size: ~3-4KB (plenty of space on Mega)
- RAM usage: ~200 bytes (plenty available)
- Processing speed: Sufficient for 100 Hz ECG

## Production Deployment

### Pre-Deployment Tests
- [ ] Verify serial communication at 9600 baud
- [ ] Test each sensor individually
- [ ] Perform full 10-second basic test
- [ ] Perform 30-second ECG recording
- [ ] Verify JSON output format
- [ ] Test lead-off detection

### Permanent Installation
1. Mount Arduino securely in enclosure
2. Route USB cable safely (avoid stress)
3. Label all sensor connections
4. Test monthly
5. Keep power supply stable and regulated

## Reference Documents

- **Arduino IDE**: https://www.arduino.cc
- **Arduino Mega 2560**: https://www.arduino.cc/en/Guide/ArduinoMega2560
- **AD8232 ECG Module**: Datasheet from AD8232 manufacturer
- **LM35 Temperature**: LM35 datasheet
- **Serial Communication**: Arduino Serial reference

## Support

If the Arduino doesn't respond:

1. Check USB connection
2. Verify board and port selection
3. Check Serial Monitor baud rate (9600)
4. Review sketch for errors
5. Check sensor wiring
6. Test with different Arduino if available

---

**Last Updated:** 2026-08-31
**Compatible Arduino:** Mega 2560
**Baud Rate:** 9600
**Protocol:** JSON over Serial
