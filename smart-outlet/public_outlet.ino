#include <SPI.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <ESP8266WiFi.h>
#include <ACROBOTIC_SSD1306.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>


//http.setTimeout(1000);

int httpCode;
DynamicJsonBuffer jsonBuffer(200);
String payload;

//GPIO pins
const int relayPin = 16;
const int currentSensor = A0;

//values needed for energyDraw
int maxValue;
unsigned long time1;
unsigned long time2;
int adcRead;
float currentRMS;
float energyDraw;

//values 
float totalEnergyUsed;
float currentEnergyUse;
float energyLeft;
int timeRemaining;
int timeInit;
int timeElapsed;
float energySinceLastUpdate = 0;
int lastTime = 0;
int countZeros = 0;

//states
boolean authorized = false;
boolean relayOn = false;

//NFC chip
#define PN532_SCK  (14)
#define PN532_MOSI (13)
#define PN532_SS   (2)
#define PN532_MISO (12)
#define PN532_RESET (15)
Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

//NFC Card
uint8_t success;
uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)

//energyDraw Calculation function
float getEnergyDraw() {
  maxValue = 0;
  time1 = millis();
  time2 = time1;
  while (time2 - time1 < 200) {
    adcRead = analogRead(currentSensor);;
    if (adcRead > maxValue) {
      maxValue = adcRead;
    }
    time2 = millis();
  }
  if (maxValue < 10) {
    maxValue = 0;
  }
  currentRMS = ((float(maxValue)/1024)/200)*.707*1000;
  energyDraw = (currentRMS * 120 * .2) / 3600; //in Wh
  return energyDraw;

}


void setup() {
  Serial.begin(115200);

  //setup relay
  digitalWrite(relayPin, LOW);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  //setup NFC
  nfc.begin();
  while(1){
    uint32_t versiondata = nfc.getFirmwareVersion();
    if (versiondata) {
      break;
    }
  }
  nfc.SAMConfig();
  
  //set up i2c display
  Wire.begin();
  oled.init();
  oled.clearDisplay();

  //setup wifi
  WiFi.begin("Columbia University");
  //int seconds = 0;
  while (WiFi.status() != WL_CONNECTED) {
    oled.setTextXY(3,0);
    oled.putString("Connecting....");
    //seconds += 1;
    delay(100);
    //if (seconds == 50) {
      //ESP.reset();
    //}
  }
  String httpRequest;
  HTTPClient http;
  httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/use?signal=off&usage=0";
  http.begin(httpRequest);
  httpCode = http.GET();
  http.end();
  
}

