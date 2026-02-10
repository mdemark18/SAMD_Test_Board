import subprocess
import serial
import serial.tools.list_ports
import threading
import time
import shutil
import sys
from pathlib import Path
from queue import Queue, Empty

# ----------------- CONFIG -----------------
DEVICE = "ATSAMD21E18A"
BASE_DIR = Path(__file__).resolve().parent
HEX_FILE = BASE_DIR / "firmware.hex"
BAUDRATE = 115200
SERIAL_TIMEOUT = 1  # seconds

# ----------------- FLASHING -----------------
def flash():
    print("\n=== FLASHING TARGET ===\n")
    if not HEX_FILE.exists():
        print("Firmware file not found:", HEX_FILE)
        return False

    # Try to find pymcuprog automatically
    CMD_PATH = shutil.which("pymcuprog")
    if CMD_PATH is None:
        # Common Python Scripts folder fallback
        possible_paths = [
            Path(sys.executable).parent / "Scripts" / "pymcuprog.exe",
            Path.home() / r"AppData\Local\Programs\Python\Python3\Scripts\pymcuprog.exe",
            Path.home() / r"AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pymcuprog.exe"
        ]
        for p in possible_paths:
            if p.exists():
                CMD_PATH = str(p)
                break

    if CMD_PATH is None:
        print("Could not find pymcuprog.exe on this system.")
        print("Please install it or provide the correct path.")
        return False

    print("Using pymcuprog at:", CMD_PATH)

    cmd = [
        CMD_PATH,
        "write",
        "--tool", "atmelice",
        "--device", DEVICE,
        "--interface", "swd",
        "--erase",
        "--verify",
        "--file", str(HEX_FILE)
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(line.strip())
        proc.wait()
        if proc.returncode == 0:
            print("\nFLASH SUCCESS\n")
            return True
        else:
            print("\nFLASH FAILED\n")
            return False
    except Exception as e:
        print("Error running flash:", e)
        return False
# ----------------- PORT DETECTION -----------------
def detect_ports(timeout=10):
    print("\nWaiting for serial ports to appear...\n")
    start = time.time()

    while time.time() - start < timeout:
        target = None
        arduino = None
        ports = serial.tools.list_ports.comports()

        for p in ports:
            desc = p.description.lower()
            print(f"  {p.device} -> {p.description}")

            if "arduino" in desc:
                arduino = p.device

            if "communication device class asf example" in desc:
                target = p.device

        if target and arduino:
            print("\nPorts detected!")
            return target, arduino

        print("Waiting for device enumeration...\n")
        time.sleep(1)

    print("\nTimed out waiting for ports.")
    return None, None

# ----------------- SERIAL READER -----------------
def read_serial_lines(ser, queue):
    """Continuously read serial lines into a queue."""
    while ser.is_open:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                queue.put(line)
        except Exception:
            break

# ----------------- RUN TEST -----------------
def run_test(flash_first=True):
    if flash_first:
        if not flash():
            print("Flash failed, aborting test.")
            return

    print("Detecting devices...")
    target_port, arduino_port = detect_ports()
    if not target_port or not arduino_port:
        print("Devices not found.")
        return

    try:
        target_ser = serial.Serial(target_port, BAUDRATE, timeout=SERIAL_TIMEOUT)
        arduino_ser = serial.Serial(arduino_port, BAUDRATE, timeout=SERIAL_TIMEOUT)
    except Exception as e:
        print("Failed to open serial ports:", e)
        return

    time.sleep(2)  # give devices time to reset

    # Queue to store lines from Arduino
    arduino_queue = Queue()
    arduino_thread = threading.Thread(target=read_serial_lines, args=(arduino_ser, arduino_queue), daemon=True)
    arduino_thread.start()

    # --- Send DEBUG command ---
    print("\n=== DEBUG MODE STARTED ===")
    arduino_ser.write(b"DEBUG\n")
    target_ser.write(b"DEBUG\n")

    # --- Collect Arduino output until end ---
    arduino_lines = []
    while True:
        try:
            line = arduino_queue.get(timeout=0.1)
            print("[ARDUINO]", line)
            arduino_lines.append(line)
            if "End of Test." in line:
                break
        except Empty:
            continue

    print("\n=== DEBUG COMPLETE ===")
    print("=== FINAL SUMMARY ===")
    for line in arduino_lines:
        print("[ARDUINO]", line)

    # Cleanup
    arduino_ser.close()
    target_ser.close()
    print("\nTest session finished.\n")


# ----------------- TERMINAL UI -----------------
def main():
    print("\n=== SAMD Hardware Tester ===\n")
    print("Firmware file:", HEX_FILE)

    while True:
        try:
            cmd = input(
                "\nCommands:\n"
                "  run   → flash + test\n"
                "  again → test only (no flash)\n"
                "  exit  → quit\n\n> "
            ).strip().lower()

            if cmd == "run":
                run_test(flash_first=True)
            elif cmd == "again":
                run_test(flash_first=False)
            elif cmd == "exit":
                print("\nExiting tester...")
                break
            else:
                print("Unknown command.")

        except KeyboardInterrupt:
            print("\n(Interrupted — tester still running)")

# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    main()
