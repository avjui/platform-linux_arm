/*
 * Bare-Metal UART Serial Communication Example
 *
 * Demonstrates asynchronous serial communication using Linux termios API.
 * No GPIO library required - uses standard POSIX serial port interface.
 *
 * Features:
 * - Proper termios configuration following POSIX best practices
 * - Multiple operation modes (echo test, interactive)
 * - Configurable baud rate
 * - Non-blocking I/O with timeout
 * - Comprehensive error handling
 *
 * Use cases:
 * - GPS modules (NMEA data)
 * - Bluetooth serial (HC-05, HC-06)
 * - GSM/LTE modems (AT commands)
 * - Serial sensors and devices
 * - USB-to-Serial adapters
 *
 * Hardware connections (for hardware UART on GPIO):
 * - TX (GPIO 14, Pin 8)  -> RX of serial device
 * - RX (GPIO 15, Pin 10) -> TX of serial device
 * - GND -> GND
 *
 * Serial devices on Raspberry Pi:
 * - /dev/serial0 - Primary UART (symlink to ttyAMA0 or ttyS0)
 * - /dev/ttyAMA0 - Hardware UART (GPIO 14/15 on Pi 1/2/Zero)
 * - /dev/ttyS0 - Mini UART or Bluetooth (varies by model)
 * - /dev/ttyUSB0 - USB-to-Serial adapter
 * - /dev/ttyACM0 - USB CDC ACM device
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/select.h>
#include <sys/time.h>
#include <time.h>

// Configuration
#define DEFAULT_DEVICE "/dev/serial0"
#define DEFAULT_BAUD B9600
#define BUFFER_SIZE 256
#define TIMEOUT_SECONDS 5

// ANSI color codes for better readability
#define COLOR_RESET   "\033[0m"
#define COLOR_GREEN   "\033[32m"
#define COLOR_BLUE    "\033[34m"
#define COLOR_YELLOW  "\033[33m"
#define COLOR_RED     "\033[31m"
#define COLOR_CYAN    "\033[36m"

// Function prototypes
int configure_serial_port(int fd, speed_t baud);
int serial_write(int fd, const char *data, size_t len);
int serial_read_timeout(int fd, char *buffer, size_t max_len, int timeout_sec);
void print_usage(const char *program_name);
void run_echo_test(int fd);
void run_interactive_mode(int fd);

int main(int argc, char *argv[]) {
    const char *device = DEFAULT_DEVICE;
    speed_t baud = DEFAULT_BAUD;
    int fd;
    int mode = 0; // 0 = echo test, 1 = interactive

    // Print header
    printf("\n");
    printf("╔════════════════════════════════════════════════════╗\n");
    printf("║  Bare-Metal UART Serial Communication Example     ║\n");
    printf("║  Platform: Linux ARM (Raspberry Pi)               ║\n");
    printf("║  API: POSIX termios (no framework required)        ║\n");
    printf("╚════════════════════════════════════════════════════╝\n");
    printf("\n");

    // Parse command line arguments
    if (argc > 1) {
        if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
            print_usage(argv[0]);
            return 0;
        }
        if (strcmp(argv[1], "--interactive") == 0 || strcmp(argv[1], "-i") == 0) {
            mode = 1;
        }
        if (argc > 2) {
            device = argv[2];
        }
    }

    // Display configuration
    printf("Configuration:\n");
    printf("  Device: %s\n", device);
    printf("  Baud rate: 9600\n");
    printf("  Mode: %s\n", mode == 0 ? "Echo Test" : "Interactive");
    printf("\n");

    // Open serial port
    printf("Opening serial port...\n");
    fd = open(device, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        fprintf(stderr, "%sERROR: Error opening %s: %s%s\n",
                COLOR_RED, device, strerror(errno), COLOR_RESET);
        fprintf(stderr, "\nCommon issues:\n");
        fprintf(stderr, "  • Device not found: Check device path\n");
        fprintf(stderr, "  • Permission denied: Run as root or add user to 'dialout' group\n");
        fprintf(stderr, "  • UART disabled: Enable with 'sudo raspi-config' > Interface Options > Serial Port\n");
        fprintf(stderr, "\nTry: sudo usermod -a -G dialout $USER\n");
        fprintf(stderr, "Then log out and back in.\n");
        return 1;
    }
    printf("%sSerial port opened successfully%s\n", COLOR_GREEN, COLOR_RESET);

    // Configure serial port
    printf("Configuring serial parameters...\n");
    if (configure_serial_port(fd, baud) < 0) {
        fprintf(stderr, "%sERROR: Error configuring serial port%s\n", COLOR_RED, COLOR_RESET);
        close(fd);
        return 1;
    }
    printf("%sSerial port configured%s\n", COLOR_GREEN, COLOR_RESET);
    printf("\n");

    // Run selected mode
    if (mode == 0) {
        run_echo_test(fd);
    } else {
        run_interactive_mode(fd);
    }

    // Cleanup
    close(fd);
    printf("\n%sSerial port closed%s\n", COLOR_GREEN, COLOR_RESET);
    return 0;
}

/**
 * Configure serial port with proper termios settings
 * Following POSIX best practices for raw serial communication
 */
