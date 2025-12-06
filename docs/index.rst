Platform Linux ARM Documentation
================================

Welcome to the platform-linux_arm documentation for PlatformIO!

This platform enables building native applications for ARM-based Linux systems, specifically targeting Raspberry Pi devices (Pi 1-5, Pi 400, Compute Module 4, and Zero/Zero 2W).

.. contents:: Contents
    :local:
    :depth: 2

Quick Links
-----------

* **Platform Registry**: `platformio/linux_arm <https://registry.platformio.org/platforms/platformio/linux_arm>`__
* **GitHub Repository**: `platform-linux_arm <https://github.com/platformio/platform-linux_arm>`__
* **PlatformIO Home**: `platformio.org <https://platformio.org>`__

Overview
--------

**Key Features:**

* Cross-compilation support from Linux x86_64, macOS (Intel/ARM), and Windows
* Native compilation on ARM Linux systems
* Support for Raspberry Pi 1-5, Pi 400, Compute Module 4, and Zero/Zero 2W
* Modern GPIO frameworks: lgpio (Pi 5 compatible) and pigpio
* Legacy WiringPi framework for compatibility
* Bare-metal C/C++ application support
* Both 32-bit (ARMv7) and 64-bit (AArch64) architecture support

Getting Started
---------------

Installation
~~~~~~~~~~~~

Install the platform using PlatformIO CLI:

.. code-block:: bash

    # From PlatformIO registry (recommended)
    pio pkg install --global --platform platformio/linux_arm

    # Or from GitHub (development version)
    pio pkg install --global --platform https://github.com/platformio/platform-linux_arm.git

Quick Start
~~~~~~~~~~~

Create a new project:

.. code-block:: bash

    mkdir my-pi-project
    cd my-pi-project
    pio project init --board raspberrypi_5

Example ``platformio.ini``:

.. code-block:: ini

    [env:raspberrypi_5]
    platform = linux_arm
    board = raspberrypi_5
    framework = lgpio

Build your project:

.. code-block:: bash

    pio run

Documentation
-------------

Platform Reference
~~~~~~~~~~~~~~~~~~

.. toctree::
    :maxdepth: 2

    platforms/linux_arm

Additional Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

The following documentation files are available in the repository:

* **Testing Matrix** (``docs/TESTING.md``): Comprehensive testing documentation covering all boards, frameworks, and architectures
* **Troubleshooting Guide** (``docs/TROUBLESHOOTING.md``): Common issues and solutions
* **Framework Comparison** (``docs/FRAMEWORKS.md``): Detailed comparison of lgpio, pigpio, and WiringPi frameworks
* **lgpio Setup Guide** (``docs/LGPIO_SETUP.md``): Cross-compilation setup for lgpio framework
* **Documentation Plan** (``docs/DOCUMENTATION_PLAN.md``): Platform documentation roadmap

Community & Contributing
~~~~~~~~~~~~~~~~~~~~~~~~

* **Contributing Guide** (``CONTRIBUTING.md``): How to contribute to the platform
* **Changelog** (``CHANGELOG.md``): Version history and release notes
* **License** (``LICENSE``): Apache License 2.0

Supported Hardware
------------------

Boards
~~~~~~

All Raspberry Pi boards are supported:

* Raspberry Pi 1 Model B
* Raspberry Pi 2 Model B
* Raspberry Pi 3 Model B
* Raspberry Pi 4 Model B
* Raspberry Pi 5
* Raspberry Pi 400
* Raspberry Pi Compute Module 4
* Raspberry Pi Zero
* Raspberry Pi Zero 2W

Frameworks
~~~~~~~~~~

**lgpio** (Recommended)
    Modern C library for Linux GPIO access. Works on all Raspberry Pi models including Pi 5 with the RP1 I/O controller. **Recommended for all new projects.**

