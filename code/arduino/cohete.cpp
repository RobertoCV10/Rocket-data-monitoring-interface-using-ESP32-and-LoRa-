#include "cohete.h"

Cohete::Cohete(uint8_t sda, uint8_t scl, uint8_t rxPin, uint8_t txPin)
    : SDA_PIN(sda), SCL_PIN(scl), RXPin(rxPin), TXPin(txPin), mpu(Wire), ss(rxPin, txPin), previousMillis(0), logger(nullptr) {}

void Cohete::begin() {
    Serial.begin(115200);
    Serial2.begin(115200, SERIAL_8N1, 18, 17);  // Puedes adaptar esto si deseas pasarlo como parámetro

    Wire.begin(SDA_PIN, SCL_PIN);

    setupMPU6050();
    setupAHT20_BMP280();
    setupQMC5883L();
    setupBMP180();
    setupGPS();

    // Si logger no es nulo, comenzamos a registrar los datos
    if (logger) {
        if (logger->begin()) {
            Serial.println("Logger iniciado.");
        } else {
            Serial.println("Error al iniciar el logger.");
        }
    }
}

void Cohete::setLogger(DataLogger* loggerInstance) {
    logger = loggerInstance;
}

void Cohete::tcaSelect(uint8_t i) {
    if (i > 7) return;
    Wire.beginTransmission(MUX_Address);
    Wire.write(1 << i);
    Wire.endTransmission();
}

void Cohete::setupMPU6050() {
    tcaSelect(0);
    if (mpu.begin() != 0) {
        Serial.println(F("Error: No se pudo conectar al MPU6050."));
        while (1);
    }
    Serial.println(F("Calculando offsets, no mover el MPU6050"));
    delay(1000);
    mpu.calcOffsets();
    Serial.println("MPU6050 listo!");
}

void Cohete::setupAHT20_BMP280() {
    tcaSelect(3);
    if (!aht20.begin()) {
        Serial.println("No se encontró el AHT20.");
        while (1);
    }
    Serial.println("AHT20 detectado.");
    bmp280.begin();
    Serial.println("BMP280 detectado.");

    delay(1000);  // Espera a que se estabilice
    basePressure = bmp280.getPressure();
    Serial.print("Presión base registrada: ");
    Serial.print(basePressure);
    Serial.println(" Pa");
}

float Cohete::calcularAlturaRelativa(float presionActual, float presionBase) {
    return 44330.0 * (1.0 - pow(presionActual / presionBase, 0.1903));
}

void Cohete::setupQMC5883L() {
    tcaSelect(6);
    compass.init();
    Serial.println("QMC5883L iniciado.");
    compass.read();
    if (compass.getAzimuth() == 0) {
        Serial.println("Advertencia: No se detecta el QMC5883L.");
    } else {
        Serial.println("QMC5883L listo para medir.");
    }
}

void Cohete::setupBMP180() {
    tcaSelect(7);
    if (!bmp.begin()) {
        Serial.println("No se encontró un sensor BMP085/BMP180.");
        while (1);
    }
    Serial.println("BMP180 detectado correctamente.");
}

void Cohete::setupGPS() {
    ss.begin(9600);
    Serial.println(F("Inicializando GPS..."));
}

/*
void Cohete::readMPU6050() {
    tcaSelect(0);
    mpu.update();

    float accX = mpu.getAccX();
    float accY = mpu.getAccY();
    float accZ = mpu.getAccZ();

    float angleX = mpu.getAngleX();
    float angleY = mpu.getAngleY();
    float angleZ = mpu.getAngleZ();

    char mensaje[200];
    
    sprintf(mensaje,
            "\tAX: %.2f\tAY: %.2f\tAZ: %.2f\tRoll(X): %.2f\tPitch(Y): %.2f\tYaw(Z): %.2f",
            accX, accY, accZ, angleX, angleY, angleZ);

    Serial.println(mensaje);
    Serial2.println(mensaje);

    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData(accX, accY, accZ, angleX, angleY, angleZ, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
}
*/

