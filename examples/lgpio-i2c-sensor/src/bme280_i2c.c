#include <stdio.h>
#include <stdlib.h>
#include <lgpio.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>

// BME280 I2C Configuration
#define I2C_BUS 1               // /dev/i2c-1 (default I2C bus on Raspberry Pi)
#define BME280_ADDR_PRIMARY 0x76   // Primary I2C address (SDO to GND)
#define BME280_ADDR_SECONDARY 0x77 // Secondary I2C address (SDO to VDD)

// BME280 Register Addresses
#define BME280_REG_ID           0xD0
#define BME280_REG_RESET        0xE0
#define BME280_REG_CTRL_HUM     0xF2
#define BME280_REG_STATUS       0xF3
#define BME280_REG_CTRL_MEAS    0xF4
#define BME280_REG_CONFIG       0xF5
#define BME280_REG_PRESS_MSB    0xF7
#define BME280_REG_TEMP_MSB     0xFA
#define BME280_REG_HUM_MSB      0xFD

// Calibration data registers
#define BME280_REG_CALIB_00     0x88
#define BME280_REG_CALIB_26     0xE1

// BME280 chip ID
#define BME280_CHIP_ID          0x60

// Measurement settings
#define BME280_OVERSAMPLING_1X  0x01
#define BME280_OVERSAMPLING_2X  0x02
#define BME280_OVERSAMPLING_4X  0x03
#define BME280_OVERSAMPLING_8X  0x04
#define BME280_OVERSAMPLING_16X 0x05

#define BME280_MODE_SLEEP       0x00
#define BME280_MODE_FORCED      0x01
#define BME280_MODE_NORMAL      0x03

// Calibration data structure
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
} bme280_calib_data;

// Global calibration data and t_fine (needed for compensation)
static bme280_calib_data calib;
static int32_t t_fine;

/**
 * Read a single byte from I2C register
 */
int i2c_read_byte(int h, uint8_t reg, uint8_t *value) {
    int result = lgI2cReadByteData(h, reg);
    if (result < 0) {
        return result;
    }
    *value = (uint8_t)result;
    return 0;
}

/**
 * Write a single byte to I2C register
 */
int i2c_write_byte(int h, uint8_t reg, uint8_t value) {
    return lgI2cWriteByteData(h, reg, value);
}

/**
 * Read multiple bytes from I2C register
 */
int i2c_read_block(int h, uint8_t reg, uint8_t *buffer, int count) {
    return lgI2cReadI2CBlockData(h, reg, (char *)buffer, count);
}

/**
 * Read BME280 calibration data
 */
int bme280_read_calibration(int h) {
    uint8_t calib_data[32];

    // Read calibration data part 1 (0x88-0x9F)
    if (i2c_read_block(h, BME280_REG_CALIB_00, calib_data, 24) < 0) {
        fprintf(stderr, "Failed to read calibration data part 1\n");
        return -1;
    }

    // Read calibration data part 2 (0xE1-0xE7)
    if (i2c_read_block(h, BME280_REG_CALIB_26, &calib_data[24], 7) < 0) {
        fprintf(stderr, "Failed to read calibration data part 2\n");
        return -1;
    }

    // Parse calibration data
    calib.dig_T1 = (calib_data[1] << 8) | calib_data[0];
    calib.dig_T2 = (calib_data[3] << 8) | calib_data[2];
    calib.dig_T3 = (calib_data[5] << 8) | calib_data[4];

    calib.dig_P1 = (calib_data[7] << 8) | calib_data[6];
    calib.dig_P2 = (calib_data[9] << 8) | calib_data[8];
    calib.dig_P3 = (calib_data[11] << 8) | calib_data[10];
    calib.dig_P4 = (calib_data[13] << 8) | calib_data[12];
    calib.dig_P5 = (calib_data[15] << 8) | calib_data[14];
    calib.dig_P6 = (calib_data[17] << 8) | calib_data[16];
    calib.dig_P7 = (calib_data[19] << 8) | calib_data[18];
    calib.dig_P8 = (calib_data[21] << 8) | calib_data[20];
    calib.dig_P9 = (calib_data[23] << 8) | calib_data[22];

    calib.dig_H1 = calib_data[24];
    calib.dig_H2 = (calib_data[26] << 8) | calib_data[25];
    calib.dig_H3 = calib_data[27];
    calib.dig_H4 = (calib_data[28] << 4) | (calib_data[29] & 0x0F);
    calib.dig_H5 = (calib_data[30] << 4) | ((calib_data[29] >> 4) & 0x0F);
    calib.dig_H6 = calib_data[31];

    return 0;
}

