/*
 * libgpiod LED Blink Example (v2 API)
 *
 * This example demonstrates basic GPIO output using libgpiod v2.x API.
 * It blinks an LED connected to GPIO 23 (BCM numbering).
 *
 * Hardware:
 * - LED with 220Ω resistor connected to GPIO 23 (Physical pin 16)
 * - GND connection (any ground pin)
 *
 * libgpiod v2 API provides a more flexible, object-oriented design
 * compared to v1, with better support for bulk operations and configuration.
 *
 * NOTE: This code will only compile with libgpiod v2.x (Debian Bookworm,
 * Ubuntu 22.04+). For v1.x, see ../libgpiod-blink/
 */

#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>

#define GPIO_CHIP "/dev/gpiochip0"
#define LED_PIN 23
#define BLINK_COUNT 10

int main(void) {
    struct gpiod_chip *chip;
    struct gpiod_request_config *req_cfg;
    struct gpiod_line_config *line_cfg;
    struct gpiod_line_request *request;
    unsigned int offsets[1] = {LED_PIN};
    int ret;

    printf("libgpiod v2 LED Blink Example\n");
    printf("==============================\n\n");

    // Open GPIO chip
    chip = gpiod_chip_open(GPIO_CHIP);
    if (!chip) {
        perror("Failed to open GPIO chip");
        return 1;
    }

    printf("Opened GPIO chip: %s\n", GPIO_CHIP);
    printf("GPIO chip label: %s\n", gpiod_chip_get_label(chip));
    printf("Number of lines: %zu\n\n", gpiod_chip_get_num_lines(chip));

    // Create request configuration
    req_cfg = gpiod_request_config_new();
    if (!req_cfg) {
        perror("Failed to create request config");
        gpiod_chip_close(chip);
        return 1;
    }
    gpiod_request_config_set_consumer(req_cfg, "blink-example");

    // Create line configuration
    line_cfg = gpiod_line_config_new();
    if (!line_cfg) {
        perror("Failed to create line config");
        gpiod_request_config_free(req_cfg);
        gpiod_chip_close(chip);
        return 1;
    }

    // Configure line as output with initial value LOW
    gpiod_line_config_set_direction_default(line_cfg, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_config_set_output_value_default(line_cfg, 0);

    // Request lines
    request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) {
        perror("Failed to request GPIO lines");
        gpiod_line_config_free(line_cfg);
        gpiod_request_config_free(req_cfg);
        gpiod_chip_close(chip);
        return 1;
    }

    printf("Configured GPIO %d as output\n", LED_PIN);
    printf("Blinking LED %d times...\n\n", BLINK_COUNT);

    // Blink LED
    for (int i = 0; i < BLINK_COUNT; i++) {
        // Turn LED ON
        ret = gpiod_line_request_set_value(request, LED_PIN, 1);
        if (ret < 0) {
            perror("Failed to set GPIO value");
            break;
        }
        printf("LED ON  (iteration %d/%d)\n", i + 1, BLINK_COUNT);
        sleep(1);

        // Turn LED OFF
        ret = gpiod_line_request_set_value(request, LED_PIN, 0);
        if (ret < 0) {
            perror("Failed to set GPIO value");
            break;
        }
        printf("LED OFF (iteration %d/%d)\n", i + 1, BLINK_COUNT);
        sleep(1);
    }

    printf("\nBlink complete!\n");

    // Cleanup (automatic on exit, but explicit is good practice)
    gpiod_line_request_release(request);
    gpiod_line_config_free(line_cfg);
    gpiod_request_config_free(req_cfg);
    gpiod_chip_close(chip);

    printf("GPIO resources released\n");

    /*
     * NOTE: GPIO State Persistence
     *
     * By default, the GPIO line may revert to its default state (usually input)
     * when this program exits and the line request is released.
     *
     * On Raspberry Pi, to maintain the GPIO state after program exit, add this
     * line to /boot/firmware/config.txt (or /boot/config.txt on older systems):
     *
     *     dtparam=strict_gpiod
     *
     * Then reboot. This enables persistent GPIO state across process restarts.
     *
     * See docs/LIBGPIOD_SETUP.md for more details.
     */

    return 0;
}
