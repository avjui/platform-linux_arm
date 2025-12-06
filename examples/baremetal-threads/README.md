# Multi-Threading Example (Producer-Consumer Pattern)

This example demonstrates POSIX threads (pthreads) for concurrent execution on Linux ARM platforms. It implements a classic **producer-consumer pattern** with proper synchronization, showcasing fundamental multi-threading concepts for embedded Linux development.

## Description

A multi-threaded application that demonstrates:
- **Thread creation and management** (`pthread_create`, `pthread_join`)
- **Mutex locks** for thread-safe data access (`pthread_mutex`)
- **Condition variables** for inter-thread signaling (`pthread_cond`)
- **Shared data structures** with concurrent access (circular queue)
- **Proper resource cleanup** and error handling
- **Producer-consumer pattern** with bounded buffer

### What It Does

- Creates **2 producer threads** that generate items (simulating sensor readings, GPIO events, etc.)
- Creates **3 consumer threads** that process items (simulating data logging, display updates, etc.)
- Uses a **thread-safe circular queue** (size 5) to coordinate work
- Demonstrates proper synchronization to avoid race conditions and deadlocks
- Provides comprehensive logging to visualize concurrent execution
- Validates that all produced items are successfully consumed

## Output Example

```
==============================================
Multi-Threading Example (Producer-Consumer)
==============================================
Producers: 2 (each producing 10 items)
Consumers: 3
Queue Size: 5 items
==============================================

Main: Creating 2 producer threads...
Main: Creating 3 consumer threads...
Main: All threads created. Work in progress...

[Producer 1] Starting...
[Producer 2] Starting...
[Consumer 1] Starting...
[Consumer 2] Starting...
[Consumer 3] Starting...
[Producer 1] Producing item 100
[Consumer 1] Processing item 100
[Producer 2] Producing item 200
[Consumer 2] Processing item 200
[Producer 1] Producing item 101
[Producer 2] Producing item 201
[Consumer 3] Processing item 101
[Consumer 1] Processing item 201
...
[Producer 1] Finished (10 items)
[Producer 2] Finished (10 items)

Main: All producers finished. Signaling consumers...
[Consumer 1] Finished (7 items processed)
[Consumer 2] Finished (6 items processed)
[Consumer 3] Finished (7 items processed)

==============================================
Summary
==============================================
Total items produced: 20
Total items consumed: 20
Expected total: 20
✓ SUCCESS: All items produced and consumed!
==============================================

Main: All threads joined. Exiting.
```

## Building

```bash
# Build for Raspberry Pi 3
pio run -e raspberrypi_3b

# Build for Raspberry Pi 4
pio run -e raspberrypi_4b

# Build for Raspberry Pi 5
pio run -e raspberrypi_5

# Clean build artifacts
pio run --target clean
```

## Running

After building, run the program on your Raspberry Pi:

```bash
# For Raspberry Pi 3
.pio/build/raspberrypi_3b/program

# For Raspberry Pi 4
.pio/build/raspberrypi_4b/program

# For Raspberry Pi 5
.pio/build/raspberrypi_5/program
```

## Threading Concepts Explained

### 1. Thread Creation

```c
pthread_t thread;
pthread_create(&thread, NULL, thread_function, arg);
```

Creates a new thread that executes `thread_function` concurrently. The `arg` parameter passes data to the thread.

### 2. Thread Synchronization

Threads need synchronization when accessing shared data to prevent **race conditions**.

#### Mutex (Mutual Exclusion)

```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

pthread_mutex_lock(&mutex);    // Acquire lock
// ... access shared data ...
pthread_mutex_unlock(&mutex);  // Release lock
```

Only one thread can hold a mutex at a time. Other threads block until the mutex is released.

#### Condition Variables

```c
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

// Wait for condition (releases mutex while waiting)
pthread_cond_wait(&cond, &mutex);

// Signal one waiting thread
pthread_cond_signal(&cond);

// Signal all waiting threads
pthread_cond_broadcast(&cond);
```

Condition variables allow threads to wait for specific conditions efficiently (e.g., "queue not empty").

### 3. Producer-Consumer Pattern

**Problem**: Producers generate data faster than consumers can process it (or vice versa).

**Solution**: Use a bounded buffer (queue) with synchronization:
- Producers **wait** when queue is full (`not_full` condition)
- Consumers **wait** when queue is empty (`not_empty` condition)
- Mutex protects queue data from concurrent access

### 4. Thread Cleanup

```c
pthread_join(thread, NULL);  // Wait for thread to finish
```

Always join threads to:
- Ensure threads complete before program exits
- Prevent resource leaks
- Retrieve thread return values (if needed)

## Common Use Cases on Raspberry Pi

### 1. Concurrent GPIO Monitoring

```c
// Thread 1: Monitor button presses
// Thread 2: Monitor motion sensor
// Thread 3: Update display with events
```

### 2. Background Data Processing

```c
// Main thread: Handle user input (responsive)
// Worker thread: Process data, compress files, etc.
```

### 3. Parallel Sensor Polling

```c
// Thread 1: Read I2C temperature sensor
// Thread 2: Read SPI accelerometer
// Thread 3: Read UART GPS module
```