/**
 * Compensate temperature reading (from BME280 datasheet)
 */
float bme280_compensate_temperature(int32_t adc_T) {
    int32_t var1, var2;

    var1 = ((((adc_T >> 3) - ((int32_t)calib.dig_T1 << 1))) * ((int32_t)calib.dig_T2)) >> 11;
    var2 = (((((adc_T >> 4) - ((int32_t)calib.dig_T1)) * ((adc_T >> 4) - ((int32_t)calib.dig_T1))) >> 12) * ((int32_t)calib.dig_T3)) >> 14;

    t_fine = var1 + var2;

    float T = (t_fine * 5 + 128) >> 8;
    return T / 100.0;
}

/**
 * Compensate pressure reading (from BME280 datasheet)
 */
float bme280_compensate_pressure(int32_t adc_P) {
    int64_t var1, var2, p;

    var1 = ((int64_t)t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)calib.dig_P6;
    var2 = var2 + ((var1 * (int64_t)calib.dig_P5) << 17);
    var2 = var2 + (((int64_t)calib.dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)calib.dig_P3) >> 8) + ((var1 * (int64_t)calib.dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)calib.dig_P1) >> 33;

    if (var1 == 0) {
        return 0;  // Avoid division by zero
    }

    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)calib.dig_P8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (((int64_t)calib.dig_P7) << 4);

    return (float)p / 256.0 / 100.0;  // Convert to hPa
}

/**
 * Compensate humidity reading (from BME280 datasheet)
 */
float bme280_compensate_humidity(int32_t adc_H) {
    int32_t v_x1_u32r;

    v_x1_u32r = (t_fine - ((int32_t)76800));
    v_x1_u32r = (((((adc_H << 14) - (((int32_t)calib.dig_H4) << 20) - (((int32_t)calib.dig_H5) * v_x1_u32r)) +
                   ((int32_t)16384)) >> 15) * (((((((v_x1_u32r * ((int32_t)calib.dig_H6)) >> 10) *
                   (((v_x1_u32r * ((int32_t)calib.dig_H3)) >> 11) + ((int32_t)32768))) >> 10) + ((int32_t)2097152)) *
                   ((int32_t)calib.dig_H2) + 8192) >> 14));
    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * ((int32_t)calib.dig_H1)) >> 4));
    v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r);
    v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r);

    return (float)(v_x1_u32r >> 12) / 1024.0;
}

/**
 * Initialize BME280 sensor
 */
int bme280_init(int h) {
    uint8_t chip_id;

    // Read and verify chip ID
    if (i2c_read_byte(h, BME280_REG_ID, &chip_id) < 0) {
        fprintf(stderr, "Failed to read chip ID\n");
        return -1;
    }

    if (chip_id != BME280_CHIP_ID) {
        fprintf(stderr, "Invalid chip ID: 0x%02X (expected 0x%02X)\n", chip_id, BME280_CHIP_ID);
        return -1;
    }

    // Soft reset
    if (i2c_write_byte(h, BME280_REG_RESET, 0xB6) < 0) {
        fprintf(stderr, "Failed to reset sensor\n");
        return -1;
    }

    usleep(10000);  // Wait 10ms for reset to complete

    // Read calibration data
    if (bme280_read_calibration(h) < 0) {
        return -1;
    }

    // Configure sensor
    // Humidity oversampling x1
    if (i2c_write_byte(h, BME280_REG_CTRL_HUM, BME280_OVERSAMPLING_1X) < 0) {
        fprintf(stderr, "Failed to configure humidity\n");
        return -1;
    }

    // Temperature oversampling x1, Pressure oversampling x1, Normal mode
    uint8_t ctrl_meas = (BME280_OVERSAMPLING_1X << 5) | (BME280_OVERSAMPLING_1X << 2) | BME280_MODE_NORMAL;
    if (i2c_write_byte(h, BME280_REG_CTRL_MEAS, ctrl_meas) < 0) {
        fprintf(stderr, "Failed to configure measurement\n");
        return -1;
    }

    // Config: standby 1000ms, filter off
    if (i2c_write_byte(h, BME280_REG_CONFIG, 0xA0) < 0) {
        fprintf(stderr, "Failed to configure timing\n");
        return -1;
    }

    return 0;
}

/**
 * Read sensor data
 */
