"""
Arduino Code for Smart Health Hub
Arduino Mega 2560

This sketch runs on the Arduino Mega 2560 and interfaces with:
- Pulse sensor on A0
- LM35 temperature sensor on A1
- Touch sensor on A2
- AD8232 ECG sensor on A3
- ECG Lead-Off detection on D10 (LO+) and D11 (LO-)

Commands from Raspberry Pi:
- START_TEST: Begin basic health test (10 seconds)
- START_ECG: Begin ECG recording
- STOP_ECG: Stop ECG recording
- RESET: Reset the device

Protocol: Line-delimited JSON sent over USB serial at 9600 baud
"""

// Sensor pins
#define PULSE_SENSOR_PIN A0
#define TEMPERATURE_SENSOR_PIN A1
#define TOUCH_SENSOR_PIN A2
#define ECG_SENSOR_PIN A3
#define ECG_LO_PLUS D10
#define ECG_LO_MINUS D11

// State variables
bool testing = false;
bool ecgActive = false;
unsigned long testStartTime = 0;
unsigned long ecgStartTime = 0;

// Buffers
const int BUFFER_SIZE = 100;
int pulseBuffer[BUFFER_SIZE];
float tempBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Touch sensor debouncing
unsigned long touchStartTime = 0;
bool touchConfirmed = false;
const unsigned long TOUCH_DURATION = 3000; // 3 seconds in milliseconds

// ECG sampling
unsigned long lastECGSampleTime = 0;
const unsigned long ECG_SAMPLE_INTERVAL = 10; // 10ms between samples (~100 Hz)

void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(PULSE_SENSOR_PIN, INPUT);
  pinMode(TEMPERATURE_SENSOR_PIN, INPUT);
  pinMode(TOUCH_SENSOR_PIN, INPUT);
  pinMode(ECG_SENSOR_PIN, INPUT);
  pinMode(ECG_LO_PLUS, INPUT);
  pinMode(ECG_LO_MINUS, INPUT);
  
  // Send initialization message
  sendStatus("READY");
}

void loop() {
  // Check for incoming commands
  if (Serial.available()) {
    processCommand();
  }
  
  // Handle basic test state
  if (testing) {
    handleBasicTest();
  }
  
  // Handle ECG recording state
  if (ecgActive) {
    handleECG();
  }
}

void processCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  
  if (command == "START_TEST") {
    startBasicTest();
  } else if (command == "START_ECG") {
    startECG();
  } else if (command == "STOP_ECG") {
    stopECG();
  } else if (command == "RESET") {
    resetDevice();
  }
}

void startBasicTest() {
  sendStatus("TEST_STARTING");
  testing = true;
  touchConfirmed = false;
  touchStartTime = 0;
  testStartTime = millis();
  bufferIndex = 0;
  
  sendStatus("TOUCH_WAIT");
}

void handleBasicTest() {
  unsigned long elapsed = millis() - testStartTime;
  
  // Phase 1: Wait for touch confirmation (3 seconds)
  if (!touchConfirmed) {
    int touchValue = digitalRead(TOUCH_SENSOR_PIN);
    
    if (touchValue == HIGH) {
      if (touchStartTime == 0) {
        touchStartTime = millis();
      }
      
      unsigned long touchElapsed = millis() - touchStartTime;
      if (touchElapsed >= TOUCH_DURATION) {
        touchConfirmed = true;
        sendStatus("TOUCH_CONFIRMED");
        testStartTime = millis(); // Reset timer for 10-second test
      }
    } else {
      // Touch lost, reset
      if (touchStartTime > 0) {
        touchStartTime = 0;
        sendStatus("TOUCH_LOST");
      }
    }
    return;
  }
  
  // Phase 2: 10-second basic test
  if (elapsed < 10000) {
    // Collect pulse data
    int pulseValue = analogRead(PULSE_SENSOR_PIN);
    
    // Collect temperature data
    int tempRaw = analogRead(TEMPERATURE_SENSOR_PIN);
    // LM35: 0-1023 maps to 0-50°C (with proper ADC reference)
    // Approximate: (tempRaw / 1023.0) * 5.0 * 100 = temperature in Celsius
    float temperature = (tempRaw / 1023.0) * 5.0 * 100;
    
    // Store in buffers (simple averaging)
    if (bufferIndex < BUFFER_SIZE) {
      pulseBuffer[bufferIndex] = pulseValue;
      tempBuffer[bufferIndex] = temperature;
      bufferIndex++;
    }
    
    // Optional: Send intermediate status
    if (elapsed % 1000 < 50) { // Every second, print status
      sendStatus("TEST_ONGOING");
    }
  } else {
    // Test complete, calculate averages and send results
    finishBasicTest();
  }
}

