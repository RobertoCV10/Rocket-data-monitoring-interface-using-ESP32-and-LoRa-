// main.cpp
#include "cohete.h"

// Pines I2C y GPS
#define I2C_SDA 11
#define I2C_SCL 12
#define RXPin 2
#define TXPin 1

Cohete cohete(I2C_SDA, I2C_SCL, RXPin, TXPin);
DataLogger logger;

void setup() {
    Serial.begin(115200);
    logger.begin();
    cohete.setLogger(&logger);
    cohete.begin();
}

void loop() {
    cohete.update();
}
