#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// wifi info
const char* SSID = "OnePlusHotSpot"; 
const char* PASSWORD = "Ucl4r00lz!"; 

// raspberry pi IP address
String RPi_address = "192.168.220.8"

unsigned int ESPUdpPort = 4210; // local port to listen on
unsigned int RPiUdpPort = 4210; // port to send info to rpi

char incomingPacket[UDP_TX_PACKET_MAX_SIZE + 1]; // buffer for incoming packets
char replyPacket[] = "Hi there! Got the message :-)";

WiFiUDP Udp; 

//set pin numbers
const int BlueledPin = D0;
const int GreenledPin = D1;
const int RedledPin = D2;
const int ldrPin = A0;


void setup() {
  Serial.begin(115200);
  // set pin modes
  pinMode(BlueledPin, OUTPUT);
  pinMode(GreenledPin, OUTPUT);
  pinMode(RedledPin, OUTPUT);
  pinMode(ldrPin, INPUT);

  // blink light for 2 seconds
  // while trying to connect to wifi
  WiFi.begin(SSID, PASSWORD); 
  Serial.print("Connecting to %s ");
  Serial.println(SSID);

  bool connected = false;

  for(int i = 0; i < 10; i++) {
    digitalWrite(RedledPin,HIGH);
    delay(50);
    digitalWrite(RedledPin,LOW);
    delay(50);
    if ( WiFi.status() != WL_CONNECTED) {
      Serial.print('.');
      // ensure loop continues until wifi connection established
      if ( i == 9 )
        i--;
    }
    else if (! connected) {
      Serial.println(" connected!"); 
      connected = true;
    }
  }
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // ensure all lights are off
  digitalWrite(RedledPin,LOW);
  digitalWrite(GreenledPin,LOW);
  digitalWrite(BlueledPin,LOW);

  // setup client
  Udp.begin(ESPUdpPort); 
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), ESPUdpPort); 
  digitalWrite(RedledPin, HIGH);
}


int checkCurrentLightLevel() {
    int ldrStatus = analogRead(ldrPin);  //read the state of the LDR value
    delay(250);
    return ldrStatus;
}


void loop() {
    // read sensor (0.25 seconds)
    int lightLvl = checkCurrentLightLevel();

    // convert int to char *
    String msg2rpi = String(lightLvl).c_str();

    // send data to the IP address of the RPi
    Serial.print("light level: ");
    Serial.println(lightLvl);
    Serial.println("Sending to rpi");
    Udp.beginPacket(RPi_address, RPiUdpPort); 
    Udp.write(msg2rpi); //convert msg to c-style char array
    Udp.endPacket();
 
    // attempt to receive incoming UDP packet from rpi
    int packetSize = Udp.parsePacket(); 
    if(packetSize) { 
        Serial.printf("Received %d bytes from %s, port %d\n", packetSize, 
            Udp.remoteIP().toString().c_str(), Udp.remotePort()); 

        int len = Udp.read(incomingPacket, 255); 
        if(len > 0) { 
            incomingPacket[len] = '\0';
        }
        Serial.println("UDP packet contents: ");
        Serial.println(incomingPacket);
        
        int light_to_turn_on = incomingPacket[0];
        if (light_to_turn_on == 0) {
          digitalWrite(GreenledPin,HIGH);
          digitalWrite(BlueledPin,LOW);
        } else {
          digitalWrite(BlueledPin,HIGH);
          digitalWrite(GreenledPin,LOW);
        }
    }
    else {
        Serial.println("No UDP packet retrieved!");
    }
    delay(1000);
}