void Cohete::readMPU6050() {
  tcaSelect(0);
  mpu.update();

  float accX = mpu.getAccX();
  float accY = mpu.getAccY();
  float accZ = mpu.getAccZ();

  float angleX = mpu.getAngleX();
  float angleY = mpu.getAngleY();
  float angleZ = mpu.getAngleZ() + 0.09 ;

  char mensaje[50];
  sprintf(mensaje, " L2- S9=%.2f\t L2 -S8=%.2f", angleZ, accX);

  Serial.println(mensaje);
  Serial2.println(mensaje);

  // Registrar datos si el logger está activo
  if (logger) {
    logger->logData(accX, accY, accZ, angleX, angleY, angleZ, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
  }
}


/*
void Cohete::readAHT20_BMP280() {
    tcaSelect(3);
    sensors_event_t humidity, tempAHT;
    aht20.getEvent(&humidity, &tempAHT);

    float tempHT = tempAHT.temperature;
    float Rltvhdt = humidity.relative_humidity;
    float currentPressure = bmp280.getPressure();
    float relativeAltitude = calcularAlturaRelativa(currentPressure, basePressure);

    char mensaje[200];
    sprintf(mensaje,
            "\tT_AHT20: %.2f°C\tH_AHT20: %.2f%\tP_BMP280: %.2fPa\tA_BMP280: %.2f",
            tempHT, Rltvhdt, currentPressure, relativeAltitude);



    //Serial.println(mensaje);
    //Serial2.println(mensaje);



    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, tempHT, Rltvhdt, currentPressure, relativeAltitude, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
}
*/


void Cohete::readAHT20_BMP280() {
    tcaSelect(3);
    sensors_event_t humidity, tempAHT;
    aht20.getEvent(&humidity, &tempAHT);

    float tempHT = tempAHT.temperature;
    float Rltvhdt = humidity.relative_humidity;
    float currentPressure = bmp280.getPressure();
    float relativeAltitude = calcularAlturaRelativa(currentPressure, basePressure);

    char mensajeSerial[200];
    sprintf(mensajeSerial,
            "L2-S1=%.2f\t L2 -S2=%.2f\t L2 -S3=%.2f\t L2 -S4=%.2f",
            tempHT, Rltvhdt, currentPressure, relativeAltitude);

    Serial.println(mensajeSerial);
    Serial2.println(mensajeSerial);

    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, tempHT, Rltvhdt, currentPressure, relativeAltitude, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
}

/*
void Cohete::readQMC5883L() {
    tcaSelect(6);
    compass.read();

    float azimuth = compass.getAzimuth();

    char mensaje[100];
    sprintf(mensaje, "\tAzimut: %.2f", azimuth);



    Serial.println(mensaje);
    Serial2.println(mensaje);



    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, azimuth, 0.0, 0.0, 0.0, 0.0);
    }
}

*/

void Cohete::readQMC5883L() {
    tcaSelect(6);
    compass.read();

    float azimuth = compass.getAzimuth();

    char mensaje[100];
    sprintf(mensaje, "\t L2- S5=%.2f", azimuth);

    Serial.println(mensaje);
    Serial2.println(mensaje);

    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, azimuth, 0.0, 0.0, 0.0, 0.0);
    }
}

/*
void Cohete::readBMP180() {
    tcaSelect(7);

    float Patmbmp180 = bmp.readSealevelPressure();
    float ARbmp180 = bmp.readAltitude(101600);

    char mensaje[200];
    sprintf(mensaje,
            "P_atm: %.2fPa\tAltitud Real: %.2fm",
            Patmbmp180, ARbmp180);



    Serial.println(mensaje);
    Serial2.println(mensaje);



    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, Patmbmp180, ARbmp180, 0.0, 0.0);
    }
}
*/

void Cohete::readBMP180() {
    tcaSelect(7);

    float Patmbmp180 = bmp.readSealevelPressure();
    float ARbmp180 = bmp.readAltitude(101600);

    char mensaje[200];
    sprintf(mensaje,
            "\t L2- S6:%.2f\t L2- S7:%.2f",
            Patmbmp180, ARbmp180);

    Serial.println(mensaje);
    Serial2.println(mensaje);

    // Registrar datos si el logger está activo
    if (logger) {
        logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, Patmbmp180, ARbmp180, 0.0, 0.0);
    }
}

/*
void Cohete::readGPS() {
    static bool gpsWorking = true;
    char mensaje[100];

    while (ss.available() > 0) {
        if (gps.encode(ss.read())) {
            if (gps.location.isValid()) {
                double lat = gps.location.lat();
                double lng = gps.location.lng();



                sprintf(mensaje, "Lat: %.6f , long: %.6f", lat, lng);
                //Serial.println(mensaje);
                //Serial2.println(mensaje);



                // Registrar datos si el logger está activo
                if (logger) {
                    logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, lat, lng);
                }

                gpsWorking = true;
            } else {
                Serial.println(F("GPS: Location INVALID"));
                Serial2.println(F("GPS: Location INVALID"));
                gpsWorking = false;
            }
        }
    }

    if (millis() > 5000 && gps.charsProcessed() < 10 && gpsWorking) {
        Serial.println(F("GPS no responde, revisa el cableado o el fix."));
        Serial2.println(F("GPS no responde."));
        gpsWorking = false;
    }
}
*/

void Cohete::readGPS() {
    static bool gpsWorking = true;
    char mensaje[100];

    while (ss.available() > 0) {
        if (gps.encode(ss.read())) {
            if (gps.location.isValid()) {
                double lat = gps.location.lat();
                double lng = gps.location.lng();

                sprintf(mensaje, "\t L2- S10:%.6f , %.6f", lat, lng);

                Serial.println(mensaje);
                Serial2.println(mensaje);

                // Registrar datos si el logger está activo
                if (logger) {
                    logger->logData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, lat, lng);
                }

                gpsWorking = true;
            } else {
                Serial.println(F("GPS: Location INVALID"));
                Serial2.println(F("GPS: Location INVALID"));
                gpsWorking = false;
            }
        }
    }

    if (millis() > 5000 && gps.charsProcessed() < 10 && gpsWorking) {
        Serial.println(F("GPS no responde, revisa el cableado o el fix."));
        Serial2.println(F("GPS no responde."));
        gpsWorking = false;
    }
}


void Cohete::update() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        readMPU6050();
        readAHT20_BMP280();
        readQMC5883L();
        readBMP180();
        readGPS();
    }
}
