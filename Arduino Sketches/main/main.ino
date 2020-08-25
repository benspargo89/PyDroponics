
//***** Set up Flow Pins and define functions *****//
// Flow Sensor Pin
#define FLOWSENSORPIN 3
// count how many pulses!
volatile uint16_t pulses = 0;
// track the state of the pulse pin
volatile uint8_t lastflowpinstate;
// you can try to keep time of how long it is between pulses
volatile uint32_t lastflowratetimer = 0;
// and use that to calculate a flow rate
volatile float flowrate;
// Interrupt is called once a millisecond, looks for any pulses from the sensor!
SIGNAL(TIMER0_COMPA_vect) {
  uint8_t x = digitalRead(FLOWSENSORPIN);
  
  if (x == lastflowpinstate) {
    lastflowratetimer++;
    return; // nothing changed!
  }
  
  if (x == HIGH) {
    //low to high transition!
    pulses++;
  }
  lastflowpinstate = x;
  flowrate = 1000.0;
  flowrate /= lastflowratetimer;  // in hertz
  lastflowratetimer = 0;
}

void useInterrupt(boolean v) {
  if (v) {
    // Timer0 is already used for millis() - we'll just interrupt somewhere
    // in the middle and call the "Compare A" function above
    OCR0A = 0xAF;
    TIMSK0 |= _BV(OCIE0A);
  } else {
    // do not call the interrupt function COMPA anymore
    TIMSK0 &= ~_BV(OCIE0A);
  }
}

//***** Set up Temperature Pins *****//
#include "DHT.h"
#define DHTPIN 2     
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHTPIN, DHTTYPE);



void setup() {
   //Setup Flowrate sensors   
   Serial.begin(9600);
   Serial.print("Flow sensor test!"); 
   pinMode(FLOWSENSORPIN, INPUT);
   digitalWrite(FLOWSENSORPIN, HIGH);
   lastflowpinstate = digitalRead(FLOWSENSORPIN);
   useInterrupt(true);

   //Setup Temperature Sensors
   dht.begin();
   
}

void loop()                     // run over and over again
{ 
  delay(2000);
  float liters = pulses;
  liters /= 7.5;
  liters /= 60.0;  
  float h = dht.readHumidity();
  float f = dht.readTemperature(true);
  if (isnan(h) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  //Serial.print("Freq: "); Serial.println(flowrate);
  //Serial.print("Pulses: "); Serial.println(pulses, DEC);
  Serial.print("Liters:");Serial.print(liters); 
  Serial.print(F(" Humidity:"));
  Serial.print(h);
  Serial.print(F("%  Temperature:"));
  Serial.print(f);
  Serial.println(F("°F"));  
  liters = 0;
  pulses = 0;
  flowrate = 0;  
}