### 4. Responsive Applications

```c
// UI thread: Handle button presses, update display
// Network thread: Send data to server
// Logger thread: Write data to SD card
```

## Common Pitfalls and How to Avoid Them

### 1. Race Conditions

**Problem**: Multiple threads access shared data without synchronization.

**Symptoms**: Corrupted data, inconsistent results, crashes.

**Solution**: Always protect shared data with mutexes.

```c
// No - WRONG: No mutex
shared_counter++;

// Yes - CORRECT: Mutex protection
pthread_mutex_lock(&mutex);
shared_counter++;
pthread_mutex_unlock(&mutex);
```

### 2. Deadlocks

**Problem**: Threads wait for each other indefinitely.

**Common Scenario**: Thread A holds mutex 1, waits for mutex 2. Thread B holds mutex 2, waits for mutex 1.

**Solution**:
- Always acquire mutexes in the same order
- Use `pthread_mutex_trylock()` to avoid blocking
- Keep critical sections short

### 3. Spurious Wakeups

**Problem**: `pthread_cond_wait()` can wake up without signal.

**Solution**: Always use `while` loop, never `if`:

```c
// No - WRONG: Using 'if'
if (queue_empty) {
    pthread_cond_wait(&not_empty, &mutex);
}

// Yes - CORRECT: Using 'while'
while (queue_empty) {
    pthread_cond_wait(&not_empty, &mutex);
}
```

### 4. Forgetting to Unlock Mutex

**Problem**: Thread crashes while holding mutex, leaving other threads blocked forever.

**Solution**: Use `pthread_cleanup_push/pop` for critical code, or ensure exception safety.

### 5. Memory Leaks

**Problem**: Threads created but never joined.

**Solution**: Always `pthread_join()` all threads, or create detached threads explicitly.

```c
pthread_t thread;
pthread_create(&thread, NULL, func, NULL);
// ... later ...
pthread_join(thread, NULL);  // Essential!
```

## Debugging Multi-Threaded Code

### Tools

1. **Valgrind with Helgrind**: Detects race conditions and deadlocks
   ```bash
   valgrind --tool=helgrind ./program
   ```

2. **GDB**: Debug with thread awareness
   ```bash
   gdb ./program
   (gdb) info threads      # List all threads
   (gdb) thread 2          # Switch to thread 2
   (gdb) thread apply all bt  # Backtrace all threads
   ```

3. **Print Debugging**: Add thread IDs to debug output
   ```c
   printf("[Thread %ld] Message\n", pthread_self());
   ```

### Best Practices

- Start simple: Single-threaded first, then add threading
- Minimize shared data: Use thread-local storage when possible
- Keep critical sections short: Hold mutexes for minimal time
- Test thoroughly: Multi-threading bugs are non-deterministic
- Use thread sanitizers: Compile with `-fsanitize=thread` (TSan)

## Performance Considerations

### When to Use Multi-Threading

Yes - **Good use cases**:
- I/O-bound tasks (network, disk, sensors)
- Truly parallel work (multiple CPU cores)
- Responsive UI (background processing)

No - **Poor use cases**:
- CPU-bound tasks on single-core systems
- Trivial operations (overhead > benefit)
- Simple sequential processing

### Thread Count

- **Too few threads**: Underutilize CPU cores, poor concurrency
- **Too many threads**: Context switching overhead, resource contention

**Rule of thumb**:
- I/O-bound: More threads (10-100+)
- CPU-bound: Threads ≈ CPU cores (Raspberry Pi 3/4: 4 cores)

## Advanced Topics (Not Covered)

- Thread pools
- Read-write locks (`pthread_rwlock`)
- Thread-local storage (`__thread`, `pthread_key_t`)
- Semaphores (`sem_t`)
- Thread priorities and scheduling
- Lock-free data structures (atomic operations)

## Cross-Compilation

This example can be cross-compiled from:
- Linux x86_64
- macOS (Intel or Apple Silicon)
- Windows x86_64

The `-pthread` flag in `platformio.ini` ensures proper linking of the pthread library.

## References

- **POSIX Threads Programming**: https://computing.llnl.gov/tutorials/pthreads/
- **Pthread API**: `man pthread_create`, `man pthread_mutex_lock`, etc.
- **The Linux Programming Interface** (book): Chapter 29-33

## Troubleshooting

### Build Errors

**Error**: `undefined reference to 'pthread_create'`
- **Solution**: Ensure `-pthread` flag is in `platformio.ini` build_flags

### Runtime Issues

**Deadlock** (program hangs):
- Check mutex acquisition order
- Verify condition variable usage (`while` not `if`)
- Use GDB to inspect thread states

**Assertion failure** (mismatch in counts):
- Race condition in statistics counters
- Missing mutex protection on shared data

## License

This example is part of the platform-linux_arm PlatformIO platform.

## See Also

- [Bare-Metal Hello World](../baremetal-hello/) - Simplest bare-metal example
- [lgpio Blink](../lgpio-blink/) - GPIO operations (single-threaded)
- [WiringPi Examples](../wiringpi-blink/) - GPIO with WiringPi framework
