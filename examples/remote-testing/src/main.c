/*
 * Remote Testing Example
 *
 * This is a simple application that demonstrates the remote testing
 * capabilities of the platform-linux_arm PlatformIO platform.
 *
 * Run tests with: pio test
 */

#include <stdio.h>
#include "math_functions.h"

int main() {
    printf("Remote Testing Example\n");
    printf("======================\n\n");

    printf("Testing math functions:\n");
    printf("  5 + 3 = %d\n", add(5, 3));
    printf("  10 - 4 = %d\n", subtract(10, 4));
    printf("  6 * 7 = %d\n", multiply(6, 7));
    printf("  20 / 4 = %d\n", divide(20, 4));
    printf("  5! = %d\n", factorial(5));

    printf("\nApplication completed successfully!\n");
    return 0;
}
