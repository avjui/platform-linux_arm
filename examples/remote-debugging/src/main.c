/**
 * Remote Debugging Example for PlatformIO Linux ARM
 *
 * This example demonstrates debugging features including:
 * - Breakpoints
 * - Variable inspection
 * - Step-through debugging
 * - Call stack analysis
 *
 * Build with debug symbols: pio run
 * Upload to target: pio run --target upload
 * Start debugging: pio debug
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

// Structure to demonstrate variable inspection
typedef struct {
    int x;
    int y;
    char name[32];
} Point;

// Global variable for inspection
int global_counter = 0;

/**
 * Calculate factorial recursively (demonstrates call stack)
 */
unsigned long long factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);  // Set breakpoint here to see call stack
}

/**
 * Process a point structure (demonstrates struct inspection)
 */
void process_point(Point *p) {
    printf("Processing point: %s at (%d, %d)\n", p->name, p->x, p->y);

    // Calculate distance from origin
    double distance = (p->x * p->x) + (p->y * p->y);
    printf("  Distance squared from origin: %.2f\n", distance);

    // Increment global counter
    global_counter++;
}

/**
 * Demonstrate array processing
 */
void process_array(int *arr, int size) {
    printf("\nProcessing array of %d elements:\n", size);

    int sum = 0;
    int max = arr[0];
    int min = arr[0];

    for (int i = 0; i < size; i++) {  // Set breakpoint here to inspect loop variables
        sum += arr[i];
        if (arr[i] > max) max = arr[i];
        if (arr[i] < min) min = arr[i];

        printf("  [%d] = %d (sum so far: %d)\n", i, arr[i], sum);
    }

    printf("  Sum: %d, Max: %d, Min: %d, Avg: %.2f\n",
           sum, max, min, (double)sum / size);
}

/**
 * Simulate a potential bug (divide by zero)
 */
int buggy_function(int a, int b) {
    // This will crash if b is zero - good for debugging practice
    int result = a / b;  // Set breakpoint before this line to inspect variables
    return result;
}

/**
 * Main function - demonstrates various debugging scenarios
 */
int main(int argc, char *argv[]) {
    printf("=================================================\n");
    printf("PlatformIO Remote Debugging Example\n");
    printf("=================================================\n\n");

    // Print process information
    printf("Process ID: %d\n", getpid());
    printf("Arguments: %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("  argv[%d] = %s\n", i, argv[i]);
    }
    printf("\n");

    // Debugging scenario 1: Variable inspection
    printf("--- Scenario 1: Variable Inspection ---\n");
    int local_var = 42;
    double pi = 3.14159;
    const char *message = "Hello, Debugger!";

    printf("local_var = %d\n", local_var);      // Set breakpoint here
    printf("pi = %.5f\n", pi);
    printf("message = %s\n", message);
    printf("\n");

    // Debugging scenario 2: Struct inspection
    printf("--- Scenario 2: Struct Inspection ---\n");
    Point p1 = {10, 20, "Origin Point"};
    Point p2 = {-5, 15, "Sample Point"};

    process_point(&p1);  // Set breakpoint in this function
    process_point(&p2);
    printf("Total points processed: %d\n\n", global_counter);

    // Debugging scenario 3: Array processing
    printf("--- Scenario 3: Array Processing ---\n");
    int numbers[] = {5, 12, 8, 23, 3, 18, 7, 15};
    int array_size = sizeof(numbers) / sizeof(numbers[0]);

    process_array(numbers, array_size);  // Set breakpoint in loop
    printf("\n");

    // Debugging scenario 4: Recursive function (call stack)
    printf("--- Scenario 4: Call Stack Analysis ---\n");
    int n = 5;
    unsigned long long result = factorial(n);  // Step into to see recursion
    printf("Factorial of %d = %llu\n\n", n, result);

    // Debugging scenario 5: Conditional debugging
    printf("--- Scenario 5: Conditional Breakpoints ---\n");
    for (int i = 0; i < 10; i++) {
        int square = i * i;
        printf("i=%d, square=%d\n", i, square);
        // Try setting a conditional breakpoint: "break main.c:144 if i == 5"
        if (i == 5) {
            printf("  -> Halfway point!\n");  // Breakpoint here with condition
        }
    }
    printf("\n");

    // Debugging scenario 6: Time-based loop (for stepping practice)
    printf("--- Scenario 6: Step-Through Debugging ---\n");
    printf("Counting down from 5...\n");
    for (int i = 5; i > 0; i--) {
        printf("  %d...\n", i);
        sleep(1);  // Step through this to practice debugging controls
    }
    printf("  Blast off!\n\n");

    // Debugging scenario 7: Function with potential bug
    printf("--- Scenario 7: Bug Investigation ---\n");
    int dividend = 100;
    int divisor = 5;

    printf("Safe division: %d / %d = %d\n",
           dividend, divisor, buggy_function(dividend, divisor));

    // Uncomment to trigger a bug (divide by zero):
    // divisor = 0;
    // printf("Unsafe division: %d / %d = %d\n",
    //        dividend, divisor, buggy_function(dividend, divisor));

    printf("\n");

    // Debugging scenario 8: Memory inspection
    printf("--- Scenario 8: Memory Inspection ---\n");
    int *dynamic_array = (int *)malloc(5 * sizeof(int));
    if (dynamic_array == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        return 1;
    }

    for (int i = 0; i < 5; i++) {
        dynamic_array[i] = i * 10;
    }

    printf("Dynamic array contents:\n");
    for (int i = 0; i < 5; i++) {
        printf("  dynamic_array[%d] = %d (address: %p)\n",
               i, dynamic_array[i], (void *)&dynamic_array[i]);
    }

    free(dynamic_array);
    printf("\n");

    // Final summary
    printf("=================================================\n");
    printf("Debugging example completed successfully!\n");
    printf("=================================================\n\n");

    printf("Debugging Tips:\n");
    printf("1. Set breakpoint in main: (gdb) break main\n");
    printf("2. Set breakpoint at line: (gdb) break main.c:144\n");
    printf("3. Conditional breakpoint: (gdb) break main.c:144 if i == 5\n");
    printf("4. Inspect variable: (gdb) print local_var\n");
    printf("5. Inspect struct: (gdb) print p1\n");
    printf("6. Watch variable: (gdb) watch global_counter\n");
    printf("7. Step into function: (gdb) step\n");
    printf("8. Step over function: (gdb) next\n");
    printf("9. Continue execution: (gdb) continue\n");
    printf("10. View call stack: (gdb) backtrace\n");

    return 0;
}
