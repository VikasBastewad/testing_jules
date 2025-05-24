#include "gtest/gtest.h"
#include "mock_hal_header.h" // Our mock HAL interface

// Test fixture for HAL tests
class SampleHALTest : public ::testing::Test {
protected:
    // You can define per-test set-up logic here.
    // Executed before each test in the test suite.
    void SetUp() override {
        // Ensure device is off before each test that might turn it on.
        // This provides a consistent starting state.
        if (mock_hal::hal_get_status() != mock_hal::DeviceStatus::OFF) {
            mock_hal::hal_power_off();
        }
        // Reset any mock configurations
        mock_hal::hal_set_config("TARGET_VOLTAGE", 0);
    }

    // You can define per-test tear-down logic here.
    // Executed after each test in the test suite.
    void TearDown() override {
        // Example: ensure the mock device is powered off after tests.
        if (mock_hal::hal_get_status() == mock_hal::DeviceStatus::ON) {
            mock_hal::hal_power_off();
        }
    }
};

// Test case for hal_power_on
TEST_F(SampleHALTest, PowerOn) {
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF);
    EXPECT_TRUE(mock_hal::hal_power_on());
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);
}

// Test case for hal_power_off
TEST_F(SampleHALTest, PowerOff) {
    // First, ensure it's on
    mock_hal::hal_power_on();
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);

    EXPECT_TRUE(mock_hal::hal_power_off());
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF);
}

// Test case for hal_get_status
TEST_F(SampleHALTest, GetStatus) {
    // Initial state
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF);

    mock_hal::hal_power_on();
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);

    mock_hal::hal_power_off();
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF);
}

// Test case for re-powering on and off
TEST_F(SampleHALTest, PowerCycle) {
    ASSERT_TRUE(mock_hal::hal_power_on());
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);
    ASSERT_TRUE(mock_hal::hal_power_off());
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF);

    // Try again
    ASSERT_TRUE(mock_hal::hal_power_on());
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);
}

// Test case for hal_set_config and hal_get_config
TEST_F(SampleHALTest, SetAndGetConfig) {
    int value_to_set = 120;
    int retrieved_value = 0;

    // Set a known config
    EXPECT_TRUE(mock_hal::hal_set_config("TARGET_VOLTAGE", value_to_set));
    
    // Get the config and check its value
    EXPECT_TRUE(mock_hal::hal_get_config("TARGET_VOLTAGE", retrieved_value));
    EXPECT_EQ(retrieved_value, value_to_set);

    // Try to set an unknown config
    EXPECT_FALSE(mock_hal::hal_set_config("UNKNOWN_CONFIG", 99));

    // Try to get an unknown config
    int unknown_value = 0;
    EXPECT_FALSE(mock_hal::hal_get_config("NON_EXISTENT_CONFIG", unknown_value));
}

// Test case for attempting to power on when already on
TEST_F(SampleHALTest, PowerOnWhenAlreadyOn) {
    mock_hal::hal_power_on(); // Turn on
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON);
    EXPECT_FALSE(mock_hal::hal_power_on()); // Attempt to turn on again
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::ON); // Should still be ON
}

// Test case for attempting to power off when already off
TEST_F(SampleHALTest, PowerOffWhenAlreadyOff) {
    ASSERT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF); // Ensure it's off
    EXPECT_FALSE(mock_hal::hal_power_off()); // Attempt to turn off again
    EXPECT_EQ(mock_hal::hal_get_status(), mock_hal::DeviceStatus::OFF); // Should still be OFF
}

// Entry point for running the tests (if not using GTest_Main library)
// int main(int argc, char **argv) {
//   ::testing::InitGoogleTest(&argc, argv);
//   return RUN_ALL_TESTS();
// }
// We are using GTest::gtest_main, so this main is not needed.
