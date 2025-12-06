/**
 * PWM LED Fade Example using lgpio Framework with PWM HAL
 *
 * Demonstrates hardware PWM control for smooth LED fading effects.
 * Uses the Linux kernel PWM subsystem for precise, CPU-efficient control.
 *
 * Hardware Setup:
 * - LED + 220Ω resistor connected to GPIO 18 (PWM0)
 * - LED cathode (short leg) to GND
 * - LED anode (long leg) through resistor to GPIO 18
 *
 * Alternate GPIO pins:
 * - GPIO 12 (PWM0) - conflicts with GPIO 18
 * - GPIO 13 (PWM1)
 * - GPIO 19 (PWM1) - conflicts with GPIO 13
 *
 * Prerequisites:
 * 1. Enable PWM device tree overlay:
 *    - Edit /boot/config.txt (Pi 1-4) or /boot/firmware/config.txt (Pi 5)
 *    - Add: dtoverlay=pwm,pin=18,func=2
 *    - Reboot
 *
 * 2. Setup PWM permissions:
 *    sudo ./scripts/setup-pwm-perms.sh
 *
 * See docs/PWM_SETUP.md for complete setup instructions.
 *
 * @file pwm_fade.c
 * @author PlatformIO Linux ARM Platform
 * @version 1.0.0
 * @date 2025-11-12
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>
#include "pwm-hal.h"

// Configuration
#define PWM_GPIO_PIN    18      // GPIO 18 (PWM0)
#define PWM_FREQUENCY   1000    // 1 kHz (good for LED control)
#define FADE_STEPS      100     // Number of steps for fade effect
#define FADE_DELAY_MS   20      // Delay between steps (20ms = 50 updates/sec)

// Global flag for signal handling
static volatile bool g_running = true;

/**
 * @brief Signal handler for graceful shutdown
 */
void signal_handler(int signum) {
    (void)signum; // Unused parameter
    printf("\nReceived interrupt signal, shutting down...\n");
    g_running = false;
}

/**
 * @brief Fade LED from 0% to 100% brightness
 */
void fade_up(int pin) {
    for (int i = 0; i <= FADE_STEPS && g_running; i++) {
        float duty_cycle = (float)i / FADE_STEPS * 100.0f;
        int result = pwm_write(pin, duty_cycle);
        if (result != PWM_SUCCESS) {
            fprintf(stderr, "Error setting duty cycle: %s\n",
                    pwm_error_string(result));
            return;
        }
        usleep(FADE_DELAY_MS * 1000);
    }
}

/**
 * @brief Fade LED from 100% to 0% brightness
 */
void fade_down(int pin) {
    for (int i = FADE_STEPS; i >= 0 && g_running; i--) {
        float duty_cycle = (float)i / FADE_STEPS * 100.0f;
        int result = pwm_write(pin, duty_cycle);
        if (result != PWM_SUCCESS) {
            fprintf(stderr, "Error setting duty cycle: %s\n",
                    pwm_error_string(result));
            return;
        }
        usleep(FADE_DELAY_MS * 1000);
    }
}

/**
 * @brief Print setup instructions and troubleshooting tips
 */
void print_setup_info(void) {
    printf("\n");
    printf("===================================================================\n");
    printf("PWM LED Fade Example - Setup Information\n");
    printf("===================================================================\n");
    printf("\n");
    printf("Hardware Setup:\n");
    printf("  - LED + 220Ω resistor connected to GPIO 18\n");
    printf("  - LED cathode (short leg, flat side) to GND\n");
    printf("  - LED anode (long leg) through resistor to GPIO 18\n");
    printf("\n");
    printf("Software Requirements:\n");
    printf("  1. Enable PWM overlay in /boot/config.txt (Pi 1-4) or\n");
    printf("     /boot/firmware/config.txt (Pi 5):\n");
    printf("     dtoverlay=pwm,pin=18,func=2\n");
    printf("\n");
    printf("  2. Setup PWM permissions:\n");
    printf("     sudo ./scripts/setup-pwm-perms.sh\n");
    printf("\n");
    printf("  3. Reboot after making changes\n");
    printf("\n");
    printf("Troubleshooting:\n");
    printf("  - Permission denied: Run setup-pwm-perms.sh with sudo\n");
    printf("  - PWM not exported: Check device tree overlay is loaded\n");
    printf("  - Invalid pin: GPIO 18 is not available or not configured\n");
    printf("\n");
    printf("See docs/PWM_SETUP.md for complete documentation\n");
    printf("===================================================================\n");
    printf("\n");
}

/**
 * @brief Main program entry point
 */