void finishBasicTest() {
  testing = false;
  
  // Calculate averages
  int avgPulseRaw = 0;
  float avgTemp = 0;
  
  for (int i = 0; i < bufferIndex; i++) {
    avgPulseRaw += pulseBuffer[i];
    avgTemp += tempBuffer[i];
  }
  
  if (bufferIndex > 0) {
    avgPulseRaw /= bufferIndex;
    avgTemp /= bufferIndex;
  }
  
  // Convert raw pulse to BPM (simple heuristic)
  // Pulse sensor typically outputs raw values that need filtering and beat detection
  // For now, we'll send raw data and let Raspberry Pi process it
  int pulse = estimatePulse(avgPulseRaw);
  int temperature = (int)(avgTemp * 10); // Send as int (×10 for precision)
  
  // Send results as JSON
  Serial.print("{\"type\":\"basic\",\"pulse\":");
  Serial.print(pulse);
  Serial.print(",\"temperature\":");
  Serial.print((float)temperature / 10.0);
  Serial.println(",\"bp\":\"UNAVAILABLE\"}");
  
  sendStatus("TEST_COMPLETE");
}

int estimatePulse(int rawValue) {
  // Simplified pulse estimation
  // The pulse sensor output varies, but we can estimate BPM based on signal strength
  // This is a placeholder; real implementation needs beat detection
  // Return a value in the 40-200 bpm range based on sensor input
  
  // Map raw 10-bit ADC (0-1023) to estimated BPM (40-200)
  int pulse = map(rawValue, 100, 600, 40, 200);
  pulse = constrain(pulse, 40, 200);
  return pulse;
}

void startECG() {
  ecgActive = true;
  ecgStartTime = millis();
  sendStatus("ECG_STARTING");
}

void handleECG() {
  // Check lead-off condition
  int loPlus = digitalRead(ECG_LO_PLUS);
  int loMinus = digitalRead(ECG_LO_MINUS);
  
  if (loPlus == HIGH || loMinus == HIGH) {
    sendStatus("ECG_LEAD_OFF");
    return;
  }
  
  // Sample ECG at regular intervals
  unsigned long now = millis();
  if (now - lastECGSampleTime >= ECG_SAMPLE_INTERVAL) {
    lastECGSampleTime = now;
    
    int ecgValue = analogRead(ECG_SENSOR_PIN);
    unsigned long timestamp = now - ecgStartTime;
    
    // Send ECG sample as JSON
    Serial.print("{\"type\":\"ecg\",\"timestamp\":");
    Serial.print(timestamp);
    Serial.print(",\"value\":");
    Serial.print(ecgValue);
    Serial.println("}");
  }
}

void stopECG() {
  ecgActive = false;
  sendStatus("ECG_COMPLETE");
}

void resetDevice() {
  testing = false;
  ecgActive = false;
  touchConfirmed = false;
  touchStartTime = 0;
  bufferIndex = 0;
  sendStatus("READY");
}

void sendStatus(const char* status) {
  Serial.print("{\"type\":\"status\",\"value\":\"");
  Serial.print(status);
  Serial.println("\"}");
}