int configure_serial_port(int fd, speed_t baud) {
    struct termios options;

    // Get current port settings
    if (tcgetattr(fd, &options) < 0) {
        fprintf(stderr, "Error getting port attributes: %s\n", strerror(errno));
        return -1;
    }

    // Set baud rate (input and output)
    cfsetispeed(&options, baud);
    cfsetospeed(&options, baud);

    // Configure for raw input/output (no canonical mode, no echo)
    // This is the POSIX-compliant way, not zeroing the structure

    // Input flags: ignore break, no CR to NL, no parity check, no strip, no flow control
    options.c_iflag &= ~(IGNBRK | BRKINT | ICRNL | INLCR | PARMRK | INPCK | ISTRIP | IXON);

    // Output flags: no output processing
    options.c_oflag &= ~(OCRNL | ONLCR | ONLRET | ONOCR | OFILL | OPOST);

    // Line flags: no canonical mode, no echo, no signals
    options.c_lflag &= ~(ECHO | ECHONL | ICANON | IEXTEN | ISIG);

    // Control flags: 8 data bits, no parity, 1 stop bit, enable receiver, local line
    options.c_cflag &= ~(CSIZE | PARENB | CSTOPB);
    options.c_cflag |= CS8 | CREAD | CLOCAL;

    // Non-blocking read with timeout
    // VMIN = 0: return immediately with available data
    // VTIME = 5: timeout in deciseconds (0.5 seconds)
    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 5;

    // Apply settings immediately
    if (tcsetattr(fd, TCSANOW, &options) < 0) {
        fprintf(stderr, "Error setting port attributes: %s\n", strerror(errno));
        return -1;
    }

    // Flush any existing data
    tcflush(fd, TCIOFLUSH);

    return 0;
}

/**
 * Write data to serial port
 */
int serial_write(int fd, const char *data, size_t len) {
    ssize_t written = write(fd, data, len);
    if (written < 0) {
        fprintf(stderr, "Error writing to serial port: %s\n", strerror(errno));
        return -1;
    }
    // Ensure data is transmitted
    tcdrain(fd);
    return written;
}

/**
 * Read data from serial port with timeout using select()
 */
int serial_read_timeout(int fd, char *buffer, size_t max_len, int timeout_sec) {
    fd_set read_fds;
    struct timeval timeout;
    int retval;

    FD_ZERO(&read_fds);
    FD_SET(fd, &read_fds);

    timeout.tv_sec = timeout_sec;
    timeout.tv_usec = 0;

    retval = select(fd + 1, &read_fds, NULL, NULL, &timeout);

    if (retval < 0) {
        fprintf(stderr, "Error in select(): %s\n", strerror(errno));
        return -1;
    } else if (retval == 0) {
        // Timeout
        return 0;
    }

    // Data available, read it
    return read(fd, buffer, max_len);
}

/**
 * Echo test mode - sends test messages and displays responses
 */
