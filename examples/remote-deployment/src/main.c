/*
 * Remote Deployment Example for PlatformIO Linux ARM Platform
 *
 * This simple program demonstrates the upload/deployment functionality.
 * After building with 'pio run', you can deploy to a remote Raspberry Pi
 * using 'pio run --target upload'.
 *
 * The program blinks an LED using the lgpio library.
 * Adjust the GPIO pin number based on your hardware.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <lgpio.h>

#define LED_PIN 17  // GPIO 17 (Pin 11 on RPi header)
#define BLINK_COUNT 10
#define BLINK_DELAY_MS 500

int main(int argc, char *argv[]) {
    int h;
    int i;

    printf("PlatformIO Linux ARM - Remote Deployment Example\n");
    printf("=================================================\n\n");

    // Open GPIO chip
    h = lgGpiochipOpen(0);
    if (h < 0) {
        fprintf(stderr, "Error: Failed to open GPIO chip: %s\n", lgerrorText(h));
        fprintf(stderr, "Note: You may need to run with sudo for GPIO access.\n");
        return 1;
    }

    printf("GPIO chip opened successfully\n");

    // Claim GPIO pin for output
    if (lgGpioClaimOutput(h, 0, LED_PIN, 0) < 0) {
        fprintf(stderr, "Error: Failed to claim GPIO %d as output\n", LED_PIN);
        lgGpiochipClose(h);
        return 1;
    }

    printf("GPIO %d claimed as output\n", LED_PIN);
    printf("Blinking LED %d times...\n\n", BLINK_COUNT);

    // Blink the LED
    for (i = 0; i < BLINK_COUNT; i++) {
        printf("LED ON  (iteration %d/%d)\n", i + 1, BLINK_COUNT);
        lgGpioWrite(h, LED_PIN, 1);
        usleep(BLINK_DELAY_MS * 1000);

        printf("LED OFF (iteration %d/%d)\n", i + 1, BLINK_COUNT);
        lgGpioWrite(h, LED_PIN, 0);
        usleep(BLINK_DELAY_MS * 1000);
    }

    printf("\nBlink sequence complete!\n");

    // Cleanup
    lgGpioFree(h, LED_PIN);
    lgGpiochipClose(h);

    printf("GPIO resources released\n");
    printf("\n=================================================\n");
    printf("Program finished successfully\n");

    return 0;
}
