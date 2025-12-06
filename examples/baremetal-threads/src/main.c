/**
 * Multi-Threading Example - Producer-Consumer Pattern
 *
 * This example demonstrates POSIX threads (pthreads) on Linux ARM platforms.
 * It implements a classic producer-consumer pattern with proper synchronization.
 *
 * Key Concepts Demonstrated:
 * - Thread creation and management (pthread_create, pthread_join)
 * - Mutex locks for thread-safe data access (pthread_mutex)
 * - Condition variables for inter-thread signaling (pthread_cond)
 * - Proper resource cleanup and error handling
 * - Shared data structures with concurrent access
 *
 * Use Cases:
 * - Concurrent GPIO monitoring (multiple buttons/sensors)
 * - Background data processing while handling UI
 * - Parallel sensor polling (I2C + SPI simultaneously)
 * - Responsive applications (non-blocking operations)
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>
#include <string.h>

/* ============================================================================
 * Configuration Constants
 * ============================================================================ */

#define NUM_PRODUCERS       2      // Number of producer threads
#define NUM_CONSUMERS       3      // Number of consumer threads
#define ITEMS_PER_PRODUCER  10     // Items each producer will generate
#define QUEUE_SIZE          5      // Maximum items in queue (bounded buffer)

/* ============================================================================
 * Shared Data Structure - Circular Queue
 * ============================================================================ */

/**
 * Thread-safe circular queue for producer-consumer pattern
 * All access must be protected by the associated mutex
 */
typedef struct {
    int buffer[QUEUE_SIZE];     // Circular buffer for items
    int head;                    // Index for next item to consume
    int tail;                    // Index for next item to produce
    int count;                   // Current number of items in queue
    bool done;                   // Signal that all production is complete

    pthread_mutex_t mutex;       // Protects all queue data
    pthread_cond_t not_empty;    // Signals consumers when items available
    pthread_cond_t not_full;     // Signals producers when space available
} shared_queue_t;

/* Global shared queue - accessed by all threads */
static shared_queue_t queue;

/* Thread statistics for demonstration */
static int items_produced = 0;
static int items_consumed = 0;
static pthread_mutex_t stats_mutex = PTHREAD_MUTEX_INITIALIZER;

/* ============================================================================
 * Queue Operations - Thread-Safe
 * ============================================================================ */

/**
 * Initialize the shared queue
 * Must be called before any threads are created
 */
