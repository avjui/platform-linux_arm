#include <stdio.h>
#include <lgpio.h>
#include <unistd.h>

#define GPIO_PIN 23  // BCM GPIO 23

int main() {
    int h = lgGpiochipOpen(0);  // Open GPIO chip 0
    if (h < 0) {
        printf("Failed to open gpiochip0\n");
        return 1;
    }

    // Set GPIO23 as output, initial value 0
    if (lgGpioClaimOutput(h, 0, GPIO_PIN, 0) < 0) {
        printf("Failed to claim GPIO %d as output\n", GPIO_PIN);
        lgGpiochipClose(h);
        return 1;
    }

    printf("Blinking LED on GPIO %d (lgpio framework)\n", GPIO_PIN);
    printf("Press Ctrl+C to exit\n");

    // Blink 10 times
    for (int i = 0; i < 10; i++) {
        lgGpioWrite(h, GPIO_PIN, 1);  // HIGH
        printf("LED ON (iteration %d/10)\n", i + 1);
        sleep(1);
        lgGpioWrite(h, GPIO_PIN, 0);  // LOW
        printf("LED OFF\n");
        sleep(1);
    }

    lgGpiochipClose(h);
    printf("Cleanup complete\n");
    return 0;
}