**pigpio**
    Feature-rich C library with microsecond timing and advanced PWM support. Compatible with Pi 1-4. **Not compatible with Pi 5.** Deprecated in favor of lgpio.

**WiringPi**
    GPIO library with Arduino-like API. GC2 fork with Pi 5 support (GCLK function not available on Pi 5). **Cross-compilation not supported** - must build natively on Pi.

**Bare-metal**
    No framework - direct system calls. Maximum portability across all boards.

Architecture Support
~~~~~~~~~~~~~~~~~~~~

* **32-bit (ARMv7)**: Default for all boards, maximum compatibility
* **64-bit (AArch64)**: Optional for Pi 3B, 4B, 400, 5, CM4, and Zero 2W

Set ``board_build.arch = aarch64`` in ``platformio.ini`` to enable 64-bit builds.

Examples
--------

Example projects are available in the `examples/ directory <https://github.com/platformio/platform-linux_arm/tree/master/examples>`__:

baremetal-hello
    Simple bare-metal "Hello World" application demonstrating basic C program compilation.

lgpio-blink
    LED blink example using lgpio framework (recommended for all Pi models).

pigpio-blink
    LED blink example using pigpio framework (Pi 1-4 only, deprecated).

wiringpi-blink
    LED blink example using WiringPi framework (legacy compatibility).

wiringpi-serial
    Serial communication example using WiringPi framework.

Framework Selection Guide
-------------------------

Quick Recommendations
~~~~~~~~~~~~~~~~~~~~~

* **For new projects (any Pi model)**: Use **lgpio**
* **For Raspberry Pi 5**: Use **lgpio** (only fully compatible framework)
* **For advanced PWM/timing on Pi 1-4**: Use **pigpio** (if you need microsecond precision)
* **For legacy projects**: Use **WiringPi** (cross-compilation not supported)
* **For maximum portability**: Use **bare-metal** (no framework dependencies)

Compatibility Matrix
~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows: 1
    :widths: 20 15 15 15 15

    * - Board
      - lgpio
      - pigpio
      - WiringPi
      - bare-metal
    * - Pi 1, 2, 3, 4
      - Yes
      - Yes
      - Yes
      - Yes
    * - Pi 5
      - Yes
      - No
      - Partial - Limited
      - Yes
    * - Cross-compilation
      - Yes
      - Yes
      - No
      - Yes

Platform Development
--------------------

For developers contributing to the platform:

Development Setup
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Clone repository
    git clone https://github.com/platformio/platform-linux_arm.git
    cd platform-linux_arm

    # Install in development mode
    pio pkg install --global --platform symlink://.

    # Install ARM cross-compilation toolchains
    sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
    sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

    # Set up lgpio for cross-compilation
    ./scripts/setup-lgpio-cross.sh

Testing
~~~~~~~

.. code-block:: bash

    # Test examples
    cd examples/lgpio-blink
    pio run

    # Run CI tests
    .github/workflows/examples.yml

See ``CONTRIBUTING.md`` for detailed contribution guidelines.

Troubleshooting
---------------

For common issues and solutions, see:

* `Troubleshooting Guide <TROUBLESHOOTING.md>`__
* `GitHub Issues <https://github.com/platformio/platform-linux_arm/issues>`__
* `PlatformIO Community <https://community.platformio.org>`__

Support
-------

Need Help?
~~~~~~~~~~

* **Documentation**: Read the full `platform documentation <platforms/linux_arm.html>`__
* **Issues**: Report bugs or request features on `GitHub <https://github.com/platformio/platform-linux_arm/issues>`__
* **Community**: Ask questions on the `PlatformIO Community Forum <https://community.platformio.org>`__

Contributing
~~~~~~~~~~~~

Contributions are welcome! See `CONTRIBUTING.md <../CONTRIBUTING.md>`__ for guidelines.

License
-------

This project is licensed under the Apache License 2.0. See `LICENSE <../LICENSE>`__ for details.

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`search`