void queue_init(shared_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->done = false;

    // Initialize mutex and condition variables
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

/**
 * Destroy the queue and free resources
 * Must be called after all threads have finished
 */
void queue_destroy(shared_queue_t *q) {
    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
}

/**
 * Add an item to the queue (thread-safe)
 * Blocks if queue is full until space becomes available
 *
 * @param q     Pointer to the shared queue
 * @param item  Item to add
 */
void queue_put(shared_queue_t *q, int item) {
    pthread_mutex_lock(&q->mutex);

    // Wait while queue is full
    // CRITICAL: Must use 'while' not 'if' to handle spurious wakeups
    while (q->count == QUEUE_SIZE) {
        pthread_cond_wait(&q->not_full, &q->mutex);
    }

    // Add item to tail of queue
    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % QUEUE_SIZE;  // Circular wrap-around
    q->count++;

    // Signal consumers that item is available
    pthread_cond_signal(&q->not_empty);

    pthread_mutex_unlock(&q->mutex);
}

/**
 * Remove an item from the queue (thread-safe)
 * Blocks if queue is empty until item becomes available or production done
 *
 * @param q     Pointer to the shared queue
 * @param item  Pointer to store retrieved item
 * @return      true if item retrieved, false if production complete and queue empty
 */
bool queue_get(shared_queue_t *q, int *item) {
    pthread_mutex_lock(&q->mutex);

    // Wait while queue is empty AND production not finished
    // CRITICAL: Must use 'while' not 'if' to handle spurious wakeups
    while (q->count == 0 && !q->done) {
        pthread_cond_wait(&q->not_empty, &q->mutex);
    }

    // If queue empty and production done, no more items
    if (q->count == 0 && q->done) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    // Remove item from head of queue
    *item = q->buffer[q->head];
    q->head = (q->head + 1) % QUEUE_SIZE;  // Circular wrap-around
    q->count--;

    // Signal producers that space is available
    pthread_cond_signal(&q->not_full);

    pthread_mutex_unlock(&q->mutex);
    return true;
}

/**
 * Mark production as complete
 * Signals all waiting consumers to check for completion
 */
void queue_mark_done(shared_queue_t *q) {
    pthread_mutex_lock(&q->mutex);
    q->done = true;

    // Broadcast to ALL waiting consumers (not just one)
    pthread_cond_broadcast(&q->not_empty);

    pthread_mutex_unlock(&q->mutex);
}

/* ============================================================================
 * Thread Functions
 * ============================================================================ */

/**
 * Producer thread function
 * Generates items and adds them to the shared queue
 *
 * @param arg   Thread ID (cast from void*)
 */
void* producer_thread(void *arg) {
    int thread_id = *(int*)arg;
    free(arg);  // Free the allocated thread ID

    printf("[Producer %d] Starting...\n", thread_id);

    for (int i = 0; i < ITEMS_PER_PRODUCER; i++) {
        // Simulate work: generate an item
        // In real application: read sensor, process data, etc.
        int item = thread_id * 100 + i;

        // Simulate varying production time (50-150ms)
        usleep((50 + (rand() % 100)) * 1000);

        printf("[Producer %d] Producing item %d\n", thread_id, item);
        queue_put(&queue, item);

        // Update statistics (thread-safe)
        pthread_mutex_lock(&stats_mutex);
        items_produced++;
        pthread_mutex_unlock(&stats_mutex);
    }

    printf("[Producer %d] Finished (%d items)\n", thread_id, ITEMS_PER_PRODUCER);
    return NULL;
}

/**
 * Consumer thread function
 * Retrieves items from the shared queue and processes them
 *
 * @param arg   Thread ID (cast from void*)
 */
void* consumer_thread(void *arg) {
    int thread_id = *(int*)arg;
    free(arg);  // Free the allocated thread ID

    printf("[Consumer %d] Starting...\n", thread_id);

    int items_processed = 0;
    int item;

    // Continue until queue is empty AND production is done
    while (queue_get(&queue, &item)) {
        printf("[Consumer %d] Processing item %d\n", thread_id, item);

        // Simulate work: process the item
        // In real application: write to file, update display, send data, etc.
        usleep((100 + (rand() % 100)) * 1000);  // 100-200ms

        items_processed++;

        // Update statistics (thread-safe)
        pthread_mutex_lock(&stats_mutex);
        items_consumed++;
        pthread_mutex_unlock(&stats_mutex);
    }

    printf("[Consumer %d] Finished (%d items processed)\n", thread_id, items_processed);
    return NULL;
}

/* ============================================================================
 * Main Program
 * ============================================================================ */

int main(int argc __attribute__((unused)), char **argv __attribute__((unused))) {
    pthread_t producers[NUM_PRODUCERS];
    pthread_t consumers[NUM_CONSUMERS];
    int ret;

    // Print header
    printf("==============================================\n");
    printf("Multi-Threading Example (Producer-Consumer)\n");
    printf("==============================================\n");
    printf("Producers: %d (each producing %d items)\n", NUM_PRODUCERS, ITEMS_PER_PRODUCER);
    printf("Consumers: %d\n", NUM_CONSUMERS);
    printf("Queue Size: %d items\n", QUEUE_SIZE);
    printf("==============================================\n\n");

    // Seed random number generator
    srand(time(NULL));

    // Initialize shared queue
    queue_init(&queue);

    /* ------------------------------------------------------------------------
     * Create Producer Threads
     * ------------------------------------------------------------------------ */

    printf("Main: Creating %d producer threads...\n", NUM_PRODUCERS);
    for (int i = 0; i < NUM_PRODUCERS; i++) {
        // Allocate thread ID on heap (freed by thread)
        int *thread_id = malloc(sizeof(int));
        if (thread_id == NULL) {
            fprintf(stderr, "Error: Failed to allocate thread ID\n");
            exit(EXIT_FAILURE);
        }
        *thread_id = i + 1;

        ret = pthread_create(&producers[i], NULL, producer_thread, thread_id);
        if (ret != 0) {
            fprintf(stderr, "Error: pthread_create() failed: %s\n", strerror(ret));
            exit(EXIT_FAILURE);
        }
    }

    /* ------------------------------------------------------------------------
     * Create Consumer Threads
     * ------------------------------------------------------------------------ */

    printf("Main: Creating %d consumer threads...\n", NUM_CONSUMERS);
    for (int i = 0; i < NUM_CONSUMERS; i++) {
        // Allocate thread ID on heap (freed by thread)
        int *thread_id = malloc(sizeof(int));
        if (thread_id == NULL) {
            fprintf(stderr, "Error: Failed to allocate thread ID\n");
            exit(EXIT_FAILURE);
        }
        *thread_id = i + 1;

        ret = pthread_create(&consumers[i], NULL, consumer_thread, thread_id);
        if (ret != 0) {
            fprintf(stderr, "Error: pthread_create() failed: %s\n", strerror(ret));
            exit(EXIT_FAILURE);
        }
    }

    printf("Main: All threads created. Work in progress...\n\n");

    /* ------------------------------------------------------------------------
     * Wait for All Producers to Finish
     * ------------------------------------------------------------------------ */

    for (int i = 0; i < NUM_PRODUCERS; i++) {
        ret = pthread_join(producers[i], NULL);
        if (ret != 0) {
            fprintf(stderr, "Error: pthread_join() failed: %s\n", strerror(ret));
            exit(EXIT_FAILURE);
        }
    }

    printf("\nMain: All producers finished. Signaling consumers...\n");

    // Mark production as complete so consumers can exit
    queue_mark_done(&queue);

    /* ------------------------------------------------------------------------
     * Wait for All Consumers to Finish
     * ------------------------------------------------------------------------ */

    for (int i = 0; i < NUM_CONSUMERS; i++) {
        ret = pthread_join(consumers[i], NULL);
        if (ret != 0) {
            fprintf(stderr, "Error: pthread_join() failed: %s\n", strerror(ret));
            exit(EXIT_FAILURE);
        }
    }

    /* ------------------------------------------------------------------------
     * Cleanup and Summary
     * ------------------------------------------------------------------------ */

    printf("\n==============================================\n");
    printf("Summary\n");
    printf("==============================================\n");
    printf("Total items produced: %d\n", items_produced);
    printf("Total items consumed: %d\n", items_consumed);
    printf("Expected total: %d\n", NUM_PRODUCERS * ITEMS_PER_PRODUCER);

    if (items_produced == items_consumed &&
        items_produced == NUM_PRODUCERS * ITEMS_PER_PRODUCER) {
        printf("SUCCESS: All items produced and consumed!\n");
    } else {
        printf("ERROR: Mismatch in produced/consumed counts!\n");
    }
    printf("==============================================\n");

    // Clean up resources
    queue_destroy(&queue);
    pthread_mutex_destroy(&stats_mutex);

    printf("\nMain: All threads joined. Exiting.\n");
    return 0;
}
