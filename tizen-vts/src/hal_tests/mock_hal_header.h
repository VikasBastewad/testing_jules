#ifndef MOCK_HAL_HEADER_H
#define MOCK_HAL_HEADER_H

#include <string>

// Define a simple namespace for our mock HAL
namespace mock_hal {

// Enum for device status
enum class DeviceStatus {
    OFF,
    INITIALIZING,
    ON,
    ERROR
};

// Mock HAL Functions
// These functions simulate interactions with a hardware component.

/**
 * @brief Powers on the mock hardware device.
 * @return True if power on sequence initiated successfully, false otherwise.
 */
bool hal_power_on();

/**
 * @brief Powers off the mock hardware device.
 * @return True if power off sequence initiated successfully, false otherwise.
 */
bool hal_power_off();

/**
 * @brief Gets the current status of the mock hardware device.
 * @return Current DeviceStatus.
 */
DeviceStatus hal_get_status();

/**
 * @brief Sets a configuration value for the mock device.
 * @param key The configuration key (string).
 * @param value The configuration value (integer).
 * @return True if configuration was set successfully, false otherwise.
 */
bool hal_set_config(const std::string& key, int value);

/**
 * @brief Gets a configuration value from the mock device.
 * @param key The configuration key (string).
 * @param[out] value The integer value to be filled.
 * @return True if configuration was retrieved successfully, false otherwise.
 */
bool hal_get_config(const std::string& key, int& value);

// --- Implementation of Mock HAL Functions ---
// In a real scenario, these would interact with actual hardware drivers or services.
// For this mock, we'll provide simple in-line implementations.

static DeviceStatus current_status = DeviceStatus::OFF;
static int mock_config_value = 0;

inline bool hal_power_on() {
    if (current_status == DeviceStatus::OFF || current_status == DeviceStatus::ERROR) {
        current_status = DeviceStatus::INITIALIZING;
        // Simulate some delay or process
        current_status = DeviceStatus::ON;
        return true;
    }
    return false; // Already on or initializing
}

inline bool hal_power_off() {
    if (current_status == DeviceStatus::ON) {
        current_status = DeviceStatus::OFF;
        return true;
    }
    return false; // Already off or in error
}

inline DeviceStatus hal_get_status() {
    return current_status;
}

inline bool hal_set_config(const std::string& key, int value) {
    if (key == "TARGET_VOLTAGE") {
        mock_config_value = value;
        return true;
    }
    return false; // Unknown config key
}

inline bool hal_get_config(const std::string& key, int& value) {
    if (key == "TARGET_VOLTAGE") {
        value = mock_config_value;
        return true;
    }
    return false; // Unknown config key
}

} // namespace mock_hal

#endif // MOCK_HAL_HEADER_H
