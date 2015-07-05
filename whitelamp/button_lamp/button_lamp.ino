#include "LPD8806.h"
#include "SPI.h" // Comment out this line if using Trinket or Gemma
#ifdef __AVR_ATtiny85__
 #include <avr/power.h>
#endif

// Example to control LPD8806-based RGB LED Modules in a strip

/*****************************************************************************/

// Number of RGB LEDs in strand:
int nLEDs = 12;

// Chose 2 pins for output; can be any valid output pins:
int dataPin  = 2;
int clockPin = 3;

int controlPin = 5;
int input = 0;
int oldInput = 0;

// First parameter is the number of LEDs in the strand.  The LED strips
// are 32 LEDs per meter but you can extend or cut the strip.  Next two
// parameters are SPI data and clock pins:
LPD8806 strip = LPD8806(nLEDs, dataPin, clockPin);

// You can optionally use hardware SPI for faster writes, just leave out
// the data and clock pin parameters.  But this does limit use to very
// specific pins on the Arduino.  For "classic" Arduinos (Uno, Duemilanove,
// etc.), data = pin 11, clock = pin 13.  For Arduino Mega, data = pin 51,
// clock = pin 52.  For 32u4 Breakout Board+ and Teensy, data = pin B2,
// clock = pin B1.  For Leonardo, this can ONLY be done on the ICSP pins.
//LPD8806 strip = LPD8806(nLEDs);

void setup() {
  Serial.begin(9600);      // open the serial port at 9600 bps:
  // Start up the LED strip
  strip.begin();

  turnLightOff();
  
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000L)
  clock_prescale_set(clock_div_1); // Enable 16 MHz on Trinket
#endif  
}


void loop() {
  oldInput = input;
  input = digitalRead(controlPin);
  if (oldInput != input) {
    Serial.print(input);  
    if (input == HIGH) {
      turnLightOn();
    }
    else {
      turnLightOff();  
    }
  }    
}

void turnLightOn() {
  Serial.print("turn on");

  int i;
  for(i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, 255, 255, 150); // Set new pixel 'on'    
  }
  
  // Update the strip, to start they are all 'off'
  strip.show();    
}

void turnLightOff() {
  Serial.print("turn off");

  int i;
  for(i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, 0, 0, 0); // Set new pixel 'on'    
  }
  
  // Update the strip, to start they are all 'off'
  strip.show();    
}
