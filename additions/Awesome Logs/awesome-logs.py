import re
import os
import shutil
import datetime
import time
from colorama import init, Fore, Style

# === Пути ===
APPDATA_DIR = os.getenv("APPDATA")  # автоматически C:\Users\<User>\AppData\Roaming
LOG_FILE = os.path.join(APPDATA_DIR, "i2pd", "i2pd.log")
ARCHIVE_DIR = os.path.join(APPDATA_DIR, "i2pd", "logs_archive")
MAX_SIZE_MB = 15

# === Цвета ===
init(autoreset=True)
pattern = re.compile(r"(?P<time>\d+:\d+:\d+)@(?P<pid>\d+)/(?P<level>\w+) - (?P<msg>.+)")

def parse_log_line(line: str):
    match = pattern.match(line)
    if not match:
        return None
    return {
        "time": match.group("time"),
        "pid": match.group("pid"),
        "level": match.group("level").lower(),
        "message": match.group("msg"),
    }

def colorize(level, text):
    if level == "error":
        return Fore.RED + Style.BRIGHT + text
    elif level == "warn":
        return Fore.YELLOW + text
    elif level == "info":
        return Fore.GREEN + text
    else:
        return Fore.CYAN + text
    
def rotate_log():
    if not os.path.exists(LOG_FILE):
        return
    
    size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
    if size_mb < MAX_SIZE_MB:
        return
    
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = os.path.join(ARCHIVE_DIR, f"i2pd_{date_str}.log")

    shutil.move(LOG_FILE, archive_name)
    print(Fore.MAGENTA + f"📦 Log archived: {archive_name}")

    open(LOG_FILE, "w").close()

def monitor_log():
    if not os.path.exists(LOG_FILE):
        print(Fore.RED + f"❌ Log-file {LOG_FILE} does not exist yet")
        return

    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                rotate_log()
                continue

            data = parse_log_line(line)
            if not data:
                continue

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{data['level'].upper()}] {data['message']}"
            print(colorize(data["level"], log_entry))

if __name__ == "__main__":
    monitor_log()
