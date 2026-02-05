import subprocess
import sys
import os
import signal

# ---------------- CONFIG ----------------
DEVICE = "ATSAMD21E18A"        # Workaround for E15B
TOOL = "atmelice"
INTERFACE = "swd"
HEX_FILE = "firmware.hex"
# ----------------------------------------


def run_flash():
    if not os.path.exists(HEX_FILE):
        print(f"[ERROR] HEX file not found: {HEX_FILE}")
        return

    cmd = [
        "pymcuprog",
        "write",
        "--tool", TOOL,
        "--device", DEVICE,
        "--interface", INTERFACE,
        "--erase",
        "--verify",
        "--file", HEX_FILE
    ]

    print("\nStarting ATSAMD21 flashing process...")
    print("Running:")
    print(" ".join(cmd))
    print("-" * 60)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Stream output live to terminal
        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print("\n[SUCCESS] Flashing completed successfully.")
        else:
            print(f"\n[ERROR] Flashing failed with code {process.returncode}")

    except FileNotFoundError:
        print("[ERROR] pymcuprog not found. Is it installed and in PATH?")
    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    print("==============================================")
    print(" ATSAMD21 Programming Utility")
    print(" Tool: Atmel-ICE + pymcuprog")
    print("==============================================")

    while True:
        print("\nOptions:")
        print("  F  - Flash firmware")
        print("  Q  - Quit")
        print("----------------------------------------------")

        choice = input("Enter choice: ").strip().upper()

        if choice == "F":
            run_flash()
        elif choice == "Q":
            print("Exiting program.")
            break
        else:
            print("Invalid option.")


def handle_ctrl_c(sig, frame):
    print("\nCtrl+C detected. Exiting safely.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_ctrl_c)
    main()
