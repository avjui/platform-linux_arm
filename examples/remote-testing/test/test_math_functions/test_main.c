/*
 * Unit Tests for Math Functions
 *
 * These tests demonstrate remote test execution on Linux ARM targets.
 * Tests are built on the host (macOS/Linux x86_64), cross-compiled for ARM,
 * uploaded to the target device via SSH, and executed remotely.
 *
 * Test Framework: Unity (PlatformIO's default)
 */

#include <unity.h>
#include "math_functions.h"

// Unity test framework requires these functions
void setUp(void) {
    // This function runs before each test
}

void tearDown(void) {
    // This function runs after each test
}

// Test: Addition
void test_add_positive_numbers(void) {
    TEST_ASSERT_EQUAL(8, add(5, 3));
    TEST_ASSERT_EQUAL(100, add(75, 25));
    TEST_ASSERT_EQUAL(0, add(0, 0));
}

void test_add_negative_numbers(void) {
    TEST_ASSERT_EQUAL(-8, add(-5, -3));
    TEST_ASSERT_EQUAL(2, add(-5, 7));
    TEST_ASSERT_EQUAL(-2, add(5, -7));
}

// Test: Subtraction
void test_subtract_positive_numbers(void) {
    TEST_ASSERT_EQUAL(2, subtract(5, 3));
    TEST_ASSERT_EQUAL(50, subtract(75, 25));
    TEST_ASSERT_EQUAL(0, subtract(10, 10));
}

void test_subtract_negative_numbers(void) {
    TEST_ASSERT_EQUAL(-2, subtract(-5, -3));
    TEST_ASSERT_EQUAL(-12, subtract(-5, 7));
    TEST_ASSERT_EQUAL(12, subtract(5, -7));
}

// Test: Multiplication
void test_multiply_positive_numbers(void) {
    TEST_ASSERT_EQUAL(15, multiply(5, 3));
    TEST_ASSERT_EQUAL(1875, multiply(75, 25));
    TEST_ASSERT_EQUAL(0, multiply(0, 100));
}

void test_multiply_negative_numbers(void) {
    TEST_ASSERT_EQUAL(15, multiply(-5, -3));
    TEST_ASSERT_EQUAL(-35, multiply(-5, 7));
    TEST_ASSERT_EQUAL(-35, multiply(5, -7));
}

// Test: Division
void test_divide_positive_numbers(void) {
    TEST_ASSERT_EQUAL(2, divide(6, 3));
    TEST_ASSERT_EQUAL(5, divide(25, 5));
    TEST_ASSERT_EQUAL(1, divide(10, 10));
}

void test_divide_by_zero(void) {
    TEST_ASSERT_EQUAL(-1, divide(10, 0));
    TEST_ASSERT_EQUAL(-1, divide(0, 0));
}

// Test: Factorial
void test_factorial_base_cases(void) {
    TEST_ASSERT_EQUAL(1, factorial(0));
    TEST_ASSERT_EQUAL(1, factorial(1));
}

void test_factorial_positive_numbers(void) {
    TEST_ASSERT_EQUAL(2, factorial(2));
    TEST_ASSERT_EQUAL(6, factorial(3));
    TEST_ASSERT_EQUAL(24, factorial(4));
    TEST_ASSERT_EQUAL(120, factorial(5));
}

void test_factorial_negative_input(void) {
    TEST_ASSERT_EQUAL(-1, factorial(-1));
    TEST_ASSERT_EQUAL(-1, factorial(-10));
}

// Main function - runs all tests
int main(int argc, char **argv) {
    UNITY_BEGIN();

    // Addition tests
    RUN_TEST(test_add_positive_numbers);
    RUN_TEST(test_add_negative_numbers);

    // Subtraction tests
    RUN_TEST(test_subtract_positive_numbers);
    RUN_TEST(test_subtract_negative_numbers);

    // Multiplication tests
    RUN_TEST(test_multiply_positive_numbers);
    RUN_TEST(test_multiply_negative_numbers);

    // Division tests
    RUN_TEST(test_divide_positive_numbers);
    RUN_TEST(test_divide_by_zero);

    // Factorial tests
    RUN_TEST(test_factorial_base_cases);
    RUN_TEST(test_factorial_positive_numbers);
    RUN_TEST(test_factorial_negative_input);

    return UNITY_END();
}
