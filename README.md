# SAMD Testing Program
**Author:** Miller DeMark

## Overview
This program stack is used to flash our Binary Counters that are using the ARM processor. With all hardware and software downloaded correctly, the user will only need to run the python script to flash the device.

## Requirements
- **Software:**
  - [Microchip Studio](https://www.microchip.com/en-us/tools-resources/develop/microchip-studio#Downloads)
  - Python 3
    - pyserial
    - pymcuprog<br>
    (Both can be installed via pip)
- **Hardware:**
  - Atmel Ice
  - Testing Board

 ## Walkthrough
 - Ensure all software and cables are set up correctly.
 - Download all files in the [Tester](/tester) folder into one directory
 - Extract files
 - Run Tester.py

## Notes
- The tester should identify the COM ports on its own
- The tester is set up to download the firmware.hex on its own
- It is CRUCIAL that all files downloaded are in the same directory
- This should be relatively painless, any questions can be directed towards millerdemark@gmail.com