void run_echo_test(int fd) {
    char buffer[BUFFER_SIZE];
    const char *test_messages[] = {
        "Hello from Raspberry Pi!",
        "Testing UART communication",
        "1234567890",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "Special chars: !@#$%^&*()",
        NULL
    };
    int msg_idx = 0;
    int bytes_read;

    printf("╔════════════════════════════════════════════════════╗\n");
    printf("║  Echo Test Mode                                    ║\n");
    printf("╚════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("This mode sends test messages and waits for echo responses.\n");
    printf("Connect TX to RX (loopback) or to another serial device.\n");
    printf("\n");

    while (test_messages[msg_idx] != NULL) {
        const char *msg = test_messages[msg_idx];
        size_t msg_len = strlen(msg);

        // Send message
        printf("%sTX:%s %s\n", COLOR_BLUE, COLOR_RESET, msg);
        if (serial_write(fd, msg, msg_len) < 0) {
            fprintf(stderr, "%sERROR: Failed to send message%s\n", COLOR_RED, COLOR_RESET);
            msg_idx++;
            continue;
        }

        // Wait for response
        printf("%sRX:%s Waiting for response", COLOR_CYAN, COLOR_RESET);
        fflush(stdout);

        memset(buffer, 0, BUFFER_SIZE);
        bytes_read = serial_read_timeout(fd, buffer, BUFFER_SIZE - 1, TIMEOUT_SECONDS);

        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            printf(" -> %s%s%s", COLOR_GREEN, buffer, COLOR_RESET);

            // Verify echo
            if (strncmp(msg, buffer, msg_len) == 0) {
                printf(" %sMatch%s\n", COLOR_GREEN, COLOR_RESET);
            } else {
                printf(" %sWARNING: Mismatch%s\n", COLOR_YELLOW, COLOR_RESET);
            }
        } else if (bytes_read == 0) {
            printf(" %s(timeout - no response)%s\n", COLOR_YELLOW, COLOR_RESET);
        } else {
            printf(" %sERROR: Read error%s\n", COLOR_RED, COLOR_RESET);
        }

        printf("\n");
        msg_idx++;

        // Small delay between messages
        usleep(500000); // 500ms
    }

    printf("%sEcho test completed%s\n", COLOR_GREEN, COLOR_RESET);
    printf("\nResults: %d messages sent\n", msg_idx);
}

/**
 * Interactive mode - send and receive data interactively
 */
void run_interactive_mode(int fd) {
    char tx_buffer[BUFFER_SIZE];
    char rx_buffer[BUFFER_SIZE];
    int bytes_read;

    printf("╔════════════════════════════════════════════════════╗\n");
    printf("║  Interactive Mode                                  ║\n");
    printf("╚════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("Type messages to send. Press Ctrl+C to exit.\n");
    printf("Received data will be displayed automatically.\n");
    printf("\n");

    // Set stdin to non-blocking
    int stdin_flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, stdin_flags | O_NONBLOCK);

    while (1) {
        // Check for incoming serial data
        bytes_read = serial_read_timeout(fd, rx_buffer, BUFFER_SIZE - 1, 0);
        if (bytes_read > 0) {
            rx_buffer[bytes_read] = '\0';
            printf("%s<< RX:%s %s\n", COLOR_CYAN, COLOR_RESET, rx_buffer);
            fflush(stdout);
        }

        // Check for user input
        if (fgets(tx_buffer, BUFFER_SIZE, stdin) != NULL) {
            size_t len = strlen(tx_buffer);
            if (len > 0) {
                printf("%s>> TX:%s %s", COLOR_BLUE, COLOR_RESET, tx_buffer);
                serial_write(fd, tx_buffer, len);
            }
        }

        // Small delay to avoid busy waiting
        usleep(10000); // 10ms
    }

    // Restore stdin flags (won't be reached due to Ctrl+C, but good practice)
    fcntl(STDIN_FILENO, F_SETFL, stdin_flags);
}

/**
 * Print usage information
 */
void print_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] [DEVICE]\n", program_name);
    printf("\n");
    printf("Options:\n");
    printf("  -h, --help         Show this help message\n");
    printf("  -i, --interactive  Run in interactive mode (default: echo test)\n");
    printf("\n");
    printf("Arguments:\n");
    printf("  DEVICE            Serial device path (default: /dev/serial0)\n");
    printf("\n");
    printf("Examples:\n");
    printf("  %s                              # Echo test on /dev/serial0\n", program_name);
    printf("  %s --interactive                # Interactive mode\n", program_name);
    printf("  %s /dev/ttyUSB0                # Echo test on USB serial\n", program_name);
    printf("  %s --interactive /dev/ttyAMA0  # Interactive on hardware UART\n", program_name);
    printf("\n");
    printf("Common serial devices:\n");
    printf("  /dev/serial0   - Primary UART (recommended)\n");
    printf("  /dev/ttyAMA0   - Hardware UART (GPIO 14/15)\n");
    printf("  /dev/ttyS0     - Mini UART or Bluetooth\n");
    printf("  /dev/ttyUSB0   - USB-to-Serial adapter\n");
    printf("  /dev/ttyACM0   - USB CDC ACM device\n");
    printf("\n");
}
