/**
 * PWM Servo Motor Control Example
 *
 * Demonstrates servo motor position control using hardware PWM.
 * Sweeps servo between 0° and 180° positions.
 *
 * Hardware Setup:
 * - Servo motor signal wire to GPIO 18 (PWM0)
 * - Servo power wire (red/+) to external 5V power supply
 * - Servo ground wire (black/-) to common ground (Pi GND + power supply GND)
 *
 * IMPORTANT - Power Supply:
 * - DO NOT power servo from Pi's 5V pin!
 * - Servos draw high current (500mA - 2A) that can damage Pi
 * - Use external 5V power supply rated for servo current draw
 * - Connect grounds together: Pi GND <-> Power supply GND
 * - Only connect signal wire to Pi GPIO 18
 *
 * Servo Wire Colors (typical):
 * - Brown/Black: Ground (GND)
 * - Red: Power (5V from external supply)
 * - Orange/Yellow/White: Signal (GPIO 18)
 *
 * Prerequisites:
 * 1. Enable PWM device tree overlay (see docs/PWM_SETUP.md)
 * 2. Run: sudo ./scripts/setup-pwm-perms.sh
 * 3. Connect servo with external power supply
 *
 * @file servo_control.c
 * @author PlatformIO Linux ARM Platform
 * @version 1.0.0
 * @date 2025-11-12
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>
#include <math.h>
#include "pwm-hal.h"

// Servo configuration
#define SERVO_GPIO_PIN  18      // GPIO 18 (PWM0)
#define SERVO_FREQUENCY 50      // 50 Hz (20 ms period) - standard for servos

// Servo pulse width timings (typical values)
// May need adjustment based on your specific servo model
#define SERVO_MIN_PULSE_MS   1.0    // 1 ms = 0 degrees
#define SERVO_MAX_PULSE_MS   2.0    // 2 ms = 180 degrees
#define SERVO_MID_PULSE_MS   1.5    // 1.5 ms = 90 degrees

// Calculate duty cycle from pulse width
// Period = 20 ms (50 Hz), pulse width in ms
#define PULSE_TO_DUTY(pulse_ms) ((pulse_ms / 20.0) * 100.0)

// Servo limits
#define SERVO_MIN_ANGLE  0.0     // Minimum angle (degrees)
#define SERVO_MAX_ANGLE  180.0   // Maximum angle (degrees)

// Global flag for signal handling
static volatile bool g_running = true;

/**
 * @brief Signal handler for graceful shutdown
 */
void signal_handler(int signum) {
    (void)signum;
    printf("\nReceived interrupt signal, shutting down...\n");
    g_running = false;
}

/**
 * @brief Convert servo angle to duty cycle percentage
 *
 * @param angle Servo angle in degrees (0-180)
 * @return Duty cycle percentage
 */
float angle_to_duty_cycle(float angle) {
    // Clamp angle to valid range
    if (angle < SERVO_MIN_ANGLE) angle = SERVO_MIN_ANGLE;
    if (angle > SERVO_MAX_ANGLE) angle = SERVO_MAX_ANGLE;

    // Linear interpolation between min and max pulse widths
    float pulse_ms = SERVO_MIN_PULSE_MS +
                     (angle / SERVO_MAX_ANGLE) *
                     (SERVO_MAX_PULSE_MS - SERVO_MIN_PULSE_MS);

    // Convert pulse width to duty cycle
    return PULSE_TO_DUTY(pulse_ms);
}

/**
 * @brief Set servo position
 *
 * @param pin GPIO pin number
 * @param angle Target angle in degrees (0-180)
 * @return PWM_SUCCESS on success, error code on failure
 */
int servo_set_position(int pin, float angle) {
    float duty_cycle = angle_to_duty_cycle(angle);
    return pwm_write(pin, duty_cycle);
}

/**
 * @brief Smooth servo movement to target angle
 *
 * @param pin GPIO pin number
 * @param start_angle Starting angle
 * @param end_angle Target angle
 * @param duration_ms Total movement duration in milliseconds
 * @return PWM_SUCCESS on success
 */
int servo_move_smooth(int pin, float start_angle, float end_angle, int duration_ms) {
    const int steps = 50;  // Number of intermediate positions
    const int delay_ms = duration_ms / steps;

    for (int i = 0; i <= steps && g_running; i++) {
        // Linear interpolation
        float angle = start_angle + (end_angle - start_angle) * (float)i / steps;

        int result = servo_set_position(pin, angle);
        if (result != PWM_SUCCESS) {
            return result;
        }

        usleep(delay_ms * 1000);
    }

    return PWM_SUCCESS;
}

/**
 * @brief Print setup instructions
 */
void print_setup_info(void) {
    printf("\n");
    printf("===================================================================\n");
    printf("PWM Servo Control Example - Setup Information\n");
    printf("===================================================================\n");
    printf("\n");
    printf("Hardware Setup:\n");
    printf("  - Servo signal wire (orange/yellow/white) to GPIO 18\n");
    printf("  - Servo power wire (red) to external 5V power supply (+)\n");
    printf("  - Servo ground wire (black/brown) to common ground\n");
    printf("  - Connect Pi GND to power supply GND (common ground)\n");
    printf("\n");
    printf("CRITICAL SAFETY WARNING:\n");
    printf("  - DO NOT connect servo power to Pi's 5V pin!\n");
    printf("  - Servos draw 500mA - 2A current that WILL damage your Pi\n");
    printf("  - Always use external 5V power supply for servo power\n");
    printf("  - Only connect signal wire to Pi GPIO\n");
    printf("\n");
    printf("Software Requirements:\n");
    printf("  1. Enable PWM overlay in /boot/config.txt or\n");
    printf("     /boot/firmware/config.txt (Pi 5):\n");
    printf("     dtoverlay=pwm,pin=18,func=2\n");
    printf("\n");
    printf("  2. Setup PWM permissions:\n");
    printf("     sudo ./scripts/setup-pwm-perms.sh\n");
    printf("\n");
    printf("  3. Reboot after making changes\n");
    printf("\n");
    printf("See docs/PWM_SETUP.md for complete documentation\n");
    printf("===================================================================\n");
    printf("\n");
}

