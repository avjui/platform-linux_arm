/**
 * PWM Hardware Abstraction Layer (HAL) for Linux ARM Platform
 *
 * Provides user-friendly PWM control using the Linux kernel PWM subsystem
 * via sysfs (/sys/class/pwm). Works on all Raspberry Pi models (1-5).
 *
 * Features:
 * - GPIO pin-based API (automatic chip/channel mapping)
 * - Hardware PWM support (no CPU overhead)
 * - Frequency and duty cycle control
 * - Polarity configuration (normal/inverted)
 * - Comprehensive error handling
 *
 * Hardware Requirements:
 * - Device tree PWM overlay enabled (pwm or pwm-2chan)
 * - Proper permissions on /sys/class/pwm (see docs/PWM_SETUP.md)
 *
 * Example usage:
 *   pwm_init(18, 1000);              // Init GPIO 18 at 1 kHz
 *   pwm_write(18, 50.0);             // 50% duty cycle
 *   pwm_set_frequency(18, 2000);     // Change to 2 kHz
 *   pwm_deinit(18);                  // Cleanup
 *
 * @file pwm-hal.h
 * @author PlatformIO Linux ARM Platform
 * @version 1.0.0
 * @date 2025-11-12
 */

#ifndef PWM_HAL_H
#define PWM_HAL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief PWM operation return codes
 */
typedef enum {
    PWM_SUCCESS = 0,              /**< Operation completed successfully */
    PWM_ERROR_INVALID_PIN = -1,   /**< GPIO pin does not support PWM */
    PWM_ERROR_PERMISSION = -2,    /**< Permission denied (see setup-pwm-perms.sh) */
    PWM_ERROR_BUSY = -3,          /**< PWM channel already in use */
    PWM_ERROR_NOT_EXPORTED = -4,  /**< PWM channel not exported */
    PWM_ERROR_INVALID_PARAM = -5, /**< Invalid parameter value */
    PWM_ERROR_IO = -6,            /**< I/O error accessing sysfs */
    PWM_ERROR_NOT_ENABLED = -7,   /**< PWM channel not enabled */
    PWM_ERROR_HARDWARE = -8       /**< Hardware-specific limitation */
} pwm_error_t;

/**
 * @brief PWM polarity modes
 */
typedef enum {
    PWM_POLARITY_NORMAL = 0,   /**< High voltage = active (default) */
    PWM_POLARITY_INVERTED = 1  /**< Low voltage = active (inverted) */
} pwm_polarity_t;

/**
 * @brief PWM channel status information
 */
typedef struct {
    int gpio_pin;              /**< GPIO pin number (BCM) */
    int pwm_chip;              /**< PWM chip number (e.g., 0 for pwmchip0) */
    int pwm_channel;           /**< PWM channel within chip (0 or 1) */
    bool is_enabled;           /**< PWM output enabled */
    bool is_exported;          /**< Channel exported to userspace */
    uint32_t frequency_hz;     /**< Current frequency in Hz */
    float duty_cycle_percent;  /**< Current duty cycle (0.0-100.0%) */
    pwm_polarity_t polarity;   /**< Current polarity setting */
    uint64_t period_ns;        /**< Period in nanoseconds */
    uint64_t duty_cycle_ns;    /**< Duty cycle in nanoseconds */
} pwm_status_t;

/**
 * @brief Hardware limits for PWM operation
 *
 * These limits vary by Raspberry Pi model and PWM hardware.
 * Consult docs/PWM_SETUP.md for model-specific details.
 */
#define PWM_MIN_FREQUENCY_HZ    1       /**< Minimum frequency (1 Hz) */
#define PWM_MAX_FREQUENCY_HZ    100000000  /**< Maximum frequency (100 MHz theoretical) */
#define PWM_MIN_DUTY_CYCLE      0.0f    /**< Minimum duty cycle (0%) */
#define PWM_MAX_DUTY_CYCLE      100.0f  /**< Maximum duty cycle (100%) */

/* ============================================================================
 * Core PWM API Functions
 * ============================================================================ */

/**
 * @brief Initialize PWM on a GPIO pin with specified frequency
 *
 * Maps the GPIO pin to the appropriate PWM chip/channel, exports the channel
 * to userspace, and configures the initial frequency. The duty cycle is set
 * to 0% and the output is enabled.
 *
 * Supported GPIO pins (Pi 1-4):
 * - GPIO 12 (PWM0, pwmchip0 channel 0)
 * - GPIO 13 (PWM1, pwmchip0 channel 1)
 * - GPIO 18 (PWM0, pwmchip0 channel 0)
 * - GPIO 19 (PWM1, pwmchip0 channel 1)
 *
 * Supported GPIO pins (Pi 5):
 * - GPIO 12 (PWM0, pwmchip2 channel 0)
 * - GPIO 13 (PWM1, pwmchip2 channel 1)
 * - GPIO 18 (PWM0, pwmchip2 channel 0)
 * - GPIO 19 (PWM1, pwmchip2 channel 1)
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param freq_hz Frequency in Hz (1 Hz to 100 MHz, hardware-limited)
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note Requires PWM device tree overlay and proper permissions
 * @see pwm_deinit() to release the PWM channel
 */
