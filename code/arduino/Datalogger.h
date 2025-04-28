#ifndef DATALOGGER_H
#define DATALOGGER_H

#include <Arduino.h>
#include "FS.h"
#include "SD_MMC.h"

class DataLogger {
public:
    DataLogger();

    bool begin();  // Inicializa la tarjeta SD y el archivo de registro
    void logHeader();  // Registra el encabezado del archivo CSV
    void logData(
        float accX, float accY, float accZ,
        float angleX, float angleY, float angleZ,
        float tempHT, float humHT, float pressureBMP280, float altBMP280,
        float azimuthQMC,
        float pressureBMP180, float altBMP180,
        double latitude, double longitude
    );  // Registra los datos en el archivo CSV

private:
    String generateUniqueFilename();  // Genera un nombre de archivo único
    bool sdReady;  // Indica si la tarjeta SD está lista
    String filename;  // Nombre del archivo donde se registrarán los datos
};

#endif
