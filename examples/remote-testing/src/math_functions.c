/*
 * Math functions for testing
 * This module demonstrates testable code that can be validated
 * both locally and on remote hardware.
 */

#include "math_functions.h"

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    if (b == 0) {
        return -1; // Error: division by zero
    }
    return a / b;
}

int factorial(int n) {
    if (n < 0) {
        return -1; // Error: negative input
    }
    if (n == 0 || n == 1) {
        return 1;
    }
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}
