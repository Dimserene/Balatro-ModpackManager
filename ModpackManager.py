import os
import platform
import requests
import shutil
import subprocess
import time
import sys

# Detect system platform
system_platform = platform.system()
is_steam_deck = False  # Ensure it's initialized

if system_platform == "Linux":
    with open("/etc/os-release", "r") as f:
        os_release = f.read()
        if "steamdeck" in os_release.lower():
            is_steam_deck = True

# Define paths based on OS
if system_platform == "Windows":
    MANAGER_FOLDER = os.path.abspath(os.path.expandvars(r"%AppData%\\Balatro"))
    MANAGER_EXECUTABLE = "ModpackManager.exe"
    DOWNLOAD_NAME = "ModpackManager_New.exe"

elif system_platform in ["Linux", "Darwin"]:  # Linux/macOS
    MANAGER_EXECUTABLE = "ModpackManager.py"
    DOWNLOAD_NAME = "ModpackManager_New.py"
    VENV_DIR = os.path.join(os.getcwd(), "myenv")

    if is_steam_deck:
        MANAGER_FOLDER = os.path.expanduser("~/.steam/steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro")
    
    elif system_platform == "Linux":
        MANAGER_FOLDER = os.path.abspath(os.path.expandvars("/home/$USER/.steam/steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro"))
    
    elif system_platform == "Darwin":
        MANAGER_FOLDER = os.path.abspath(os.path.expanduser("~/Library/Application Support/Balatro"))

# Ensure the manager folder exists
os.makedirs(MANAGER_FOLDER, exist_ok=True)

# Configuration
INFORMATION_JSON_URL = "https://raw.githubusercontent.com/Dimserene/ModpackManager/main/information.json"

def fetch_latest_version():
    """Fetch the latest version and direct download URL based on OS."""
    version_url = "https://github.com/Dimserene/Balatro-ModpackManager/releases/latest"  # URL to fetch latest tag

    try:
        response = requests.get(version_url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Extract version number from the redirect URL (e.g., /releases/tag/v1.2.3)
        latest_version = response.url.split("/")[-1]
        
        if system_platform == "Windows":
            download_url = "https://github.com/Dimserene/Balatro-ModpackManager/releases/latest/download/ModpackManager.exe"
        elif system_platform in ["Linux", "Darwin"]:
            download_url = "https://github.com/Dimserene/Balatro-ModpackManager/releases/latest/download/ModpackManager.py"
        else:
            print("Unsupported OS detected. Exiting.")
            return None, None

        print(f"Latest version available: {latest_version}")
        return latest_version, download_url

    except requests.RequestException as e:
        print(f"Failed to fetch latest version: {e}")
        return None, None

def get_current_version():
    """Retrieve the currently installed version from a dedicated version file or executable metadata."""
    settings_folder = os.path.join(MANAGER_FOLDER, "ManagerSettings")
    version_file = os.path.join(settings_folder, "version.txt")

    # Ensure ManagerSettings folder exists
    if not os.path.exists(settings_folder):
        os.makedirs(settings_folder, exist_ok=True)

    # Check if a version file exists
    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as file:
                current_version = file.read().strip()
                if current_version:
                    return current_version  # Return the version from the version file
        except Exception as e:
            print(f"Could not read version file: {e}")

    print("No current version found. Assuming first-time install.")
    return None

def download_update(download_url):
    """Download the latest version of the Modpack Manager."""
    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        new_exe_path = os.path.join(MANAGER_FOLDER, DOWNLOAD_NAME)
        total_size = int(response.headers.get("content-length", 0))  # Get total file size
        downloaded_size = 0

        print("Downloading update...")

        with open(new_exe_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)

                # Simple progress indicator
                percent = (downloaded_size / total_size) * 100 if total_size else 0
                print(f"\rProgress: {percent:.2f}% ({downloaded_size // 1024} KB / {total_size // 1024} KB)", end="")

        # Verify the downloaded file exists and is not empty
        if os.path.exists(new_exe_path) and os.path.getsize(new_exe_path) > 0:
            print("Update downloaded successfully.")
            return new_exe_path
        else:
            print("Downloaded file is empty or corrupted.")
            return None

    except requests.RequestException as e:
        print(f"Failed to download update: {e}")
        return None

def replace_old_manager(new_exe_path, latest_version):
    """Replace the old Modpack Manager with the new version."""
    try:

        if new_exe_path is None:
            print("New manager file not found. Aborting replacement.")
            return
        
        # Paths
        old_manager_path = os.path.join(MANAGER_FOLDER, MANAGER_EXECUTABLE)

        if os.path.exists(old_manager_path):
            os.remove(old_manager_path)  # Delete old file before replacing

        shutil.move(new_exe_path, old_manager_path)

        if system_platform in ["Linux", "Darwin"]:  # Make executable on Linux/macOS
            os.chmod(old_manager_path, 0o755)

        # Update version file
        settings_folder = os.path.join(MANAGER_FOLDER, "ManagerSettings")
        version_file = os.path.join(settings_folder, "version.txt")
        os.makedirs(settings_folder, exist_ok=True)  # Ensure settings folder exists

        with open(version_file, "w", encoding="utf-8") as file:
            file.write(latest_version)

        print("Modpack Manager updated successfully.")

    except Exception as e:
        print(f"Failed to replace old manager: {e}")

def setup_virtual_env():
    """Set up Python virtual environment for macOS/Linux users."""
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        subprocess.run(["python3", "-m", "venv", VENV_DIR], check=True)

    # Ensure pip and dependencies are installed
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "PyQt6", "GitPython", "requests", "pandas", "packaging"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False
    
    return True

def launch_manager():
    """Launch the Modpack Manager."""
    try:
        manager_path = os.path.join(MANAGER_FOLDER, MANAGER_EXECUTABLE)
        if not os.path.exists(manager_path):
            print("Modpack Manager not found. Please install it first.")
            return

        if system_platform == "Windows":
            # Start the process independently and close launcher
            subprocess.Popen(f'start "" "{manager_path}"', shell=True, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

        elif system_platform in ["Linux", "Darwin"]:
            if not os.path.exists(VENV_DIR):  # Ensure virtual environment exists
                print("Setting up virtual environment...")
                if not setup_virtual_env():
                    print("Failed to set up virtual environment. Exiting.")
                    return

            venv_python = os.path.join(VENV_DIR, "bin", "python3")
            subprocess.run([venv_python, manager_path], check=True)

        print("Modpack Manager launched successfully.")

        # Exit the launcher after starting the main manager
        sys.exit(0)

        if system_platform == "Windows":
            subprocess.Popen(f'start "" "{manager_path}"', shell=True)


    except Exception as e:
        print(f"Failed to launch Modpack Manager: {e}")

def main():
    print("Checking for Modpack Manager updates...")

    latest_version, download_url = fetch_latest_version()
    if not latest_version or not download_url:
        print("Could not fetch the latest version. Launching Modpack Manager...")
        launch_manager()
        return

    current_version = get_current_version()
    if current_version == latest_version:
        print(f"Modpack Manager is up to date (Version {current_version}). Launching...")
        launch_manager()
        return

    print(f"New version available: {latest_version} (Current: {current_version})")
    update_exe_path = download_update(download_url)
    if update_exe_path:
        replace_old_manager(update_exe_path, latest_version)

    print("Launching updated Modpack Manager...")
    time.sleep(2)  # Small delay before launching
    launch_manager()

if __name__ == "__main__":
    main()