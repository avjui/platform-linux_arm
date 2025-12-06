#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define GPIO_PIN 23  // BCM GPIO 23

int main() {
    if (gpioInitialise() < 0) {
        printf("Failed to initialize pigpio\n");
        return 1;
    }

    // Set GPIO23 as output
    if (gpioSetMode(GPIO_PIN, PI_OUTPUT) < 0) {
        printf("Failed to set GPIO %d as output\n", GPIO_PIN);
        gpioTerminate();
        return 1;
    }

    printf("Blinking LED on GPIO %d (pigpio framework)\n", GPIO_PIN);
    printf("Press Ctrl+C to exit\n");

    // Blink 10 times
    for (int i = 0; i < 10; i++) {
        gpioWrite(GPIO_PIN, 1);  // HIGH
        printf("LED ON (iteration %d/10)\n", i + 1);
        sleep(1);
        gpioWrite(GPIO_PIN, 0);  // LOW
        printf("LED OFF\n");
        sleep(1);
    }

    gpioTerminate();
    printf("Cleanup complete\n");
    return 0;
}