int bme280_read_data(int h, float *temperature, float *pressure, float *humidity) {
    uint8_t data[8];

    // Read all sensor data (0xF7-0xFE)
    if (i2c_read_block(h, BME280_REG_PRESS_MSB, data, 8) < 0) {
        fprintf(stderr, "Failed to read sensor data\n");
        return -1;
    }

    // Parse raw data
    int32_t adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
    int32_t adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4);
    int32_t adc_H = (data[6] << 8) | data[7];

    // Compensate readings
    *temperature = bme280_compensate_temperature(adc_T);
    *pressure = bme280_compensate_pressure(adc_P);
    *humidity = bme280_compensate_humidity(adc_H);

    return 0;
}

/**
 * Scan I2C bus for BME280 sensor
 */
int scan_for_bme280(int *addr) {
    int h;
    uint8_t chip_id;

    // Try primary address
    printf("Scanning for BME280 at address 0x%02X...\n", BME280_ADDR_PRIMARY);
    h = lgI2cOpen(I2C_BUS, BME280_ADDR_PRIMARY, 0);
    if (h >= 0) {
        if (i2c_read_byte(h, BME280_REG_ID, &chip_id) >= 0 && chip_id == BME280_CHIP_ID) {
            lgI2cClose(h);
            *addr = BME280_ADDR_PRIMARY;
            printf("BME280 found at address 0x%02X\n", BME280_ADDR_PRIMARY);
            return 0;
        }
        lgI2cClose(h);
    }

    // Try secondary address
    printf("Scanning for BME280 at address 0x%02X...\n", BME280_ADDR_SECONDARY);
    h = lgI2cOpen(I2C_BUS, BME280_ADDR_SECONDARY, 0);
    if (h >= 0) {
        if (i2c_read_byte(h, BME280_REG_ID, &chip_id) >= 0 && chip_id == BME280_CHIP_ID) {
            lgI2cClose(h);
            *addr = BME280_ADDR_SECONDARY;
            printf("BME280 found at address 0x%02X\n", BME280_ADDR_SECONDARY);
            return 0;
        }
        lgI2cClose(h);
    }

    printf("ERROR: BME280 not found on I2C bus %d\n", I2C_BUS);
    return -1;
}

int main() {
    int h;
    int addr;
    float temperature, pressure, humidity;

    printf("BME280 I2C Sensor Example (lgpio framework)\n");
    printf("============================================\n\n");

    // Scan for sensor
    if (scan_for_bme280(&addr) < 0) {
        fprintf(stderr, "\nTroubleshooting:\n");
        fprintf(stderr, "1. Enable I2C: sudo raspi-config -> Interface Options -> I2C\n");
        fprintf(stderr, "2. Check I2C device exists: ls -l /dev/i2c*\n");
        fprintf(stderr, "3. Check wiring: VDD->3.3V, GND->GND, SDA->GPIO2, SCL->GPIO3\n");
        fprintf(stderr, "4. Scan I2C bus: i2cdetect -y 1\n");
        fprintf(stderr, "5. Install i2c-tools: sudo apt install i2c-tools\n");
        return 1;
    }

    // Open I2C device
    printf("\nOpening I2C device %d at address 0x%02X...\n", I2C_BUS, addr);
    h = lgI2cOpen(I2C_BUS, addr, 0);
    if (h < 0) {
        fprintf(stderr, "Failed to open I2C device: %d\n", h);
        fprintf(stderr, "\nCheck permissions: sudo chmod 666 /dev/i2c-%d\n", I2C_BUS);
        return 1;
    }
    printf("I2C device opened successfully (handle: %d)\n", h);

    // Initialize sensor
    printf("Initializing BME280 sensor...\n");
    if (bme280_init(h) < 0) {
        lgI2cClose(h);
        return 1;
    }
    printf("Sensor initialized successfully\n\n");

    printf("BME280 Configuration:\n");
    printf("  - Temperature: 1x oversampling\n");
    printf("  - Pressure: 1x oversampling\n");
    printf("  - Humidity: 1x oversampling\n");
    printf("  - Mode: Normal (continuous)\n");
    printf("  - Standby: 1000ms\n\n");

    printf("Reading sensor data 10 times...\n");
    printf("Press Ctrl+C to exit\n\n");

    // Read sensor 10 times
    for (int i = 0; i < 10; i++) {
        if (bme280_read_data(h, &temperature, &pressure, &humidity) < 0) {
            fprintf(stderr, "Failed to read sensor data\n");
            continue;
        }

        printf("=== Reading %d/10 ===\n", i + 1);
        printf("  Temperature: %6.2f °C\n", temperature);
        printf("  Humidity:    %6.2f %%\n", humidity);
        printf("  Pressure:    %7.2f hPa\n", pressure);
        printf("\n");

        sleep(2);
    }

    // Close I2C device
    lgI2cClose(h);
    printf("I2C device closed. Cleanup complete.\n");

    return 0;
}
