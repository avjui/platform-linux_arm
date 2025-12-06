#include <stdio.h>
#include <stdlib.h>
#include <lgpio.h>
#include <unistd.h>
#include <stdint.h>

// MCP3008 has 8 analog input channels (0-7)
#define NUM_CHANNELS 8

// SPI Configuration for MCP3008
#define SPI_DEVICE 0        // /dev/spidev0.0
#define SPI_CHANNEL 0       // CE0 (chip select 0)
#define SPI_SPEED 1000000   // 1 MHz (MCP3008 supports up to 3.6 MHz at 5V, 1.35 MHz at 2.7V)
#define SPI_FLAGS 0         // Mode 0 (CPOL=0, CPHA=0) - default mode for MCP3008

/**
 * Read analog value from MCP3008 ADC channel
 *
 * @param h SPI handle from lgSpiOpen
 * @param channel Channel number (0-7)
 * @return 10-bit ADC value (0-1023) or -1 on error
 */
int read_adc(int h, int channel) {
    if (channel < 0 || channel > 7) {
        fprintf(stderr, "Invalid channel: %d (must be 0-7)\n", channel);
        return -1;
    }

    // MCP3008 communication protocol:
    // Send 3 bytes:
    //   Byte 1: Start bit (0x01)
    //   Byte 2: SGL/DIFF + Channel (single-ended mode: 0b1000xxxx where xxxx is channel)
    //   Byte 3: Don't care (0x00)
    //
    // Receive 3 bytes:
    //   Byte 1: Don't care
    //   Byte 2: Null bit + bit 9 + bit 8 (0bxxxxxx98)
    //   Byte 3: Bits 7-0 (0b76543210)

    uint8_t tx[3];
    uint8_t rx[3];

    // Build command
    tx[0] = 0x01;                    // Start bit
    tx[1] = (0x08 | channel) << 4;   // Single-ended mode (1) + channel selection
    tx[2] = 0x00;                    // Don't care

    // Perform SPI transfer
    int result = lgSpiXfer(h, (char *)tx, (char *)rx, 3);
    if (result < 0) {
        fprintf(stderr, "SPI transfer failed: %d\n", result);
        return -1;
    }

    // Parse 10-bit result from received bytes
    // Byte 1 (rx[0]): ignore
    // Byte 2 (rx[1]): bits 9-8 in lower 2 bits
    // Byte 3 (rx[2]): bits 7-0
    int value = ((rx[1] & 0x03) << 8) | rx[2];

    return value;
}

/**
 * Convert ADC value to percentage
 */
float adc_to_percentage(int adc_value) {
    return (adc_value / 1023.0) * 100.0;
}

/**
 * Convert ADC value to voltage (assuming 3.3V reference)
 */
float adc_to_voltage(int adc_value) {
    return (adc_value / 1023.0) * 3.3;
}

int main() {
    printf("MCP3008 SPI ADC Example (lgpio framework)\n");
    printf("=========================================\n\n");

    // Open SPI device
    printf("Opening SPI device %d.%d...\n", SPI_DEVICE, SPI_CHANNEL);
    int h = lgSpiOpen(SPI_DEVICE, SPI_CHANNEL, SPI_SPEED, SPI_FLAGS);
    if (h < 0) {
        fprintf(stderr, "Failed to open SPI device: %d\n", h);
        fprintf(stderr, "\nTroubleshooting:\n");
        fprintf(stderr, "1. Enable SPI: sudo raspi-config -> Interface Options -> SPI\n");
        fprintf(stderr, "2. Check SPI device exists: ls -l /dev/spidev*\n");
        fprintf(stderr, "3. Check permissions: sudo chmod 666 /dev/spidev0.0\n");
        return 1;
    }
    printf("SPI device opened successfully (handle: %d)\n", h);
    printf("SPI speed: %d Hz (%.2f MHz)\n\n", SPI_SPEED, SPI_SPEED / 1000000.0);

    printf("MCP3008 Configuration:\n");
    printf("  - 8 channels (0-7)\n");
    printf("  - 10-bit resolution (0-1023)\n");
    printf("  - Reference voltage: 3.3V\n");
    printf("  - Single-ended mode\n\n");

    printf("Reading all channels 10 times...\n");
    printf("Press Ctrl+C to exit\n\n");

    // Read all channels 10 times
    for (int iteration = 0; iteration < 10; iteration++) {
        printf("=== Reading %d/10 ===\n", iteration + 1);

        for (int channel = 0; channel < NUM_CHANNELS; channel++) {
            int adc_value = read_adc(h, channel);

            if (adc_value < 0) {
                printf("  Channel %d: ERROR\n", channel);
                continue;
            }

            float percentage = adc_to_percentage(adc_value);
            float voltage = adc_to_voltage(adc_value);

            printf("  Channel %d: %4d (0x%03X) | %6.2f%% | %5.3fV\n",
                   channel, adc_value, adc_value, percentage, voltage);
        }

        printf("\n");
        sleep(2);  // Wait 2 seconds between readings
    }

    // Close SPI device
    lgSpiClose(h);
    printf("SPI device closed. Cleanup complete.\n");

    return 0;
}
