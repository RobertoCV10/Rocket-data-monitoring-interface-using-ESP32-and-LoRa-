#ifndef COHETE_H
#define COHETE_H

#include <Wire.h>
#include <MPU6050_light.h>
#include <Adafruit_BMP085.h>
#include <QMC5883LCompass.h>
#include <Adafruit_AHTX0.h>
#include <BMP280.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include "FS.h"
#include "SD_MMC.h"
#include "DataLogger.h"

class Cohete {
public:
    Cohete(uint8_t sda, uint8_t scl, uint8_t rxPin, uint8_t txPin);

    void begin();
    void update();
    void setLogger(DataLogger* logger);  // Método para asignar el logger

private:
    void tcaSelect(uint8_t i);

    void setupMPU6050();
    void setupAHT20_BMP280();
    void setupQMC5883L();
    void setupBMP180();
    void setupGPS();

    void readMPU6050();
    void readAHT20_BMP280();
    void readQMC5883L();
    void readBMP180();
    void readGPS();

    const uint8_t MUX_Address = 0x70;
    uint8_t SDA_PIN;
    uint8_t SCL_PIN;
    uint8_t RXPin;
    uint8_t TXPin;

    MPU6050 mpu;
    Adafruit_BMP085 bmp;
    QMC5883LCompass compass;
    Adafruit_AHTX0 aht20;
    BMP280 bmp280;
    TinyGPSPlus gps;
    SoftwareSerial ss;

    DataLogger* logger;  // Instancia del logger

    unsigned long previousMillis;
    const unsigned long interval = 200;
    float basePressure = 101320.0;
    float calcularAlturaRelativa(float presionActual, float presionBase);
};

#endif