int main(int argc, char *argv[]) {
    int result;
    int gpio_pin = PWM_GPIO_PIN;
    int frequency = PWM_FREQUENCY;

    // Parse command line arguments
    if (argc > 1) {
        gpio_pin = atoi(argv[1]);
    }
    if (argc > 2) {
        frequency = atoi(argv[2]);
    }

    // Print header
    printf("PWM LED Fade Example (lgpio framework with PWM HAL)\n");
    printf("====================================================\n");
    printf("GPIO Pin: %d\n", gpio_pin);
    printf("Frequency: %d Hz\n", frequency);
    printf("Fade Steps: %d\n", FADE_STEPS);
    printf("Fade Delay: %d ms\n", FADE_DELAY_MS);
    printf("Press Ctrl+C to exit\n");
    printf("\n");

    // Setup signal handler for graceful shutdown
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Validate GPIO pin
    if (!pwm_pin_is_valid(gpio_pin)) {
        fprintf(stderr, "ERROR: GPIO %d does not support PWM\n", gpio_pin);
        fprintf(stderr, "Valid PWM pins: 12, 13, 18, 19\n\n");
        print_setup_info();
        return 1;
    }

    // Initialize PWM
    printf("Initializing PWM on GPIO %d at %d Hz...\n", gpio_pin, frequency);
    result = pwm_init(gpio_pin, frequency);
    if (result != PWM_SUCCESS) {
        fprintf(stderr, "ERROR: Failed to initialize PWM: %s\n",
                pwm_error_string(result));
        fprintf(stderr, "\n");

        // Provide specific troubleshooting based on error type
        if (result == PWM_ERROR_PERMISSION) {
            fprintf(stderr, "This error usually means:\n");
            fprintf(stderr, "  1. PWM permissions not setup correctly\n");
            fprintf(stderr, "  2. User not in 'gpio' group\n");
            fprintf(stderr, "\nSolution: Run setup script with sudo:\n");
            fprintf(stderr, "  sudo ./scripts/setup-pwm-perms.sh\n");
            fprintf(stderr, "  sudo usermod -a -G gpio $USER\n");
            fprintf(stderr, "  # Log out and back in for group changes to take effect\n");
        } else if (result == PWM_ERROR_NOT_EXPORTED) {
            fprintf(stderr, "This error usually means:\n");
            fprintf(stderr, "  1. PWM device tree overlay not loaded\n");
            fprintf(stderr, "  2. Wrong pwmchip number for your Pi model\n");
            fprintf(stderr, "\nSolution: Enable PWM overlay:\n");
            fprintf(stderr, "  # Edit /boot/config.txt (Pi 1-4) or /boot/firmware/config.txt (Pi 5)\n");
            fprintf(stderr, "  # Add the following line:\n");
            fprintf(stderr, "  dtoverlay=pwm,pin=%d,func=2\n", gpio_pin);
            fprintf(stderr, "  # Reboot\n");
        } else if (result == PWM_ERROR_BUSY) {
            fprintf(stderr, "This error means the PWM channel is already in use.\n");
            fprintf(stderr, "Note: GPIO 12 and 18 share PWM0, GPIO 13 and 19 share PWM1\n");
        }

        fprintf(stderr, "\n");
        print_setup_info();
        return 1;
    }

    printf("PWM initialized successfully!\n");
    printf("Starting fade effect (Ctrl+C to stop)...\n");
    printf("\n");

    // Get initial status
    pwm_status_t status;
    if (pwm_get_status(gpio_pin, &status) == PWM_SUCCESS) {
        printf("PWM Status:\n");
        printf("  Chip: %d, Channel: %d\n", status.pwm_chip, status.pwm_channel);
        printf("  Enabled: %s\n", status.is_enabled ? "yes" : "no");
        printf("  Frequency: %u Hz\n", status.frequency_hz);
        printf("  Period: %llu ns\n", (unsigned long long)status.period_ns);
        printf("\n");
    }

    // Main fade loop
    int cycle = 0;
    while (g_running) {
        cycle++;
        printf("Fade cycle %d: UP ", cycle);
        fflush(stdout);

        fade_up(gpio_pin);

        if (!g_running) break;

        printf("-> DOWN\n");
        fade_down(gpio_pin);

        if (!g_running) break;

        // Brief pause between cycles
        usleep(500000); // 500ms
    }

    // Cleanup
    printf("\nCleaning up...\n");
    result = pwm_deinit(gpio_pin);
    if (result != PWM_SUCCESS) {
        fprintf(stderr, "Warning: Failed to cleanup PWM: %s\n",
                pwm_error_string(result));
    } else {
        printf("PWM cleanup complete\n");
    }

    printf("Exiting.\n");
    return 0;
}
