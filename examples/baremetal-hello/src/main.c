#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    printf("Hello from bare-metal Linux ARM!\n");
    printf("Running on: ");

    #if defined(RASPBERRYPI4)
    printf("Raspberry Pi 4\n");
    #elif defined(RASPBERRYPI3)
    printf("Raspberry Pi 3\n");
    #elif defined(RASPBERRYPI2)
    printf("Raspberry Pi 2\n");
    #elif defined(RASPBERRYPI)
    printf("Raspberry Pi\n");
    #else
    printf("Unknown ARM Linux board\n");
    #endif

    printf("This is a bare-metal application (no framework).\n");
    printf("Built with PlatformIO for Linux ARM platform.\n");

    return 0;
}
