import subprocess
import time
import threading

files = [
    ["python", "forward_from_channel_to_group.py"],
    ["python", "ocr_space_api.py"],
]

def run_script(cmd):
    subprocess.run(cmd)

if __name__ == "__main__":
    print("🚀 Khởi động tất cả bot...")
    for cmd in files:
        threading.Thread(target=run_script, args=(cmd,), daemon=True).start()
    while True:
        time.sleep(60)