int pwm_init(int pin, uint32_t freq_hz);

/**
 * @brief Set PWM duty cycle as a percentage
 *
 * Adjusts the duty cycle (pulse width) while maintaining the current frequency.
 * The duty cycle determines the average power delivered to the load.
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param duty_cycle_percent Duty cycle percentage (0.0 to 100.0)
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note Pin must be initialized with pwm_init() first
 * @note 0% = always off, 100% = always on, 50% = half power
 */
int pwm_write(int pin, float duty_cycle_percent);

/**
 * @brief Disable and release PWM channel
 *
 * Disables the PWM output, unexports the channel from userspace, and releases
 * all resources. After calling this function, the pin returns to GPIO mode.
 *
 * @param pin GPIO pin number (BCM numbering)
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note Safe to call even if pwm_init() failed or was not called
 */
int pwm_deinit(int pin);

/* ============================================================================
 * Extended PWM API Functions
 * ============================================================================ */

/**
 * @brief Change PWM frequency without changing duty cycle
 *
 * Adjusts the frequency while maintaining the current duty cycle percentage.
 * Useful for applications requiring dynamic frequency control (e.g., servo
 * sweep, motor speed control).
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param freq_hz New frequency in Hz (1 Hz to 100 MHz, hardware-limited)
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note Pin must be initialized with pwm_init() first
 * @note Changing frequency may introduce glitches in the output signal
 */
int pwm_set_frequency(int pin, uint32_t freq_hz);

/**
 * @brief Set PWM output polarity (normal or inverted)
 *
 * Changes the polarity of the PWM signal:
 * - NORMAL: High voltage during duty cycle (default)
 * - INVERTED: Low voltage during duty cycle
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param polarity PWM_POLARITY_NORMAL or PWM_POLARITY_INVERTED
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note Polarity can only be changed when PWM output is disabled
 * @note This function temporarily disables and re-enables the output
 */
int pwm_set_polarity(int pin, pwm_polarity_t polarity);

/**
 * @brief Query current PWM status and configuration
 *
 * Retrieves detailed information about the PWM channel including frequency,
 * duty cycle, polarity, and enable state. Useful for debugging and monitoring.
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param status Pointer to pwm_status_t structure to fill
 * @return PWM_SUCCESS on success, error code on failure
 *
 * @note status parameter must not be NULL
 */
int pwm_get_status(int pin, pwm_status_t *status);

/**
 * @brief Check if PWM channel is enabled
 *
 * Quick check to determine if a PWM channel is currently active and outputting
 * a signal.
 *
 * @param pin GPIO pin number (BCM numbering)
 * @return true if enabled, false if disabled or not initialized
 */
bool pwm_is_enabled(int pin);

/* ============================================================================
 * Utility Functions
 * ============================================================================ */

/**
 * @brief Get human-readable error message
 *
 * Converts a PWM error code to a descriptive error message for debugging
 * and user feedback.
 *
 * @param error Error code returned by PWM functions
 * @return Pointer to static error message string
 */
const char* pwm_error_string(pwm_error_t error);

/**
 * @brief Check if a GPIO pin supports PWM
 *
 * Validates that a GPIO pin can be used for hardware PWM on the current
 * Raspberry Pi model.
 *
 * @param pin GPIO pin number (BCM numbering)
 * @return true if pin supports PWM, false otherwise
 */
bool pwm_pin_is_valid(int pin);

/**
 * @brief Get PWM chip and channel for a GPIO pin
 *
 * Maps a GPIO pin to the corresponding PWM chip and channel. This mapping
 * varies by Raspberry Pi model (Pi 1-4 use pwmchip0, Pi 5 uses pwmchip2/3).
 *
 * @param pin GPIO pin number (BCM numbering)
 * @param chip Pointer to store PWM chip number (output parameter)
 * @param channel Pointer to store PWM channel number (output parameter)
 * @return PWM_SUCCESS on success, PWM_ERROR_INVALID_PIN if not a PWM pin
 *
 * @note chip and channel parameters must not be NULL
 */
int pwm_get_chip_channel(int pin, int *chip, int *channel);

#ifdef __cplusplus
}
#endif

#endif /* PWM_HAL_H */
