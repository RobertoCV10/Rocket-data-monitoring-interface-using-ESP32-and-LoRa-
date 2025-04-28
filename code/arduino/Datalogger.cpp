#include "DataLogger.h"
#include <Arduino.h>

DataLogger::DataLogger() : sdReady(false) {}

bool DataLogger::begin() {
    // Pines personalizados
    #define SD_MMC_CMD 38
    #define SD_MMC_CLK 39
    #define SD_MMC_D0  40

    SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
    if (!SD_MMC.begin("/sdcard", true)) {
        Serial.println("[SD] ERROR: No se pudo montar la tarjeta SD.");
        sdReady = false;
        return false;
    }
    Serial.println("[SD] Tarjeta SD montada correctamente.");

    filename = generateUniqueFilename();
    File file = SD_MMC.open(filename.c_str(), FILE_WRITE);
    if (file) {
        logHeader();
        file.close();
        Serial.print("[SD] Archivo creado: ");
        Serial.println(filename);
        sdReady = true;
    } else {
        Serial.println("[SD] ERROR: No se pudo crear el archivo.");
        sdReady = false;
    }

    return sdReady;
}

String DataLogger::generateUniqueFilename() {
    int index = 1;
    String uniqueFilename;
    do {
        uniqueFilename = "/VUELO" + String(index) + ".csv";
        index++;
    } while (SD_MMC.exists(uniqueFilename));
    return uniqueFilename;
}

void DataLogger::logHeader() {
    if (!sdReady) return;
    File file = SD_MMC.open(filename.c_str(), FILE_APPEND);
    if (file) {
        file.println("AccX,AccY,AccZ,AngX,AngY,AngZ,T_AHT20,H_AHT20,P_BMP280,A_BMP280,Azimut,P_BMP180,A_BMP180,Lat,Lng");
        file.close();
    }
}

void DataLogger::logData(
    float accX, float accY, float accZ,
    float angleX, float angleY, float angleZ,
    float tempHT, float humHT, float pressureBMP280, float altBMP280,
    float azimuthQMC,
    float pressureBMP180, float altBMP180,
    double latitude, double longitude
) {
    if (!sdReady) return;
    File file = SD_MMC.open(filename.c_str(), FILE_APPEND);
    if (file) {
        file.printf("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f\n",
                    accX, accY, accZ,
                    angleX, angleY, angleZ,
                    tempHT, humHT,
                    pressureBMP280, altBMP280,
                    azimuthQMC,
                    pressureBMP180, altBMP180,
                    latitude, longitude);
        file.close();
    }
}
