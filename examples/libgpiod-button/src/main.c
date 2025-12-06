/*
 * libgpiod Button Input with Interrupts Example
 *
 * This example demonstrates GPIO input with edge detection (interrupts).
 * It monitors a button connected to GPIO 24 and detects press/release events.
 * Also blinks an LED on GPIO 23 when the button is pressed.
 *
 * Hardware:
 * - Button connected between GPIO 24 (Physical pin 18) and GND
 * - LED with 220Ω resistor connected to GPIO 23 (Physical pin 16)
 *
 * Press Ctrl+C to exit.
 */

#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>

#define GPIO_CHIP "gpiochip0"
#define BUTTON_PIN 24
#define LED_PIN 23

// Global flag for signal handling
static volatile bool keep_running = true;

void signal_handler(int signum) {
    (void)signum;  // Unused parameter
    keep_running = false;
    printf("\nReceived interrupt signal, exiting...\n");
}

int main(void) {
    struct gpiod_chip *chip;
    struct gpiod_line *button_line, *led_line;
    struct gpiod_line_event event;
    struct timespec timeout = {1, 0};  // 1 second timeout
    int ret;
    bool led_state = false;

    printf("libgpiod Button Input with Interrupts Example\n");
    printf("==============================================\n\n");

    // Set up signal handler for graceful shutdown
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Open GPIO chip
    chip = gpiod_chip_open_by_name(GPIO_CHIP);
    if (!chip) {
        perror("Failed to open GPIO chip");
        return 1;
    }

    printf("Opened GPIO chip: %s\n\n", GPIO_CHIP);

    // Get button line (GPIO 24)
    button_line = gpiod_chip_get_line(chip, BUTTON_PIN);
    if (!button_line) {
        perror("Failed to get button GPIO line");
        gpiod_chip_close(chip);
        return 1;
    }

    // Get LED line (GPIO 23)
    led_line = gpiod_chip_get_line(chip, LED_PIN);
    if (!led_line) {
        perror("Failed to get LED GPIO line");
        gpiod_chip_close(chip);
        return 1;
    }

    // Request button line as input with pull-up and both edge events
    ret = gpiod_line_request_both_edges_events_flags(button_line, "button-example",
                                                      GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP);
    if (ret < 0) {
        perror("Failed to request button line for events");
        gpiod_chip_close(chip);
        return 1;
    }

    // Request LED line as output
    ret = gpiod_line_request_output(led_line, "button-led", 0);
    if (ret < 0) {
        perror("Failed to request LED line as output");
        gpiod_line_release(button_line);
        gpiod_chip_close(chip);
        return 1;
    }

    printf("Configured GPIO %d as input (button) with pull-up\n", BUTTON_PIN);
    printf("Configured GPIO %d as output (LED)\n", LED_PIN);
    printf("\nMonitoring button presses... Press Ctrl+C to exit\n\n");

    // Main event loop
    while (keep_running) {
        // Wait for edge event with timeout
        ret = gpiod_line_event_wait(button_line, &timeout);

        if (ret < 0) {
            perror("Error waiting for events");
            break;
        } else if (ret == 0) {
            // Timeout - no event occurred, continue waiting
            continue;
        }

        // Event occurred, read it
        ret = gpiod_line_event_read(button_line, &event);
        if (ret < 0) {
            perror("Error reading event");
            break;
        }

        // Process event
        if (event.event_type == GPIOD_LINE_EVENT_RISING_EDGE) {
            printf("Button RELEASED (rising edge)  - LED OFF\n");
            led_state = false;
            gpiod_line_set_value(led_line, 0);
        } else if (event.event_type == GPIOD_LINE_EVENT_FALLING_EDGE) {
            printf("Button PRESSED  (falling edge) - LED ON\n");
            led_state = true;
            gpiod_line_set_value(led_line, 1);
        }
    }

    printf("\nCleaning up...\n");

    // Turn off LED before exit
    gpiod_line_set_value(led_line, 0);

    // Cleanup
    gpiod_line_release(button_line);
    gpiod_line_release(led_line);
    gpiod_chip_close(chip);

    printf("GPIO resources released\n");
    printf("Exiting gracefully\n");

    return 0;
}
