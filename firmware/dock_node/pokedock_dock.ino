/*
PokéDock Dock Node — ESP32-C3 Arduino scaffold
Libraries:
- Adafruit PN532
- Adafruit VL53L0X
- BH1750
- Adafruit NeoPixel
ESP-NOW is built into ESP32 Arduino core.
*/
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <esp_now.h>
#include <Adafruit_PN532.h>
#include <Adafruit_VL53L0X.h>
#include <BH1750.h>
#include <Adafruit_NeoPixel.h>

#ifndef SDA_PIN
#define SDA_PIN 8
#endif
#ifndef SCL_PIN
#define SCL_PIN 9
#endif
#ifndef LED_PIN
#define LED_PIN 2
#endif
#define LED_COUNT 8

Adafruit_PN532 nfc(-1, -1, &Wire);
Adafruit_VL53L0X lox;
BH1750 lightMeter;
Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

enum Flags : uint16_t {
  PHONE_PRESENT = 1u<<0,
  NFC_PRESENT   = 1u<<1,
  DARK          = 1u<<2,
  NODE_OK       = 1u<<3,
};

struct __attribute__((packed)) DockPacket {
  uint32_t magic;
  uint32_t seq;
  uint16_t flags;
  uint16_t lux_x10;
  uint16_t distance_mm;
  uint16_t pokemon_id;
  uint32_t uid_hash;
};

uint8_t HMI_MAC[6] = {0,0,0,0,0,0}; // EDIT after first HMI boot
uint32_t seqNo = 0;
bool docked = false;
uint32_t lastSend=0;

uint32_t fnv1a(const uint8_t* d, size_t n){
  uint32_t h=2166136261u;
  for(size_t i=0;i<n;i++){ h ^= d[i]; h *= 16777619u; }
  return h;
}

uint16_t mapUidToPokemon(uint32_t uidHash){
  // Replace with learned hashes after tag enrollment.
  // Return 0 = unknown.
  return 0;
}

void setTheme(uint16_t pokemonId){
  uint32_t c = pixels.Color(120,120,120);
  if(pokemonId==417) c=pixels.Color(80,150,255);
  else if(pokemonId==94) c=pixels.Color(100,45,160);
  else if(pokemonId==448)c=pixels.Color(40,90,180);
  else if(pokemonId==175)c=pixels.Color(255,180,140);
  for(int i=0;i<LED_COUNT;i++) pixels.setPixelColor(i,c);
  pixels.setBrightness(50);
  pixels.show();
}

void setup(){
  Serial.begin(115200);
  Wire.begin(SDA_PIN,SCL_PIN);
  pixels.begin(); pixels.clear(); pixels.show();

  bool okLux=lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  bool okToF=lox.begin();
  bool okNfc=nfc.begin();

  if(okNfc){
    uint32_t v=nfc.getFirmwareVersion();
    if(v) nfc.SAMConfig();
    else okNfc=false;
  }

  WiFi.mode(WIFI_STA);
  Serial.print("Dock MAC: "); Serial.println(WiFi.macAddress());
  if(esp_now_init()!=ESP_OK) Serial.println("ESP-NOW init fail");

  esp_now_peer_info_t peer{};
  memcpy(peer.peer_addr,HMI_MAC,6);
  peer.channel=0; peer.encrypt=false;
  esp_now_add_peer(&peer);

  Serial.printf("Sensors lux=%d tof=%d nfc=%d\n",okLux,okToF,okNfc);
}

void loop(){
  static float lux=100;
  static uint16_t dist=999;
  static uint16_t pokemon=0;
  static uint32_t uidHash=0;
  static bool nfcPresent=false;

  float l=lightMeter.readLightLevel();
  if(l>=0) lux = 0.8f*lux + 0.2f*l;

  VL53L0X_RangingMeasurementData_t m;
  lox.rangingTest(&m,false);
  if(m.RangeStatus!=4) dist=(uint16_t)m.RangeMilliMeter;

  if(!docked && dist<90) docked=true;
  if(docked && dist>130) docked=false;

  uint8_t uid[7]; uint8_t uidLen=0;
  if(nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A,uid,&uidLen,20)){
    uidHash=fnv1a(uid,uidLen);
    pokemon=mapUidToPokemon(uidHash);
    nfcPresent=true;
  } else {
    nfcPresent=false;
    pokemon=0;
  }

  if(millis()-lastSend>500){
    DockPacket p{};
    p.magic=0x504F4B45;
    p.seq=seqNo++;
    p.flags=NODE_OK | (docked?PHONE_PRESENT:0) | (nfcPresent?NFC_PRESENT:0) | (lux<8?DARK:0);
    p.lux_x10=(uint16_t)constrain((int)(lux*10),0,65535);
    p.distance_mm=dist;
    p.pokemon_id=pokemon;
    p.uid_hash=uidHash;
    esp_now_send(HMI_MAC,(uint8_t*)&p,sizeof(p));
    lastSend=millis();
  }

  if(nfcPresent && pokemon) setTheme(pokemon);
  else if(docked) setTheme(417);
  else if(lux<8) setTheme(94);

  delay(50);
}