/**
 * @brief Demonstrate various servo movements
 */
void demo_servo_movements(int pin) {
    printf("\nDemo 1: Basic positions (0°, 90°, 180°)\n");
    printf("----------------------------------------\n");

    printf("Moving to 0° (full left)...\n");
    servo_set_position(pin, 0.0);
    sleep(2);

    printf("Moving to 90° (center)...\n");
    servo_set_position(pin, 90.0);
    sleep(2);

    printf("Moving to 180° (full right)...\n");
    servo_set_position(pin, 180.0);
    sleep(2);

    printf("Moving back to 90° (center)...\n");
    servo_set_position(pin, 90.0);
    sleep(2);

    if (!g_running) return;

    printf("\nDemo 2: Smooth sweep (0° to 180° and back)\n");
    printf("-------------------------------------------\n");

    printf("Sweeping from 0° to 180°...\n");
    servo_move_smooth(pin, 0.0, 180.0, 2000);  // 2 second movement
    if (!g_running) return;

    sleep(1);

    printf("Sweeping from 180° to 0°...\n");
    servo_move_smooth(pin, 180.0, 0.0, 2000);  // 2 second movement
    if (!g_running) return;

    sleep(1);

    if (!g_running) return;

    printf("\nDemo 3: Precise angles\n");
    printf("----------------------\n");

    float angles[] = {0, 30, 60, 90, 120, 150, 180};
    int num_angles = sizeof(angles) / sizeof(angles[0]);

    for (int i = 0; i < num_angles && g_running; i++) {
        printf("Setting position to %.0f°...\n", angles[i]);
        servo_set_position(pin, angles[i]);
        sleep(1);
    }

    if (!g_running) return;

    printf("\nDemo 4: Continuous sweep (Ctrl+C to stop)\n");
    printf("-----------------------------------------\n");

    int cycle = 0;
    while (g_running) {
        cycle++;
        printf("Sweep cycle %d: 0° -> 180° -> 0°\n", cycle);

        servo_move_smooth(pin, 0.0, 180.0, 2000);
        if (!g_running) break;

        servo_move_smooth(pin, 180.0, 0.0, 2000);
        if (!g_running) break;

        sleep(1);
    }
}

/**
 * @brief Main program entry point
 */
int main(int argc, char *argv[]) {
    int result;
    int gpio_pin = SERVO_GPIO_PIN;
    int frequency = SERVO_FREQUENCY;

    // Parse command line arguments
    if (argc > 1) {
        gpio_pin = atoi(argv[1]);
    }

    // Print header
    printf("PWM Servo Motor Control Example\n");
    printf("================================\n");
    printf("GPIO Pin: %d\n", gpio_pin);
    printf("Frequency: %d Hz (standard servo frequency)\n", frequency);
    printf("Pulse Width Range: %.1f - %.1f ms\n",
           SERVO_MIN_PULSE_MS, SERVO_MAX_PULSE_MS);
    printf("Angle Range: %.0f° - %.0f°\n",
           SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    printf("Press Ctrl+C to exit\n");
    printf("\n");

    // Setup signal handler
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

        // Provide troubleshooting
        if (result == PWM_ERROR_PERMISSION) {
            fprintf(stderr, "Solution: Run setup script with sudo:\n");
            fprintf(stderr, "  sudo ./scripts/setup-pwm-perms.sh\n");
        } else if (result == PWM_ERROR_NOT_EXPORTED) {
            fprintf(stderr, "Solution: Enable PWM overlay and reboot:\n");
            fprintf(stderr, "  # Add to /boot/config.txt (Pi 1-4) or /boot/firmware/config.txt (Pi 5):\n");
            fprintf(stderr, "  dtoverlay=pwm,pin=%d,func=2\n", gpio_pin);
            fprintf(stderr, "  # Then reboot\n");
        }

        fprintf(stderr, "\n");
        print_setup_info();
        return 1;
    }

    printf("PWM initialized successfully!\n");

    // Get PWM status
    pwm_status_t status;
    if (pwm_get_status(gpio_pin, &status) == PWM_SUCCESS) {
        printf("\nPWM Status:\n");
        printf("  Chip: %d, Channel: %d\n", status.pwm_chip, status.pwm_channel);
        printf("  Frequency: %u Hz\n", status.frequency_hz);
        printf("  Period: %llu ns (%.1f ms)\n",
               (unsigned long long)status.period_ns,
               status.period_ns / 1000000.0);
        printf("\n");
    }

    // Center servo before starting demo
    printf("Centering servo (90°)...\n");
    servo_set_position(gpio_pin, 90.0);
    sleep(1);

    // Run demo
    printf("\nStarting servo demonstration...\n");
    demo_servo_movements(gpio_pin);

    // Return to center position
    if (g_running) {
        printf("\nReturning to center position...\n");
        servo_set_position(gpio_pin, 90.0);
        sleep(1);
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
