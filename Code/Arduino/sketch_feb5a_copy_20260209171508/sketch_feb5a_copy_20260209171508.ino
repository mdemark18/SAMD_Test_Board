const int ledPins[] = {2,3,4,5,6,7,8,9,10,11};
const int numLeds = sizeof(ledPins)/sizeof(ledPins[0]);

bool ledSeen[numLeds];          
bool ledOutOfSequence[numLeds];  
int sequenceOrder[numLeds];      
int nextSequenceIndex = 0;

void setup() {
  Serial.begin(115200);

  for(int i=0; i<numLeds; i++){
    pinMode(ledPins[i], INPUT_PULLUP);
    ledSeen[i] = false;
    ledOutOfSequence[i] = false;
    sequenceOrder[i] = -1;
  }
}

void loop() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (!cmd.equalsIgnoreCase("DEBUG")) return;

  // --- RESET ---
  for(int i=0; i<numLeds; i++){
    ledSeen[i] = false;
    ledOutOfSequence[i] = false;
    sequenceOrder[i] = -1;
  }
  nextSequenceIndex = 0;

  unsigned long startTime = millis();
  const unsigned long timeout = 10000; // 10s max

  while (millis() - startTime < timeout) {
    int ledsOnCount = 0;
    bool currentState[numLeds];
    for(int i=0;i<numLeds;i++){
      currentState[i] = (digitalRead(ledPins[i]) == LOW);
      if(currentState[i]) ledsOnCount++;
    }

    // Ignore sample if all LEDs are on
    if(ledsOnCount == numLeds) continue;

    // Track sequence
    for(int i=0; i<numLeds; i++){
      if(currentState[i] && !ledSeen[i]){
        ledSeen[i] = true;
        sequenceOrder[nextSequenceIndex] = i;

        if(i < nextSequenceIndex){
          ledOutOfSequence[i] = true;
        }

        nextSequenceIndex++;
      }
    }

    // Check if all LEDs have been seen individually
    bool allSeen = true;
    for(int i=0;i<numLeds;i++){
      if(!ledSeen[i]){
        allSeen = false;
        break;
      }
    }
    if(allSeen) break;

    delay(5);
  }

  // Print LED sequence and any errors
  Serial.println("LED sequence test finished. Results:");
  for(int i=0; i<numLeds; i++){
    Serial.print("LED ");
    Serial.print(i+1);
    if(!ledSeen[i]){
      Serial.println(" NEVER lit.");
    } else if(ledOutOfSequence[i]){
      Serial.println(" lit OUT OF SEQUENCE!");
    } else {
      Serial.println(" lit in sequence.");
    }
  }


  // Final summary
  bool anyIssue = false;
  for(int i=0; i<numLeds; i++){
    if(!ledSeen[i] || ledOutOfSequence[i]){
      anyIssue = true;
      break;
    }
  }

  if(!anyIssue){
    Serial.println("All lights work as expected.");
  } else {
    Serial.println("There were issues with some LEDs. Check for shorts or sequence errors.");
  }

  Serial.println("End of Test.");
}
