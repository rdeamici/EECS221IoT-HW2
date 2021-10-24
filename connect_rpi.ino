#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Trinh's wifi and password
const char* ssid = "SETUP-564E-5"; 
const char* password = "butler69"; 

// setup wifi
WiFiUDP Udp; 
unsigned int ESPUdpPort = 4210; // local port to listen on
unsigned int RPiUdpPort = 4210;

char incomingPacket[255]; // buffer for incoming packets
 // a reply string to send back
char replyPacket[] = "Hi there! Got the message :-)";

//set pin numbers
const int BlueledPin = D0;
const int GreenledPin = D1;
const int RedledPin = D2;
const int ldrPin = A0;

float checkCurrentLightLevel() {
    int ldrStatus = analogRead(ldrPin);  //read the state of the LDR value
    delay(250);
    return ldrStatus;
}



void setup() {
    // set pin modes
    pinMode(BlueledPin, OUTPUT);
    pinMode(GreenledPin, OUTPUT);
    pinMode(RedledPin, OUTPUT);
    pinMode(ldrPin, INPUT);

    // ensure all lights are off
    Serial.begin(115200);
    digitalWrite(RedledPin,LOW);
    digitalWrite(GreenledPin,LOW);
    digitalWrite(BlueledPin,LOW);

    bool connected = false;
    // blink light for 2 seconds
    // while trying to connect to wifi
    Serial.println();

    Serial.printf("Connecting to %s ", ssid); 
    WiFi.begin(ssid, password); 
    for(int i = 0; i < 10; i++) {
        digitalWrite(RedledPin,HIGH);
        time.sleep(50);
        digitalWrite(RedledPin,LOW);
        time.sleep(50);
        if ( WiFi.status() != WL_CONNECTED) {
            Serial.printf(".");
            
            // ensure loop continues until wifi connection established
            if ( i == 9 )
                i--;
        }
        else if (! connected) {
            Serial.println(" connected"); 
            connected = true;
        }
    }

    // setup server
    Udp.begin(ESPUdpPort); 
    Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), ESPUdpPort); 
    digitalWrite(RedledPin, HIGH);
}

void loop() {
    // read sensor (0.25 seconds)
    int lightLvl = checkCurrentLightLevel();
    // convert int to char *
    String msg2rpi = String(lightLvl)
    // send data to the IP address of the RPi
    Udp.beginPacket('192.168.0.16', RPiUdpPort); 
    Udp.write(msg2rpi.c_str()); //convert msg to c-style char array
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
        Serial.prinln(incomingPacket);

    } 
}