void loop() {
  if (energyLeft == 0 and authorized) {
        digitalWrite(relayPin, LOW);
        authorized = false;
        oled.clearDisplay();
        oled.setTextXY(3,0);
        oled.putString("Disconnecting");
        String httpRequest;
        HTTPClient http;
        httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/use?signal=off&usage=0";
        http.begin(httpRequest);
        httpCode = http.GET();
        http.end();
        delay(1000);
        
        
  }
  if (!authorized) {
    oled.clearDisplay();
    oled.setTextXY(3,0);
    oled.putString("Waiting for NFC");
    //read NFC card
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
    while (1){
      if (success) {
        oled.clearDisplay();
        oled.setTextXY(3,0);
        oled.putString("Found NFC");
        oled.setTextXY(4,0);
        oled.putString("Authorizing");
        String httpRequest;
        HTTPClient http;
        httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/point?card_id=";
        for (int i = 0; i < uidLength; i++) {
           httpRequest += String(uid[i], HEX);
        }
        Serial.print(httpRequest);
        //authorizing...
        
        http.begin(httpRequest);
        Serial.print("[HTTP] GET...\n");
        // start connection and send HTTP header
        
        httpCode = http.GET();
  
        // httpCode will be negative on error
        if(httpCode > 0) {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] GET... code: %d\n", httpCode);
            // file found at server
            payload = http.getString();
        }
        http.end();   
        JsonObject& root1 = jsonBuffer.parseObject(payload);
        if (!root1.success()) {
          Serial.println(F("Parsing failed!"));
          oled.clearDisplay();
          oled.setTextXY(3,0);
          oled.putString("Try again");
          delay(1000); 
          
        }
        Serial.println(payload);
        delay(100);
        if (root1.containsKey("power_left")) {
          Serial.println("yes");
          authorized = true;
          energyLeft = root1["power_left"];
          oled.setTextXY(3,0);
          oled.putString("Unlocking relay");
          if (energyLeft > 0) {
            digitalWrite(relayPin, HIGH);
          }
          delay(1000);
          oled.clearDisplay();
          timeInit = millis();
          totalEnergyUsed = 0;
          energySinceLastUpdate = 0;
          
        }
        else {
          oled.clearDisplay();
          oled.setTextXY(3,0);
          oled.putString("Unauthorized");
          oled.setTextXY(4,0);
          oled.putString("Try again");
        delay(1000);
        }
        break;
      }
   }
}
  
  else {
    Serial.println("why not here");
    totalEnergyUsed += getEnergyDraw(); 
    if (lastTime != timeElapsed) {
      energySinceLastUpdate = totalEnergyUsed - energySinceLastUpdate;
      if (energySinceLastUpdate == 0) {
        countZeros+=1;
      }
      String httpRequest;
      HTTPClient http;
      if (energySinceLastUpdate >= 0){
        httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/use?usage=" + String(energySinceLastUpdate) + "&signal=on";
      } else {
        httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/use?usage=0&signal=off";
      }
      energySinceLastUpdate = totalEnergyUsed;
      http.begin(httpRequest);
      httpCode = http.GET();
      
      if(httpCode > 0) {
             // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] GET... code: %d\n", httpCode);
            // file found at server
            payload = http.getString();
            JsonObject& root = jsonBuffer.parseObject(payload);
            if (!root.success()) {
              Serial.println(("Parsing failed!"));
            }
            Serial.println(payload);
            if (root.containsKey("state")) {
              Serial.println("here");
              oled.clearDisplay();
              oled.setTextXY(3,0);
              oled.putString("Disconnecting");
              digitalWrite(relayPin, LOW);
              authorized = false;
              delay(1000);
            }
            else if (root.containsKey("remaining")) {
              energyLeft = root["remaining"];
              Serial.print(energyLeft);
              timeRemaining = root["time_remaining"];
              
            }
            
      }
  
      http.end();
      lastTime = timeElapsed;
    }
    if (countZeros == 10) {
      countZeros = 0;
      String httpRequest;
      HTTPClient http;
      httpRequest = "http://ec2-54-86-19-170.compute-1.amazonaws.com:8080/use?signal=off&usage=0";
      http.begin(httpRequest);
      httpCode = http.GET();
      oled.clearDisplay();
      oled.setTextXY(3,0);
      oled.putString("10 sec of no use");
      oled.setTextXY(4,0);
      oled.putString("Disconnecting");
      http.end();
      digitalWrite(relayPin, LOW);
      authorized = false;
      delay(1000);
    }
    
    if (authorized) {
      oled.setTextXY(0,0);
      oled.putString("Energy Consumed:");
      oled.setTextXY(1,0);
      oled.putString(String(totalEnergyUsed) + "Wh");
      timeElapsed = (millis() - timeInit)/1000;
   
      oled.setTextXY(3,0);
      oled.putString("Time remaining:");
      oled.setTextXY(4,0);
      oled.putString("~");
      oled.setTextXY(4,1);
      int hours = timeRemaining / 3600;
      int minutes = (timeRemaining % 3600) / 60;
      int sec = timeRemaining % 60;
      char buffer1[9];
      sprintf(buffer1, "%02d:%02d:%02d", hours, minutes, sec);
      oled.putString(buffer1);
      oled.setTextXY(6,0);
      oled.putString("Energy Left:");
      oled.setTextXY(7,0);
      oled.putString(String(energyLeft) + "Wh");
    }
  }
}
