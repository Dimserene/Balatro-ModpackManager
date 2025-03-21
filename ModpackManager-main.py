import os, logging, sys, tarfile, io, subprocess, math, random, re, shutil, requests, webbrowser, zipfile, stat, json, logging, time, platform
from PyQt6.QtGui import QColor, QPixmap, QCursor, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QProcess, QThread, pyqtSignal, QPoint
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QSlider, QSizePolicy, QStackedWidget, QListWidget, QSplashScreen, QInputDialog, QMenu, QSplitter, QListWidgetItem, QScrollArea, QProgressDialog, QHBoxLayout, QFileDialog, QMessageBox, QApplication, QCheckBox, QLineEdit, QDialog, QLabel, QPushButton, QComboBox, QGridLayout, QWidget, QVBoxLayout
import git
from pathlib import Path
from git import Repo, GitCommandError
from datetime import datetime
from packaging.version import Version
from urllib.parse import urlparse
import pandas as pd
from io import BytesIO

############################################################
# Detect OS and set default settings
############################################################

DATE = "2025/03/11"
ITERATION = "31"
VERSION = Version("1.13.2")

system_platform = platform.system()

is_steam_deck = False
if system_platform == "Linux":
    with open("/etc/os-release", "r") as f:
        os_release = f.read()
        if "steamdeck" in os_release.lower():
            is_steam_deck = True

# Default settings for all platforms
DEFAULT_SETTINGS = {
    "profile_name": "Balatro",
    "default_modpack": "Dimserenes-Modpack",
    "backup_mods": False,
    "remove_mods": True,
    "skip_mod_selection": False,
    "auto_install": False,
    "show_floating_play_button": False,
    "floating_play_x": 100,  # Default position (X)
    "floating_play_y": 100,   # Default position (Y)
    "floating_play_size": (32, 32),  # Default size (width, height)
    "git_http_version": "HTTP/2",
    "http_post_buffer": 1,          # Default: 1MB
    "http_max_request_buffer": 1,   # Default: 1MB
    "http_low_speed_limit": 0,      # Default: 0 KB/s
    "http_low_speed_time": 999999,  # Default: 999,999 sec
    "core_compression": 3,          # Default: Git's default compression level
    "use_steam_launch": False,
    "use_luajit2": False,
    "disable_rainbow_title": False,
    "theme": "Light",
    "log.level": "info",
    "log.enable_stacktrace": False
}

# Configure paths based on OS
if system_platform == "Windows":
    APPDATA_FOLDER = Path(os.getenv("APPDATA", Path.home() / "AppData/Roaming")) / "Balatro"
    SETTINGS_FOLDER = APPDATA_FOLDER / "ManagerSettings"
    DEFAULT_SETTINGS.update({
        "game_directory": Path("C:/Program Files (x86)/Steam/steamapps/common/Balatro"),
        "mods_directory": APPDATA_FOLDER / "Mods",
        "modpack_directory": APPDATA_FOLDER / "Modpacks",
    })

elif system_platform == "Linux":
    home_dir = Path.home()  # Get the user's home directory dynamically

    if is_steam_deck:
        game_directory = Path("/home/deck/.steam/steam/steamapps/common/Balatro")
        if not (game_directory / "Balatro.exe").exists():
            game_directory = Path("/run/media/deck/STEAM/steamapps/common/Balatro")

        APPDATA_FOLDER = home_dir / ".steam/steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro"
    else:
        game_directory = home_dir / ".steam/steam/steamapps/common/Balatro"
        APPDATA_FOLDER = home_dir / ".steam/steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro"
     
    SETTINGS_FOLDER = APPDATA_FOLDER / "ManagerSettings"

    DEFAULT_SETTINGS.update({
        "game_directory": game_directory,
        "mods_directory": APPDATA_FOLDER / "Mods",
        "modpack_directory": APPDATA_FOLDER / "Modpacks",
    })

elif system_platform == "Darwin":
    APPDATA_FOLDER = Path("~/Library/Application Support/Balatro").expanduser()
    SETTINGS_FOLDER = APPDATA_FOLDER / "ManagerSettings"
    DEFAULT_SETTINGS.update({
        "game_directory": Path("~/Library/Application Support/Steam/steamapps/common/Balatro").expanduser(),
        "mods_directory": APPDATA_FOLDER / "Mods",
        "modpack_directory": APPDATA_FOLDER / "Modpacks",
    })

ASSETS_FOLDER = SETTINGS_FOLDER / "assets"
SETTINGS_FILE = SETTINGS_FOLDER / "user_settings.json"
INSTALL_FILE = SETTINGS_FOLDER / "excluded_mods.json"
FAVORITES_FILE = SETTINGS_FOLDER / "favorites.json"
PRESETS_FILE = SETTINGS_FOLDER / "modpack_presets.json"
CACHE_FILE = SETTINGS_FOLDER / "modpack_cache.json"
CSV_CACHE_FILE = SETTINGS_FOLDER / "cached_data.csv"

LOGO_URL = "https://raw.githubusercontent.com/Dimserene/Dimserenes-Modpack/refs/heads/main/NewFullPackLogo.png"
LOGO_PATH = ASSETS_FOLDER / "logo.png"

CHECKBOX_URL = "https://github.com/Dimserene/Balatro-ModpackManager/raw/main/assets/assets.zip"
INFORMATION_URL = "https://raw.githubusercontent.com/Dimserene/ModpackManager/main/information.json"
CSV_URL = "https://docs.google.com/spreadsheets/d/1L2wPG5mNI-ZBSW_ta__L9EcfAw-arKrXXVD-43eU4og/export?format=csv&gid=510782711"

LOGS_DIR = SETTINGS_FOLDER / "log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_filename = LOGS_DIR / f"modpack_manager_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

LIGHT_THEME = """
    QWidget, QMainWindow, QDialog {
        background-color: #fefefe;
        color: #000;
    }

    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QListWidget {
        color: #000;
        font: 10pt 'Helvetica';
    }

    QLineEdit, QComboBox, QSpinBox, QPushButton {
        border: 1px solid gray;
        padding: 6px;
    }

    QPushButton:hover { background-color: #dadada; }
    QPushButton:pressed { background-color: #fefefe; }
    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #a0a0a0;
        border: 1px solid #ccc;
    }

    QCheckBox { background-color: transparent; }
    QDialog, QListWidget { border: 1px solid #bbb; }

    QListWidget {
        background: #fefefe;
        border: 1px solid #444;
    }

    QListWidget::item {
        border: 1px solid #aaa;
        margin: 4px;
        min-height: 36px;
    }

    QListWidget::item:selected { background: #0078d7; border: 1px solid #005ea0; }
    QListWidget::item:hover { background: #ccc; }

    QCheckBox::indicator { width: 24px; height: 24px; }
    QCheckBox::indicator:unchecked { image: url("ManagerSettings/assets/icons8-checkbox-unchecked.png"); }
    QCheckBox::indicator:unchecked:hover { image: url("ManagerSettings/assets/icons8-checkbox-hoverunchecked.png"); }
    QCheckBox::indicator:checked { image: url("ManagerSettings/assets/icons8-checkbox-checked.png"); }
    QCheckBox::indicator:checked:hover { image: url("ManagerSettings/assets/icons8-checkbox-hoverchecked.png"); }

    QMenu {
        background-color: #fefefe;
        border: 1px solid #555;
        padding: 5px;
        font-size: 14px;
        color: black;
    }

    QMenu::item { padding: 5px 20px; }
    QMenu::item:selected { background-color: #454545; }
    QMenu::separator { height: 1px; background: #666; margin: 5px 10px; }
"""

DARK_THEME = """
    QWidget, QMainWindow, QDialog {
        background-color: #222;
        color: #fff;
    }

    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QListWidget {
        color: #fff;
        font: 10pt 'Helvetica';
    }

    QLineEdit, QComboBox, QSpinBox, QPushButton {
        border: 1px solid gray;
        padding: 6px;
    }

    QPushButton:hover { background-color: #dadada; }
    QPushButton:pressed { background-color: #222; }
    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #a0a0a0;
        border: 1px solid #ccc;
    }

    QCheckBox { background-color: transparent; }
    QDialog, QListWidget { border: 1px solid #bbb; }

    QListWidget {
        background: #2c2c2c;
        border: 1px solid #444;
    }

    QListWidget::item {
        border: 1px solid #aaa;
        margin: 4px;
        min-height: 36px;
    }

    QListWidget::item:selected { background: #0078d7; border: 1px solid #005ea0; }
    QListWidget::item:hover { background: #ccc; color: white; }

    QCheckBox::indicator { width: 24px; height: 24px; }
    QCheckBox::indicator:unchecked { image: url("ManagerSettings/assets/icons8-checkbox-uncheckedwhite.png"); }
    QCheckBox::indicator:unchecked:hover { image: url("ManagerSettings/assets/icons8-checkbox-uncheckedwhite.png"); }
    QCheckBox::indicator:checked { image: url("ManagerSettings/assets/icons8-checkbox-checkedwhite.png"); }
    QCheckBox::indicator:checked:hover { image: url("ManagerSettings/assets/icons8-checkbox-checkedwhite.png"); }

    QMenu {
        background-color: #222;
        border: 1px solid #555;
        padding: 5px;
        font-size: 14px;
        color: white;
    }

    QMenu::item { padding: 5px 20px; }
    QMenu::item:selected { background-color: #454545; color: white; }
    QMenu::separator { height: 1px; background: #666; margin: 5px 10px; }
"""

def ensure_settings_folder_exists():
    """Ensure the settings and assets folders exist and create required JSON files if missing."""
    SETTINGS_FOLDER.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured Settings folder exists at: {SETTINGS_FOLDER}")

    ASSETS_FOLDER.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured Assets folder exists at: {ASSETS_FOLDER}")

    # Create default JSON files if they don't exist
    for file_path, default_content in [
        (SETTINGS_FILE, DEFAULT_SETTINGS),
        (INSTALL_FILE, []),
        (FAVORITES_FILE, [])
    ]:
        if not file_path.exists():
            # Convert Path objects to strings before writing JSON
            if isinstance(default_content, dict):
                default_content = {key: str(value) if isinstance(value, Path) else value for key, value in default_content.items()}
            elif isinstance(default_content, list):
                default_content = [str(value) if isinstance(value, Path) else value for value in default_content]

            file_path.write_text(json.dumps(default_content, indent=4), encoding="utf-8")
            logging.info(f"Created file: {file_path}")

# Call the function to ensure directories and files exist
ensure_settings_folder_exists()

def cache_modpack_data(data):
    """Cache modpack data to a local JSON file."""
    try:
        CACHE_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
        logging.info("[Startup] Modpack data cached successfully.")
    except Exception as e:
        logging.error(f"Failed to cache modpack data: {e}", exc_info=True)

def load_cached_modpack_data():
    """Load cached modpack data, with a check for availability."""
    try:
        if CACHE_FILE.exists():
            logging.info("Cached modpack data loaded.")
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        else:
            logging.warning("No cached modpack data found.")
    except Exception as e:
        logging.error(f"Failed to load cached modpack data: {e}", exc_info=True)
    return {}

def download_logo(url, save_path: Path):
    """Download the logo from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        save_path.write_bytes(response.content)  # Simplified file write using pathlib
        logging.info(f"Logo downloaded successfully: {save_path}")
    except requests.RequestException as e:
        logging.error(f"Failed to download logo: {e}", exc_info=True)
        exit(1)

def download_and_extract_icons(url):
    """Download and extract icons from the specified URL into ManagerSettings/assets."""

    try:
        # Download the ZIP file
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Extract the ZIP file into the assets directory
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(ASSETS_FOLDER)

        logging.debug("[Startup] Icons downloaded and extracted successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

def remove_debug_folders(mods_directory):
    """
    Check for folders other than 'Steamodded' that contain 'tk_debug_window.py'
    and remove them.
    """
    mods_directory = Path(mods_directory)  # Ensure it is a Path object
    
    if not mods_directory.exists():
        logging.warning(f"[Cleanup] Mods directory does not exist: {mods_directory}")
        return  # Exit early to prevent errors

    for folder in mods_directory.iterdir():
        if folder.is_dir() and folder.name != "Steamodded":
            debug_file_path = folder / "tk_debug_window.py"
            if debug_file_path.is_file():
                try:
                    logging.info(f"[Cleanup] Removing folder: {folder}")
                    shutil.rmtree(folder)
                except Exception as e:
                    logging.error(f"[Cleanup] Failed to remove {folder}: {e}", exc_info=True)

def is_online(test_url="https://www.google.com", parent=None):
    """Check if the system is connected to the internet."""
    try:
        response = requests.get(test_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        if parent:
            QMessageBox.warning(parent, "Offline Mode", "Unable to fetch modpack data. Using cached data if available.")
        return False

def fetch_modpack_data(url):
    """Fetch modpack data, with fallback to offline cache if offline."""
    if is_online():
        logging.info("[Startup] Online: Fetching modpack data...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()       # Parse JSON data
            cache_modpack_data(data)     # Cache the data for offline use
            
            return data
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data: {e}", exc_info=True)
    else:
        logging.info("Offline: Using cached modpack data.")

    # Fallback to cached data if offline
    return load_cached_modpack_data()

modpack_data = fetch_modpack_data(INFORMATION_URL)

# Extract `recommanded_lovely` if available
recommanded_lovely = modpack_data.get("recommanded_lovely", "https://github.com/ethangreen-dev/lovely-injector/releases/latest/download/")
logging.debug(f"Recommanded Lovely URL: {recommanded_lovely}")

def fetch_dependencies(url):
    """
    Fetch dependencies from the `information.json` file.
    Args:
        url (str): URL of the `information.json` file.
        parent (QWidget or None): Optional parent for QMessageBox.
    Returns:
        dict: Dictionary of dependencies from the JSON file.
    """
    if is_online():
        logging.debug(f"Fetching dependencies from {url}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cache the dependencies locally
            cache_modpack_data(data)

            dependencies = data.get("dependencies", {})
            logging.debug(f"Dependencies fetched successfully: {dependencies}")
            return dependencies
        except requests.RequestException as e:
            logging.error(f"Failed to fetch dependencies: {e}", exc_info=True)
    else:
        logging.info("Offline: Using cached dependency data.")
    
    # Load cached data as fallback
    cached_data = load_cached_modpack_data()
    return cached_data.get("dependencies", {}) if cached_data else {}
    
dependencies = fetch_dependencies(INFORMATION_URL)

def fetch_csv_data(url, parent=None):
    """
    Fetch CSV data with fallback to offline mode and caching.
    Args:
        url (str): URL of the CSV file.
        parent (QWidget or None): Optional parent for QMessageBox.
    Returns:
        pd.DataFrame or None: Pandas DataFrame with CSV data, or None on failure.
    """
    if is_online():
        logging.debug(f"Fetching CSV data from {url}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            csv_data = response.text
            
            # Save the CSV data to cache
            CSV_CACHE_FILE.write_text(csv_data, encoding="utf-8")
            logging.debug("CSV data cached successfully.")

            # Load the data into a DataFrame
            return pd.read_csv(io.StringIO(csv_data))

        except requests.RequestException as e:
            logging.error(f"Error fetching CSV data: {e}", exc_info=True)
            if parent:
                QMessageBox.warning(parent, "Offline Mode", "Failed to fetch CSV data. Using cached data if available.")
    else:
        logging.info("Offline: Cannot fetch CSV data without an internet connection.")
        if parent:
            QMessageBox.information(parent, "Offline Mode", "No internet connection detected. Using cached CSV data.")

    # Fallback to cached CSV data
    return load_cached_csv_data()

def load_cached_csv_data():
    """
    Load cached CSV data from the local file.
    Returns:
        pd.DataFrame or None: Cached CSV data as a DataFrame, or None if not available.
    """
    try:
        if CSV_CACHE_FILE.exists():
            logging.info("Loading cached CSV data...")
            return pd.read_csv(CSV_CACHE_FILE)
        else:
            logging.warning("No cached CSV data found.")
    except Exception as e:
        logging.error(f"Failed to load cached CSV data: {e}", exc_info=True)
    return None

# Process data to extract genres and tags
def process_genres_tags(data: pd.DataFrame) -> dict:
    """
    Extract unique genres and associated tags from the dataset.

    Args:
        data (pd.DataFrame): The dataset containing 'Genre' and 'Tags' columns.

    Returns:
        dict: A dictionary mapping genres to their respective tags.
    """
    if {'Genre', 'Tags'}.difference(data.columns):
        raise KeyError("Required columns 'Genre' and 'Tags' not found in the data.")

    return {
        genre: data.loc[data['Genre'] == genre, 'Tags']
                .dropna().astype(str).unique().tolist()
        for genre in data['Genre'].dropna().unique()
    }

def populate_genres_tags(list_widget: QListWidget, genre_tags: dict):
    """
    Populate a QListWidget with genres as parent items and tags as child items.

    Args:
        list_widget (QListWidget): The widget to populate.
        genre_tags (dict): A dictionary mapping genres to their respective tags.
    """
    for genre, tags in genre_tags.items():
        genre_item = QListWidgetItem(f"Genre: {genre}")
        genre_item.setFlags(genre_item.flags())  # Non-editable
        list_widget.addItem(genre_item)

        # Add tags as child items
        for tag in tags:
            tag_item = QListWidgetItem(f"  - Tag: {tag}")
            tag_item.setFlags(tag_item.flags())  # Non-editable
            list_widget.addItem(tag_item)

def map_mods_to_metadata(data: pd.DataFrame) -> dict:
    """
    Map mods to their metadata (Genre, Tags, and Description).

    Args:
        data (pd.DataFrame): The dataset containing mod details.

    Returns:
        dict: A dictionary mapping mod folder names to their metadata.
    """
    return {
        str(row.get('Folder Name', "Unknown")).strip(): {
            "Genre": str(row.get('Genre', "Unknown")).strip() if pd.notna(row.get('Genre')) else "Unknown",
            "Tags": [tag.strip() for tag in str(row.get('Tags', "")).split(',')] if pd.notna(row.get('Tags')) else [],
            "Description": str(row.get('Description', "No description available.")).strip(),
            "Page Link": str(row.get('Page Link', "")).strip() if pd.notna(row.get('Page Link')) else "",
            "Discord Link": str(row.get('Discord Link', "")).strip() if pd.notna(row.get('Discord Link')) else ""
        }
        for _, row in data.iterrows()
    }

############################################################
# Worker classes
############################################################

class ModpackDownloadWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)  # Signal to update progress (optional)

    def __init__(self, clone_url, repo_name, branch_name, modpack_directory, force_update=False):
        super().__init__()
        self.clone_url = clone_url
        self.repo_name = Path(modpack_directory) / repo_name
        self.branch_name = branch_name
        self.force_update = force_update
        self.process = None  # Store the QProcess instance

    def run(self):
        logging.info(f"[Modpack Download] Starting download for {self.repo_name} from {self.clone_url}")

        try:
            # Ensure the Modpacks folder exists
            self.repo_name.parent.mkdir(parents=True, exist_ok=True)

            # Check if the repository folder already exists
            if self.repo_name.exists():
                if self.force_update:
                    # Delete the existing folder if force_update is True
                    try:
                        shutil.rmtree(self.repo_name, onerror=readonly_handler)
                        logging.info(f"Deleted existing folder: {self.repo_name}")
                    except Exception as e:
                        logging.error(f"[Modpack Download] Failed to delete existing folder: {e}", exc_info=True)
                        self.finished.emit(False, f"Failed to delete existing folder: {str(e)}")
                        return
                else:
                    # If not forcing update, emit failure message
                    logging.warning(f"[Modpack Download] Modpack folder '{self.repo_name}' already exists. Skipping download.")
                    self.finished.emit(False, f"Modpack folder '{self.repo_name}' already exists. Enable force update to overwrite.")
                    return

            if self.clone_url.endswith('.git'):
                # Clone the repository using the selected branch
                git_command = ["git", "clone", "-b", self.branch_name, "--recurse-submodules", self.clone_url, str(self.repo_name)]
                logging.info(f"[Modpack Download] Running Git clone command: {' '.join(git_command)}")

                self.process = QProcess()
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                
                # Connect QProcess signals for dynamic output handling
                self.process.finished.connect(self.git_finished)
                self.process.readyReadStandardOutput.connect(self.read_git_output)
                self.process.start(git_command[0], git_command[1:])
                self.process.waitForFinished(-1)

            else:
                # Download the file (this part will still emit the success message)
                logging.info(f"[Modpack Download] Downloading file from: {self.clone_url}")
                response = requests.get(self.clone_url, stream=True)

                if response.status_code != 200:
                    logging.error(f"[Modpack Download] File download failed: HTTP {response.status_code}")
                    self.finished.emit(False, f"File download failed: HTTP status {response.status_code}.")
                    return

                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                modpack_directory = self.get_expanded_path("modpack_directory")

                local_file_path = modpack_directory / f"{self.repo_name.name}.zip"

                with open(local_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # Emit progress signal if you have a connected GUI progress bar
                            if total_size > 0:
                                progress_percent = int((downloaded_size / total_size) * 100)
                                self.progress.emit(progress_percent)

                # Verify the file size after download
                if downloaded_size != total_size:
                    logging.error(f"[Modpack Download] File download failed: Incomplete file. Expected {total_size} bytes, got {downloaded_size} bytes.")
                    self.finished.emit(False, "File download failed: Incomplete file.")
                    return

                # Unzip if necessary
                if zipfile.is_zipfile(local_file_path):
                    try:
                        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
                            zip_ref.extractall(self.repo_name)
                        local_file_path.unlink()  # Delete the zip file after extraction
                        logging.info(f"[Modpack Download] Successfully extracted ZIP file to {self.repo_name}")
                    except zipfile.BadZipFile:
                        logging.error(f"[Modpack Download] Corrupt ZIP file: {local_file_path}", exc_info=True)
                        self.finished.emit(False, "File download failed: Corrupt ZIP file.")
                        return

                # If file download succeeds, emit success
                self.finished.emit(True, f"Successfully downloaded {self.repo_name}.")
                logging.info(f"[Modpack Download] Successfully downloaded {self.repo_name}.")

        except Exception as e:
            logging.error(f"[Modpack Download] Unexpected error: {str(e)}", exc_info=True)
            self.finished.emit(False, f"An unexpected error occurred: {str(e)}")

    def read_git_output(self):
        """Capture real-time output from the Git process."""
        output = bytes(self.process.readAllStandardOutput()).decode('utf-8').strip()
        if output:
            logging.info(f"[Git Output] {output}")  # Optionally, update your GUI log or console with this output

    def git_finished(self):
        """Callback for handling the QProcess finish signal for Git operations."""
        # Capture standard output and error messages
        output = self.process.readAllStandardOutput().data().decode('utf-8').strip()
        error_msg = self.process.readAllStandardError().data().decode('utf-8').strip()

        # Check for actual error conditions
        if self.process.exitCode() == 0 and self.process.error() == QProcess.ProcessError.UnknownError:
            # Success case: Repository should exist
            if self.repo_name.exists() and any(self.repo_name.iterdir()):
                logging.info(f"[Modpack Download] Successfully cloned {self.repo_name}.")
                self.finished.emit(True, f"Successfully cloned {self.repo_name}.")
            else:
                # Handle unexpected case where the repo doesn't exist after a 'successful' clone
                logging.error(f"[Modpack Download] Git clone succeeded but folder {self.repo_name} is empty.")
                self.finished.emit(False, f"Git clone succeeded but the folder {self.repo_name} is empty.")
        else:
            # Error case: Provide more detailed output
            error_detail = error_msg if error_msg else (output if output else "An unknown error occurred.")
            logging.error(f"[Modpack Download] Git clone failed: {error_detail}", exc_info=True)
            self.finished.emit(False, f"Git clone failed: {error_detail}")

        self.process.readyReadStandardOutput.connect(self.capture_stdout)
        self.process.readyReadStandardError.connect(self.capture_stderr)

    def capture_stdout(self):
        output = self.process.readAllStandardOutput().data().decode('utf-8').strip()
        logging.info(f"Standard Output: {output}")

    def capture_stderr(self):
        error_msg = self.process.readAllStandardError().data().decode('utf-8').strip()
        logging.error(f"Standard Error: {error_msg}", exc_info=True)

def update_submodules(repo):
    """
    Update submodules of a given repository, handling additions and removals.

    Args:
        repo (Repo): The GitPython Repo object representing the repository.
    """
    try:
        logging.debug("Synchronizing submodules...")
        repo.git.submodule('sync')  # Sync submodule URLs

        logging.debug("Initializing new submodules...")
        repo.git.submodule('init')  # Initialize new submodules

        logging.debug("Updating submodules recursively...")
        repo.git.submodule('update', '--recursive')  # Update submodules

        submodules_path = Path(repo.working_tree_dir) / ".gitmodules"
        if not submodules_path.exists():
            logging.warning(".gitmodules file not found. Skipping stale submodule cleanup.")
            return

        logging.debug("Cleaning up stale submodules...")
        # Deinit stale submodules
        repo.git.submodule('deinit', '--all', '--force')

        # Remove cached and stale submodules
        repo.git.rm('--cached', '-r', '--ignore-unmatch', submodules_path)

        stale_paths = [Path(repo.working_tree_dir) / submodule.path for submodule in repo.submodules]
        for path in stale_paths:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)

        logging.debug("Re-initializing submodules...")
        repo.git.submodule('init')
        repo.git.submodule('update', '--recursive')

        logging.info("Submodules updated successfully.")
    except GitCommandError as e:
        logging.error(f"Git command error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Unexpected error during submodule update: {e}", exc_info=True)
        raise

class ModpackUpdateWorker(QThread):
    finished = pyqtSignal(bool, str)  # Signal to indicate task completion with success status and message
    progress = pyqtSignal(str)       # Signal to report progress to the GUI

    def __init__(self, repo_url, repo_name, branch_name, parent_folder):
        super().__init__()
        self.repo_url = repo_url
        self.repo_name = repo_name
        self.branch_name = branch_name
        self.repo_path = Path(parent_folder) / self.repo_name

    def run(self):
        """Main update function."""
        logging.info(f"[Update] Starting update for {self.repo_name} in {self.repo_path}")

        try:
            if not self.repo_path.exists() or not self.repo_path.is_dir():
                error_msg = f"Invalid repository path: {self.repo_path}"
                logging.error(error_msg)
                self.finished.emit(False, error_msg)
                return

            repo = Repo(self.repo_path)

            # Handle uncommitted changes
            try:
                if repo.is_dirty(untracked_files=True):
                    self.progress.emit("Uncommitted changes detected. Resetting and cleaning repository...")
                    logging.warning("[Update] Uncommitted changes detected. Resetting repo...")
                    
                    repo.git.reset('--hard')  # Discard local changes
                    repo.git.clean('-fd')     # Remove untracked files and directories
                    logging.info("[Update] Repository reset and cleaned successfully.")

            except GitCommandError as e:
                error_msg = f"Error resetting repository: {str(e)}"
                logging.error(error_msg, exc_info=True)
                self.finished.emit(False, error_msg)
                return

            # Pull the latest changes
            self.progress.emit("Pulling latest changes...")
            logging.info("[Update] Pulling latest changes...")

            try:
                repo.remotes.origin.pull()
                logging.info("[Update] Pull completed successfully.")

            except GitCommandError as e:
                error_msg = f"Error pulling latest changes: {str(e)}"
                logging.error(error_msg, exc_info=True)
                self.finished.emit(False, error_msg)
                return

            # Update submodules
            self.progress.emit("Updating submodules...")
            logging.info("[Update] Updating submodules...")

            try:
                self.update_submodules(repo)
                logging.info("[Update] Submodules updated successfully.")

            except GitCommandError as e:
                error_msg = f"Error updating submodules: {str(e)}"
                logging.error(error_msg, exc_info=True)
                self.finished.emit(False, error_msg)
                return

            success_msg = "Modpack and submodules updated successfully."
            logging.info(f"[Update] {success_msg}")
            self.finished.emit(True, success_msg)

        except GitCommandError as e:
            error_msg = f"Git error: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.finished.emit(False, error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.finished.emit(False, error_msg)

    def update_submodules(self, repo):
        """Update all submodules recursively."""
        logging.info("[Update] Initializing and updating submodules...")
        repo.git.submodule('update', '--init', '--recursive')
        self.progress.emit("Submodules updated.")
        logging.info("[Update] Submodules successfully updated.")

class FloatingPlayButton(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setFixedSize(40, 40)  # Slightly larger for better visibility

        # Load play button image
        self.play_icon_path = ASSETS_FOLDER / "floating_play.png"

        # Play button
        self.play_label = QLabel(self)
        self.play_label.setPixmap(QPixmap(str(self.play_icon_path)).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.play_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.play_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Close button
        self.close_button = QPushButton("x", self)
        self.close_button.setFixedSize(16, 16)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 150);
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 200);
            }
        """)
        self.close_button.hide()
        self.close_button.clicked.connect(self.close_button_clicked)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.play_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Opacity effect for hover effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)  # Full opacity by default

        # Load last position
        self.load_position()

        # Initialize drag variables
        self.drag_start_position = None
        self.is_dragging = False

    def mousePressEvent(self, event: QMouseEvent):
        """Start moving window on mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            self.is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Move the floating window when dragged."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_start_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            if delta.manhattanLength() > 5:
                self.is_dragging = True
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.drag_start_position = event.globalPosition().toPoint()
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """If the mouse was not dragged, treat as a click."""
        if not self.is_dragging:
            self.launch_game()
        self.save_position()
        self.is_dragging = False
        event.accept()

    def enterEvent(self, event):
        """Show close button and apply hover effect instantly."""
        self.show_close_button()
        self.on_hover()

    def leaveEvent(self, event):
        """Hide close button when mouse leaves."""
        self.close_button.hide()
        self.on_leave()

    def on_hover(self):
        """Reduce opacity when hovered."""
        self.opacity_effect.setOpacity(0.9)

    def on_leave(self):
        """Restore opacity when mouse leaves."""
        self.opacity_effect.setOpacity(1.0)

    def show_close_button(self):
        """Show close button inside play icon (top-right corner)."""
        self.close_button.setParent(self)
        self.close_button.move(self.width() - 18, 2)  # Position inside top-right
        self.close_button.show()

    def close_button_clicked(self):
        """Hide floating button."""
        self.close()

    def save_position(self):
        """Save the last position of the floating button."""
        self.main_window.settings["floating_play_x"] = self.x()
        self.main_window.settings["floating_play_y"] = self.y()
        self.main_window.save_settings()

    def load_position(self):
        """Load the last saved position of the floating button."""
        x = self.main_window.settings.get("floating_play_x", 100)
        y = self.main_window.settings.get("floating_play_y", 100)
        self.move(x, y)

    def launch_game(self):
        """Trigger game launch."""
        logging.info("[Floating Button] Launching game via play_game()")
        self.main_window.play_game()

    def closeEvent(self, event):
        """Ensure the floating button closes when the Mod Manager is closed."""
        logging.info("[Floating Button] Closing with Mod Manager.")
        self.save_position()
        self.main_window.settings["floating_play_visible"] = False  # Save visibility state
        self.main_window.save_settings()
        event.accept()

############################################################
# Tutorial class
############################################################

class TutorialPopup(QDialog):
    """Floating, titleless popup to display tutorial instructions."""
    def __init__(self, step_text, related_widget, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Store the main window for use in positioning
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Modal
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()

        # QLabel to display the tutorial text
        self.label = QLabel(step_text)
        
        # Custom stylesheet for the tutorial text
        self.label.setStyleSheet("""
            QLabel {
                background-color: lightyellow;
                color: #333333;
                font: 10pt 'Helvetica';
                padding: 10px;
                border: 2px solid #0087eb;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Adjust the popup's position near the related widget
        self.adjust_popup_position(related_widget)

    def adjust_popup_position(self, related_widget):
        """Position the popup near the related widget and ensure it stays within the main window's bounds."""
        main_window_geometry = self.main_window.geometry()  # Get the main window size and position
        widget_pos = related_widget.mapToGlobal(QPoint(0, related_widget.height()))  # Get widget position
        self.adjustSize()  # Adjust popup size before positioning

        popup_x = widget_pos.x()
        popup_y = widget_pos.y()

        # Ensure the popup stays within the main window bounds
        popup_width = self.width()
        popup_height = self.height()
        main_window_right = main_window_geometry.x() + main_window_geometry.width()
        main_window_left = main_window_geometry.x()
        main_window_top = main_window_geometry.y()
        main_window_bottom = main_window_geometry.y() + main_window_geometry.height()

        # Correct if the popup goes off the right side of the main window
        if popup_x + popup_width > main_window_right:
            popup_x = main_window_right - popup_width - 10  # Adjust to fit within the right side

        # Correct if the popup goes off the left side of the main window
        if popup_x < main_window_left:
            popup_x = main_window_left + 10  # Add margin to the left

        # Correct if the popup goes off the bottom of the main window
        if popup_y + popup_height > main_window_bottom:
            popup_y = widget_pos.y() - popup_height - related_widget.height()

        # Correct if the popup goes off the top of the main window
        if popup_y < main_window_top:
            popup_y = main_window_top + 10  # Add margin to the top

        # Finally, move the popup to the adjusted position
        self.move(popup_x, popup_y)

############################################################
# Main Program
############################################################

class ModpackManagerApp(QWidget):  # or QMainWindow
    
    def __init__(self, *args, **kwargs):
        super(ModpackManagerApp, self).__init__(*args, **kwargs)
        self.setWindowTitle("Dimserene's Modpack Manager")

        logging.info("[Startup] Initializing Modpack Manager...")

        # Ensure settings are loaded before using them
        self.settings = self.load_settings()
        self.setup_logging()
        self.check_game_directory()

        if not LOGO_PATH.exists():
            logging.info("[Startup] Downloading missing logo...")
            download_logo(LOGO_URL, LOGO_PATH)

        # Load the splash screen
        splash_pixmap = QPixmap(str(LOGO_PATH)).scaled(
            400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
        self.splash.showMessage(
            "Loading Modpack Manager...",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.black,
        )
        self.splash.show()

        logging.debug("[Startup] Downloading icons...")
        download_and_extract_icons(CHECKBOX_URL)

        # Flags to track whether the popups are open
        self.settings_popup_open = False
        self.revert_popup_open = False
        self.install_popup_open = False

        # Initialize metadata as an attribute
        self.metadata = {}

        # Fetch modpack data with offline support
        logging.info("[Startup] Fetching modpack data...")
        self.modpack_data = fetch_modpack_data(INFORMATION_URL)
        if not self.modpack_data:
            logging.warning("[Startup] Failed to load modpack data. Check internet connection.")
            QMessageBox.critical(self, "Error", "Failed to load modpack data. Please check your internet connection.")
            self.modpack_data = {"modpack_categories": []}  # Use empty data as a fallback

        # Extract hints from JSON data
        self.useful_hints = self.modpack_data.get("hints", ["Tip: No hints found."])  # Default fallback

        self.branch_data = {}        # Dictionary to store branches for each modpack

        # Load favorite mods
        self.favorite_mods = set()  # Initialize favorites
        self.load_favorites()  # Load favorites on startup

        # Load and process the CSV data
        logging.debug("[Startup] Fetching metadata CSV...")
        data = fetch_csv_data(CSV_URL)  # Replace with your CSV-fetching logic
        if data is not None:
            self.metadata = map_mods_to_metadata(data)  # Create metadata mapping
        else:
            logging.error("[Startup] Failed to load CSV metadata.")
            QMessageBox.critical(self, "Error", "Failed to load metadata. Ensure the CSV is accessible.")

        # Load the last selected theme on startup
        selected_theme = self.settings.get("theme", "Light")
        logging.info(f"[Startup] Applying theme: {selected_theme}")

        if selected_theme == "Dark":
            self.apply_theme(DARK_THEME)
        elif selected_theme == "Light":
            self.apply_theme(LIGHT_THEME)

        self.game_dir = self.get_expanded_path("game_directory")
        self.mods_dir = self.get_expanded_path("mods_directory")
                        
        self.profile_name = self.settings.get("profile_name")
        self.selected_modpack = self.settings.get("default_modpack")
        self.excluded_mods = self.read_preferences()

        # Declare default versions
        self.old_version = ""
        self.version_hash = ""

        # Fetch modpack data
        self.modpack_data = modpack_data  # Assign the global modpack_data to an instance variable
        logging.info("[Startup] Modpack data successfully loaded.")

        # Proceed only if data is available
        if not self.modpack_data:
            logging.error("[Startup] Modpack data is empty. Aborting initialization.")
            QMessageBox.critical(self, "Error", "Failed to load modpack data. Please check your internet connection.")
            return

        self.splash.finish(self)

        self.create_widgets()
        
        # Resize the window to the minimum size required for content
        self.adjustSize()

        # Enable drag-and-drop
        self.setAcceptDrops(True)

        # Create an overlay QLabel for the drag image
        self.overlay_label = QLabel(self)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("font-weight: bold; background-color: rgba(0, 0, 0, 200); font-size: 20pt; color: white")
        self.overlay_label.setWordWrap(True)  # Prevent text clipping
        self.overlay_label.setText("Drag and drop to\nimport custom mods...")
        self.overlay_label.hide()  # Hide overlay initially

        self.initialize_branches()   # List all branches on startup
        self.update_branch_dropdown()
        self.update_installed_info()  # Initial update

        # Create a reference to the worker thread
        self.worker = None

        # Initialize blink_timer as None
        self.blink_timer = None

        """Check modpack status when the manager starts."""
        logging.info("[Startup] Checking modpack status on startup.")
        self.setup_button_blinking()  # Ensure correct buttons blink

        self.tutorial_popup = None  # To track the active tutorial popup
        self.current_step = 0  # To track the current tutorial step
        self.tutorial_steps = [
            ("Welcome to the Modpack Manager! Let's get started.", self),
            ("↑ Use this dropdown to select the modpack.", self.modpack_var),
            ("↑ Click Download/Update button to download or update the selected modpack.", self.download_button),
            ("↑ Use Install button to copy the mod files.", self.install_button),
            ("↑ Then click PLAY button to start the game.", self.play_button),
            ("That's it! You are now ready to use the Modpack Manager.", self)
        ]

        # Automatically adjust window size based on content
        self.adjustSize()

        # Prevent manual resizing while still allowing dynamic resizing
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setMinimumSize(self.sizeHint())  # Ensures a minimum size based on current content

        if self.settings.get("show_floating_play_button", False):
            self.floating_play_button = FloatingPlayButton(self)
            self.floating_play_button.show()

        logging.info("[Startup] Modpack Manager initialized successfully.")
    
    def closeEvent(self, event):
        # Save the selected modpack when the window is closed
        selected_modpack = self.modpack_var.currentText()
        self.settings["default_modpack"] = selected_modpack

        # Save settings without showing a popup
        self.save_settings(default_modpack=selected_modpack)
        logging.info(f"[Exit] Saved default modpack: {selected_modpack}")
        logging.error("====================================================================")

        # Ensure the Floating Play Button also closes
        if hasattr(self, "floating_play_button") and self.floating_play_button is not None:
            logging.info("[Exit] Closing Floating Play Button.")
            self.floating_play_button.close()
            self.floating_play_button = None  # Remove reference

        # Call the default closeEvent to continue closing the window
        super(ModpackManagerApp, self).closeEvent(event)

    def dragEnterEvent(self, event):
        """Triggered when a drag enters the window."""
        if event.mimeData().hasUrls():  # Only accept files or folders
            event.acceptProposedAction()
            self.show_drag_overlay()
            logging.info("[Drag] File dragged into window.")

    def dragLeaveEvent(self, event):
        """Triggered when a drag leaves the window."""
        self.hide_drag_overlay()
        logging.info("[Drag] Drag exited window.")

    def dropEvent(self, event):
        """Triggered when a file or URL is dropped onto the window."""
        self.hide_drag_overlay()
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path:
                logging.info(f"[Import] File dropped: {file_path}")
                self.handle_custom_files(file_path)
            elif url.isValid():
                logging.info(f"[Import] URL dropped: {url.toString()}")
                self.handle_custom_files(url.toString())  # Handle URLs

    def show_drag_overlay(self):
        """Show the overlay image when dragging files into the window."""
        self.overlay_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay_label.show()
        logging.debug("[Drag] Drag overlay displayed.")

    def hide_drag_overlay(self):
        """Hide the overlay image when dragging ends."""
        self.overlay_label.hide()
        logging.debug("[Drag] Drag overlay hidden.")

    def handle_custom_files(self, path):
        """Process custom files, zips, and repositories into Modpacks/Custom/"""
        logging.debug(f"[Import] Handling file: {path}")

        path = Path(path)

        modpack_directory = self.get_expanded_path("modpack_directory")
        custom_dir = modpack_directory / "Custom"
        custom_dir.mkdir(parents=True, exist_ok=True)  # Ensure Custom directory exists

        logging.info(f"[Import] Using custom mod directory: {custom_dir}")

        if str(path).startswith("http"):  # If URL
            logging.debug(f"[Import] Handling URL: {path}")
            self.handle_url(path)
            return

        if path.is_file():  # If it's a file
            file_name = path.name
            clean_name = self.clean_mod_name(path.stem)  # Clean mod name
            dest_dir = custom_dir / clean_name  # Folder for the file

            if self.is_supported_archive(path):  # Copy & extract archives
                logging.info(f"[Extract] Extracting archive: {file_name}")
                dest_dir.mkdir(parents=True, exist_ok=True)
                self.extract_archive(path, dest_dir)
                self.flatten_nested_folders(dest_dir)  # Flatten nested folders after extraction

            elif path.suffix in [".lua", ".toml"]:  # Copy config files
                shutil.copy2(path, dest_dir / file_name)
                QMessageBox.information(self, "File Copied", f"Copied {file_name} to: {dest_dir}")
                logging.info(f"[Import] Copied config file: {file_name} to {dest_dir}")

            else:
                QMessageBox.warning(self, "Unknown File", "Only ZIP, TAR, RAR, 7Z, LUA, and TOML files are supported.")
                logging.warning(f"[Import] Unknown file type: {file_name}")
            
        elif path.is_dir():  # If it's a folder
            folder_name = path.name
            clean_folder_name = self.clean_mod_name(folder_name)  # Clean mod name
            dest_dir = custom_dir / clean_folder_name

            logging.info(f"[Import] Copying folder: {folder_name} to {dest_dir}")

            shutil.copytree(path, dest_dir, dirs_exist_ok=True)  # Copy instead of move
            self.flatten_nested_folders(dest_dir)  # Flatten nested folders
            QMessageBox.information(self, "Folder Copied", f"Copied folder to: {dest_dir}")

    def flatten_nested_folders(self, folder_path):
        """
        If the extracted/copied folder contains only one folder, move contents up one level.
        Ensures the folder name does not conflict by renaming existing folders.
        """
        folder_path = Path(folder_path)

        while True:
            items = list(folder_path.iterdir())  # Get all items in the folder

            if len(items) == 1 and items[0].is_dir():  # Only one folder inside
                inner_folder = items[0]

                logging.info(f"[Flatten] Moving files from {inner_folder} to {folder_path}")

                for item in inner_folder.iterdir():
                    destination = folder_path / item.name

                    # If destination already exists, rename it
                    if destination.exists():
                        counter = 1
                        new_destination = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
                        while new_destination.exists():
                            counter += 1
                            new_destination = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
                        destination = new_destination

                    shutil.move(str(item), str(destination))  # Move files/folders up

                inner_folder.rmdir()  # Remove the now-empty nested folder
            else:
                break  # Stop if there's more than one item or no folders

    def clean_mod_name(self, mod_name):
        """
        Removes '-main', '-master', and any other branch suffix from the mod folder name.
        Ensures mod folder names are unique by checking existing folders.
        """
        cleaned_name = re.sub(r'-(main|master|dev|beta|alpha|release|hotfix|patch\d+)$', '', mod_name, flags=re.IGNORECASE)

        modpack_directory = self.get_expanded_path("modpack_directory")

        custom_mods_dir = modpack_directory / "Custom"
        destination_path = custom_mods_dir / cleaned_name

        # Ensure unique name if a folder already exists
        if destination_path.exists():
            counter = 1
            new_name = f"{cleaned_name}_{counter}"
            while (custom_mods_dir / new_name).exists():
                counter += 1
                new_name = f"{cleaned_name}_{counter}"
            cleaned_name = new_name

        logging.debug(f"[Import] Cleaned mod name: {cleaned_name}")
        return cleaned_name

    def is_supported_archive(self, file_path):
        """Checks if the file is a supported archive format."""
        return str(file_path).endswith((".zip", ".tar", ".tar.gz", ".tar.xz", ".tar.bz2", ".rar", ".7z"))

    def extract_archive(self, archive_path, extract_to):
        """Extracts various archive types, using system tools for .rar and .7z."""
        try:
            logging.info(f"[Extract] Starting extraction: {archive_path}")
            temp_extract_dir = Path(str(extract_to) + "_temp")

            # Remove existing folder before extraction
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)

            temp_extract_dir.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix == ".zip":  # ZIP Extraction
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
                logging.info(f"[Extract] ZIP extracted successfully: {archive_path}")

            elif archive_path.suffix in [".tar", ".tar.gz", ".tar.xz", ".tar.bz2"]:  # TAR Extraction
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(temp_extract_dir)
                logging.info(f"[Extract] TAR extracted successfully: {archive_path}")

            elif archive_path.suffix == ".rar":  # RAR Extraction
                self.extract_rar(archive_path, temp_extract_dir)

            elif archive_path.suffix == ".7z":  # 7Z Extraction
                self.extract_7z(archive_path, temp_extract_dir)

            # Find extracted folder(s) inside temp directory
            extracted_items = list(temp_extract_dir.iterdir())
            
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                extracted_folder = extracted_items[0]
            else:
                extracted_folder = temp_extract_dir

            cleaned_name = self.clean_mod_name(archive_path.stem)
            destination_path = extract_to / cleaned_name

            # If the destination path already exists, rename it
            counter = 1
            while destination_path.exists():
                destination_path = extract_to / f"{cleaned_name}_{counter}"
                counter += 1

            shutil.move(extracted_folder, destination_path)

            shutil.rmtree(temp_extract_dir, ignore_errors=True)  # Cleanup temp extraction folder
            self.flatten_nested_folders(destination_path)  # Flatten after extraction
            logging.info(f"[Extract] Extraction completed: {destination_path}")

            QMessageBox.information(self, "Extracted", f"Successfully extracted: {archive_path.name}")

        except Exception as e:
            logging.error(f"[Extract] Failed to extract {archive_path}: {e}", exc_info=True)
            QMessageBox.critical(self, "Extraction Error", f"Failed to extract: {archive_path.name}\nError: {str(e)}")
            
    def extract_rar(self, archive_path, extract_to):
        """Extracts .rar files using system tools."""
        try:
            archive_path = Path(archive_path)
            extract_to = Path(extract_to)
            logging.info(f"[Extract] Extracting .rar file: {archive_path}")

            if system_platform == "Windows":  # Windows
                winrar_path = Path("C:\\Program Files\\WinRAR\\WinRAR.exe")
                seven_zip_path = Path("C:\\Program Files\\7-Zip\\7z.exe")
                if winrar_path.exists():
                    subprocess.run([winrar_path, "x", "-y", str(archive_path), str(extract_to)], check=True)
                elif seven_zip_path.exists():
                    subprocess.run([seven_zip_path, "x", "-y", str(archive_path), f"-o{str(extract_to)}"], check=True)
                else:
                    raise FileNotFoundError("WinRAR not found. Install WinRAR or use another extractor.")

            else:  # Linux/MacOS
                subprocess.run(["unrar", "x", "-o+", str(archive_path), str(extract_to)], check=True)

        except Exception as e:
            logging.error(f"[Extract] RAR extraction failed: {e}", exc_info=True)
            QMessageBox.critical(self, "RAR Extraction Error", f"Failed to extract .rar file: {str(e)}")

    def extract_7z(self, archive_path, extract_to):
        """Extracts .7z files using system tools."""
        try:
            logging.info(f"[Extract] Extracting .7z file: {archive_path}")
            if system_platform == "Windows":  # Windows
                seven_zip_path = Path("C:\\Program Files\\7-Zip\\7z.exe")
                if seven_zip_path.exists():
                    subprocess.run([seven_zip_path, "x", "-y", str(archive_path), f"-o{str(extract_to)}"], check=True)
                else:
                    raise FileNotFoundError("7-Zip not found. Install 7-Zip or use another extractor.")

            else:  # Linux/MacOS
                subprocess.run(["7z", "x", "-y", str(archive_path), f"-o{str(extract_to)}"], check=True)

        except Exception as e:
            logging.error(f"[Extract] 7Z extraction failed: {e}", exc_info=True)
            QMessageBox.critical(self, "7Z Extraction Error", f"Failed to extract .7z file: {str(e)}")

    def handle_url(self, url):
        """Handle URLs for downloading files or cloning repositories."""
        url = str(url).replace("\\", "/")  # Convert backslashes to forward slashes

        # Ensure there are no double "https://" issues
        if url.startswith("https:/") and not url.startswith("https://"):
            url = url.replace("https:/", "https://", 1)

        # If no scheme is present, add "https://"
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "https://" + url.lstrip("/")  # Fix cases where "github.com/Dimserene" is passed

        parsed_url = urlparse(url)  # Re-parse after fixing

        # Validate that the URL has a valid host
        if not parsed_url.netloc:
            logging.error(f"[Download] Invalid URL: {url}. No valid host found.")
            QMessageBox.critical(self, "Download Failed", f"Invalid URL: {url}\nNo valid host found.")
            return

        file_name = Path(parsed_url.path).name  # Extract filename
        modpack_directory = self.get_expanded_path("modpack_directory")
        custom_dir = modpack_directory / "Custom"
        download_path = custom_dir / file_name

        try:
            if url.endswith(".git") or "github.com" or "gitlab.com" in url:
                repo_name = Path(file_name).stem  # Get repo name
                repo_path = custom_dir / repo_name

                if repo_path.exists():
                    logging.warning(f"[Git] Repo already exists: {repo_name}")
                    QMessageBox.warning(self, "Git Repo Exists", f"Repo already exists: {repo_name}")
                    return
                
                logging.info(f"[Git] Cloning repository: {url} to {repo_path}")
                git.Repo.clone_from(url, repo_path)
                QMessageBox.information(self, "Git Cloned", f"Cloned repo: {repo_name}")
                return

            # Download file
            logging.info(f"[Download] Downloading: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(download_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            logging.info(f"[Download] File downloaded successfully: {file_name}")
            QMessageBox.information(self, "Download Complete", f"File downloaded: {file_name}")
            self.handle_custom_files(download_path)  # Process downloaded file

        except requests.exceptions.InvalidURL as e:
            logging.error(f"[Download] Invalid URL: {url}. Error: {e}")
            QMessageBox.critical(self, "Download Failed", f"Invalid URL: {url}\nError: {e}")

        except Exception as e:
            logging.error(f"[Download] Failed to download {url}: {e}", exc_info=True)
            QMessageBox.critical(self, "Download Failed", f"Error downloading: {str(e)}")

    def apply_modpack_styles(self, modpack_name):
        """Apply styles to UI elements based on the selected modpack"""
        if modpack_name == "Coonie's Modpack":
            self.apply_coonies_play_button_style()  # Purple for Coonie's Modpack
        elif modpack_name == "Elbe's Modpack":
            self.apply_elbes_play_button_style()  # Dark Blue for Elbe's Modpack
        else:
            self.apply_default_play_button_style()  # Green for other modpacks

############################################################
# Foundation of root window
############################################################

    def get_modpack_names(self):
        """Retrieve a list of modpack names from self.modpack_data."""
        return [
            modpack["name"]
            for category in self.modpack_data.get("modpack_categories", [])
            for modpack in category.get("modpacks", [])
        ] if self.modpack_data else []

    def create_widgets(self):

        logging.debug("[UI] Initializing main UI components...")
        layout = QGridLayout()

        # Set equal stretch for all columns
        for i in range(6):  # Assuming a 6-column layout
            layout.setColumnStretch(i, 1)

        # Title label
        self.title_label = QLabel("☷☷☷Dimserene's Modpack Manager☷☷☷", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font: 16pt 'Helvetica';")
        layout.addWidget(self.title_label, 0, 0, 1, 6, alignment=Qt.AlignmentFlag.AlignCenter)

        # Initialize variables for breathing effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_color)
        self.timer.start(150)  # Adjust the interval for smoother or slower color changes
        self.breathing_phase = 0

        # Hint label
        self.hint_label = QLabel("", self)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font: 10pt 'Helvetica'; color: gray;")
        self.hint_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Set pointer cursor
        self.hint_label.mousePressEvent = self.update_hint
        layout.addWidget(self.hint_label, 1, 0, 1, 6, alignment=Qt.AlignmentFlag.AlignCenter)

        # Start the hint cycling timer
        self.start_hint_timer()

        # PLAY button
        self.play_button = QPushButton("PLAY", self)
        self.play_button.clicked.connect(self.play_game)
        layout.addWidget(self.play_button, 2, 0, 1, 6)
        logging.debug("[UI] PLAY button initialized.")

        # Installed modpack info label
        self.installed_info_label = QLabel("", self)
        self.installed_info_label.setStyleSheet("font: 10pt 'Helvetica';")
        layout.addWidget(self.installed_info_label, 3, 0, 1, 6)

        # Refresh button
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.setStyleSheet("font: 10pt 'Helvetica';")
        self.refresh_button.setToolTip("Refresh currently installed modpack information")
        self.refresh_button.clicked.connect(self.update_installed_info)
        layout.addWidget(self.refresh_button, 4, 0, 1, 6, alignment=Qt.AlignmentFlag.AlignCenter)
        logging.debug("[UI] Refresh button initialized.")

        # Modpack selection label
        self.modpack_label = QLabel("Modpack:", self)
        self.modpack_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.modpack_label, 5, 0, 1, 1)

        # Assuming self.settings["default_modpack"] exists and contains the default modpack name
        modpack_names = self.get_modpack_names()
        default_modpack = self.settings.get("default_modpack", "Dimserenes-Modpack")  # Get default modpack

        self.apply_modpack_styles(default_modpack)

        # Modpack selection dropdown
        self.modpack_var = QComboBox(self)
        self.modpack_var.addItems(modpack_names)
        self.modpack_var.currentIndexChanged.connect(self.update_modpack_description)
        self.modpack_var.currentIndexChanged.connect(self.update_branch_dropdown)
        self.modpack_var.currentIndexChanged.connect(self.on_modpack_changed)
        layout.addWidget(self.modpack_var, 5, 1, 1, 3)
        logging.info(f"[UI] Modpack dropdown initialized with {len(modpack_names)} modpacks.")

        if default_modpack in modpack_names:
            index = self.modpack_var.findText(default_modpack)
            self.modpack_var.setCurrentIndex(index)
        else:
            self.modpack_var.setEditText(default_modpack)

        # Branches
        self.branch_var = QComboBox(self)
        self.branch_var.currentIndexChanged.connect(self.on_modpack_changed)
        layout.addWidget(self.branch_var, 5, 4, 1, 2)

        # Descriptions
        self.description_label = QLabel("", self)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label, 6, 0, 1, 6)

        self.update_modpack_description()

        # Download button
        self.download_button = QPushButton("Download Modpack", self)
        self.download_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.download_button.clicked.connect(lambda: self.download_modpack(main_window=self))
        layout.addWidget(self.download_button, 7, 0, 1, 3)
        self.download_button.setToolTip("Download (clone) selected modpack to the set directory")
        logging.debug("[UI] Download Modpack button initialized.")

        # Quick Update button
        self.update_button = QPushButton("Quick Update", self)
        self.update_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.update_button.clicked.connect(self.update_modpack)
        layout.addWidget(self.update_button, 7, 3, 1, 3)
        self.update_button.setToolTip("Quickly update downloaded modpacks (can be malfunctioned)")
        logging.debug("[UI] Quick Update button initialized.")

        # Install button
        self.install_button = QPushButton("Install Modpack", self)
        self.install_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.install_button.clicked.connect(self.install_modpack)
        layout.addWidget(self.install_button, 8, 0, 1, 3)
        self.install_button.setToolTip("Copy (install) modpack content to Mods folder")
        logging.debug("[UI] Install Modpack button initialized.")

        # Uninstall button
        self.uninstall_button = QPushButton("Uninstall Modpack", self)
        self.uninstall_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.uninstall_button.clicked.connect(self.uninstall_modpack)
        layout.addWidget(self.uninstall_button, 8, 3, 1, 3)
        self.uninstall_button.setToolTip("Delete Mods folder and its contents, cannot be undone")
        logging.debug("[UI] Uninstall Modpack button initialized.")

        # Verify Integrity button
        self.verify_button = QPushButton("Verify Integrity", self)
        self.verify_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.verify_button.clicked.connect(self.verify_modpack_integrity)
        layout.addWidget(self.verify_button, 9, 0, 1, 3)
        self.verify_button.setToolTip("Check if modpack has missing or incomplete files")
        logging.debug("[UI] Verify Integrity button initialized.")

        # Check Versions button
        self.check_versions_button = QPushButton("Check Versions", self)
        self.check_versions_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.check_versions_button.clicked.connect(self.check_versions)
        layout.addWidget(self.check_versions_button, 9, 3, 1, 3)
        self.check_versions_button.setToolTip("Check latest version for all modpacks")
        logging.debug("[UI] Check Versions button initialized.")

        # Install Lovely button
        self.install_lovely_button = QPushButton("Install/Update lovely", self)
        self.install_lovely_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.install_lovely_button.clicked.connect(self.install_lovely_injector)
        layout.addWidget(self.install_lovely_button, 10, 0, 1, 3)
        self.install_lovely_button.setToolTip("Install/update lovely injector")
        logging.debug("[UI] Install/Update Lovely button initialized.")

        # Settings button
        self.open_settings_button = QPushButton("Settings", self)
        self.open_settings_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.open_settings_button.clicked.connect(self.open_settings_popup)
        layout.addWidget(self.open_settings_button, 10, 3, 1, 3)
        self.open_settings_button.setToolTip("Settings")
        logging.debug("[UI] Settings button initialized.")

        # Discord button
        self.discord_button = QPushButton("Join Discord", self)
        self.discord_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.discord_button.clicked.connect(self.open_discord)
        layout.addWidget(self.discord_button, 11, 0, 1, 3)
        self.discord_button.setToolTip("Open Discord server in web browser")
        logging.debug("[UI] Join Discord button initialized.")

        # Links button
        self.links_button = QPushButton("Links", self)
        self.links_button.setStyleSheet("font: 12pt 'Helvetica';")
        self.links_button.clicked.connect(self.open_links_menu)
        layout.addWidget(self.links_button, 11, 3, 1, 3)
        self.links_button.setToolTip("Open relavent links in web browser")
        logging.debug("[UI] Links button initialized.")

        # Tutorial link
        self.tutorial_link = QLabel(self)
        self.tutorial_link.setText('<a href="#">Start Tutorial</a>')  # Set HTML for clickable text
        self.tutorial_link.setOpenExternalLinks(False)  # Disable default behavior of opening URLs
        self.tutorial_link.linkActivated.connect(self.start_tutorial)  # Connect to the tutorial method
        self.tutorial_link.setStyleSheet("""
            QLabel {
                color: #0087eb;  /* Blue link color */
                font: 8pt 'Helvetica';
                text-decoration: underline;  /* Underline the text to make it look like a link */
            }
            QLabel:hover {
                color: #005ea0;  /* Change color on hover */
            }
        """)
        layout.addWidget(self.tutorial_link, 12, 0, 1, 2)
        logging.debug("[UI] Tutorial link initialized.")

        self.info = QLabel(self)
        self.info.setText("")
        self.update_build_info()
        layout.addWidget(self.info, 12, 0, 1, 6, alignment=Qt.AlignmentFlag.AlignRight)

        # Apply the grid layout to the window
        self.setLayout(layout)
        logging.info("[UI] UI components successfully initialized.")

############################################################
# Helper functions
############################################################

    def update_build_info(self):
        """Updates the build info label dynamically."""
        theme = self.settings.get("theme", "Light")  # Default to Light if theme not set
        version_style = "color: white;" if theme == "Dark" else "color: black;"
        
        self.info.setText(f"Build: {DATE}, Iteration: {ITERATION}, Version: Release {VERSION}")
        self.info.setStyleSheet(f"font: 8pt 'Helvetica'; {version_style}")
        self.info.update()  # Force UI refresh

    def on_modpack_changed(self):
        """Handles modpack selection changes and updates UI accordingly."""
        selected_modpack = self.modpack_var.currentText()
        logging.info(f"[UI] Modpack changed to: {selected_modpack}")

        # Update UI elements
        self.apply_default_play_button_style()
        self.settings["default_modpack"] = selected_modpack

        # Ensure button blinking updates accordingly
        self.setup_button_blinking()

    def update_color(self):
        """Smooth breathing effect with a full-spectrum rainbow color transition."""

        if self.settings.get("disable_rainbow_title", False):
            if self.settings.get("theme") == "Light":
                self.title_label.setStyleSheet("font: 16pt 'Helvetica'; color: black;")  # Default color
            elif self.settings.get("theme") == "Dark":
                self.title_label.setStyleSheet("font: 16pt 'Helvetica'; color: white;")  # Default color
            return

        # Adjust breathing phase for a smooth transition
        self.breathing_phase = (self.breathing_phase + 0.003) % (2 * math.pi)  # Keep it within a cycle

        # Compute RGB values using a full-spectrum rainbow pattern
        red = int(127.5 * (math.sin(self.breathing_phase) + 1))
        green = int(127.5 * (math.sin(self.breathing_phase + 2 * math.pi / 3) + 1))
        blue = int(127.5 * (math.sin(self.breathing_phase + 4 * math.pi / 3) + 1))

        # Convert color to hex format and apply it
        color_hex = QColor(red, green, blue).name()
        self.title_label.setStyleSheet(f"font: 16pt 'Helvetica'; color: {color_hex};")
            
    def get_repo_url(self, modpack_name):
        """Returns the Git URL for the selected modpack."""
        url = self.modpack_data.get(modpack_name, {}).get("url", "") 
        if not url:
            logging.warning(f"[Branch] No repository URL found for modpack: {modpack_name}")
        return url

    def initialize_branches(self):
        """Lists all branches for each modpack and stores them."""
        logging.debug("[Branch] Initializing branch data for all modpacks...")
        for category in self.modpack_data.get("modpack_categories", []):
            for modpack in category.get("modpacks", []):
                modpack_name = modpack["name"]
                self.branch_data[modpack_name] = self.list_branches(modpack_name)

        logging.debug("[Branch] Branch data initialized.")

        for modpack, branches in self.branch_data.items():
            logging.debug(f"[Branch] {modpack}: {branches}")

    def list_branches(self, modpack_name):
        """Lists all branches of a given modpack from the JSON data."""
        for category in self.modpack_data.get("modpack_categories", []):
            for modpack in category.get("modpacks", []):
                if modpack["name"] == modpack_name:
                    branches = modpack.get("branches", ["main"])
                    logging.debug(f"[Branch] Found branches for {modpack_name}: {branches}")
                    return branches
        logging.warning(f"[Branch] No branches found for modpack: {modpack_name}, Default to main.")
        return []

    def update_branch_dropdown(self):
        """Update branch dropdown based on the selected modpack."""
        if not hasattr(self, 'branch_var'):
            logging.warning("Warning: branch_var is not initialized yet.")
            return  # Prevent running the function if branch_var is missing
            
        selected_modpack = self.modpack_var.currentText()
        branches = self.branch_data.get(selected_modpack, ["main"])

        if branches:
            logging.info(f"[Branch] Updating branch dropdown for {selected_modpack}: {branches}")
            self.branch_var.clear()
            self.branch_var.addItems(branches)
        else:
            logging.warning(f"[Branch] No branches available for {selected_modpack}. Defaulting to 'main'.")
            self.branch_var.clear()
            self.branch_var.addItem("main")

    def start_hint_timer(self):
        """Start a timer to update the hint label with a random useful tip."""
        if not self.useful_hints:
            logging.warning("[Hints] No hints available in the modpack data.")
            return

        logging.debug("[Hints] Starting hint cycling timer.")
        self.update_hint()  # Show an initial hint
        self.hint_timer = QTimer(self)
        self.hint_timer.timeout.connect(self.update_hint)
        self.hint_timer.start(30000)  # Change hint every 30 seconds

    def update_hint(self, event=None):
        """Update the hint label with a new random hint from information.json."""
        if self.useful_hints:
            hint = random.choice(self.useful_hints)
            self.hint_label.setText(hint)
            logging.debug(f"[Hints] Updated hint: {hint}")
        else:
            logging.warning("[Hints] No hints found. Hint label not updated.")

    def open_links_menu(self):
        """Dynamically generate a dropdown menu with links from information.json."""
        links_menu = QMenu(self)
        general_links = self.modpack_data.get("links", {})

        if not general_links:
            logging.warning("[Links] No external links found in modpack data.")
            return
        
        logging.debug("[Links] Populating links menu with available links.")
        for link_name, url in general_links.items():
            # Convert key names into readable labels
            label = link_name.replace("_", " ").title()  # Convert key names to readable labels
            action = links_menu.addAction(label)
            action.triggered.connect(lambda checked, url=url: self.open_external_link(url))

        # Show the menu under the "Links" button
        links_menu.exec(self.links_button.mapToGlobal(self.links_button.rect().bottomLeft()))

    def open_external_link(self, url):
        """Opens an external link in the user's web browser."""
        logging.info(f"[Links] Opening external link: {url}")
        webbrowser.open(url)

    def toggle_floating_play_button(self):
        """Enable or disable floating play button."""
        show_button = self.floating_play_checkbox.isChecked()
        self.settings["show_floating_play_button"] = show_button
        self.save_settings()

        if show_button:
            if not hasattr(self, "floating_play_button"):
                self.floating_play_button = FloatingPlayButton(self)
            self.floating_play_button.show()
        else:
            if hasattr(self, "floating_play_button"):
                self.floating_play_button.close()
                del self.floating_play_button

    def get_expanded_path(self, setting_key):
        """
        Returns the expanded directory path from settings based on the operating system.
        
        Args:
            setting_key (str): The key in `self.settings` to retrieve the directory path.

        Returns:
            Path: A pathlib.Path object with the correctly expanded path.
        """
        path_value = self.settings.get(setting_key, DEFAULT_SETTINGS.get(setting_key, ""))

        if system_platform == "Darwin":  # macOS
            return Path(path_value).expanduser()
        elif system_platform in ["Windows", "Linux"]:
            return Path(os.path.expandvars(path_value)).resolve()

############################################################
# Foundation of tutorial
############################################################

    def start_tutorial(self):
        """Starts the tutorial from step 0."""
        logging.info("[Tutorial] Starting tutorial...")
        self.current_step = 0
        self.show_tutorial_step()

    def show_tutorial_step(self):
        """Shows the current tutorial step with a floating popup."""
        if self.current_step >= len(self.tutorial_steps):
            # Tutorial completed, close the popup and reset
            logging.info("[Tutorial] Tutorial completed.")
            if self.tutorial_popup:
                self.tutorial_popup.close()
                self.tutorial_popup = None  # Clear the popup
            self.current_step = 0  # Reset tutorial steps
            return

        step_text, widget = self.tutorial_steps[self.current_step]
        logging.debug(f"[Tutorial] Step {self.current_step + 1}/{len(self.tutorial_steps)}: {step_text}")

        # Close the previous popup if it exists
        if self.tutorial_popup:
            self.tutorial_popup.close()
            logging.debug("[Tutorial] Previous tutorial popup closed.")

        # Create a new popup and show it
        self.tutorial_popup = TutorialPopup(step_text, widget, self)
        self.tutorial_popup.show()
        logging.debug("[Tutorial] Displayed tutorial popup.")

        # Move to the next step after 5 seconds
        self.current_step += 1
        QApplication.processEvents()
        QTimer.singleShot(5000, self.show_tutorial_step)

    def next_tutorial_step(self):
        """Moves to the next step in the tutorial."""
        logging.debug(f"[Tutorial] User moved to next step ({self.current_step + 1}).")
        self.current_step += 1
        self.show_tutorial_step()

############################################################
# Foundation of settings popup
############################################################

    def open_settings_popup(self):

        # Prevent opening multiple settings popups
        if getattr(self, "settings_popup", None) and self.settings_popup.isVisible():
            logging.warning("[Settings] Settings popup already open. Preventing duplicate.")
            return

        logging.info("[Settings] Opening settings popup.")

        self.settings_popup_open = True
        self.settings = self.load_settings()

        popup = QDialog(self)
        popup.setWindowTitle("Settings")
        popup.setFixedSize(600, 550)
        popup.setWindowModality(Qt.WindowModality.NonModal)  # Allow interaction with floating button

        settings_list = QListWidget()
        items = ["General", "Installation", "Theme", "Advanced", "Git Settings"]

        for text in items:
            item = QListWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            settings_list.addItem(item)

        # Set a fixed width to prevent dynamic resizing
        settings_list.setFixedWidth(150)  # Adjust width as needed
        settings_list.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        settings_stack = QStackedWidget()  # Holds different setting pages
        settings_stack.addWidget(self.create_general_tab(popup))
        settings_stack.addWidget(self.create_installation_tab(popup))
        settings_stack.addWidget(self.create_theme_tab(popup))
        settings_stack.addWidget(self.create_advanced_tab(popup))
        settings_stack.addWidget(self.create_git_settings_tab(popup))

        settings_list.currentRowChanged.connect(settings_stack.setCurrentIndex)

        # Main Layout
        layout = QHBoxLayout()
        layout.addWidget(settings_list)
        layout.addWidget(settings_stack)

        popup.setLayout(layout)
        popup.finished.connect(lambda: setattr(self, "settings_popup_open", False))

        # Store reference to prevent garbage collection
        self.settings_popup = popup
        self.settings_popup.show()  # Use show() instead of exec()
        self.settings_popup.activateWindow()  # Bring the settings window to the front

        logging.info("[Settings] Settings popup closed.")

    def create_general_tab(self, parent=None):
        """Create the General settings tab."""
        logging.debug("[Settings] Loading General tab.")

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(12)

        # Adjust default game directory based on OS
        default_game_dir = self.get_expanded_path("game_directory")

        # List all .exe files in the game directory and strip ".exe"
        exe_files = self.get_exe_files(default_game_dir)

        # Game Directory
        game_dir_label = QLabel("Game Directory:")
        self.game_dir_entry = QLineEdit(self.settings.get("game_directory", DEFAULT_SETTINGS["game_directory"]))
        self.game_dir_entry.setFixedHeight(30)
        self.game_dir_entry.textChanged.connect(lambda: self.save_settings(game_directory=self.game_dir_entry.text()))
        logging.info(f"[Settings] Loaded game directory: {self.game_dir_entry.text()}")

        default_game_dir_button = QPushButton("Default")
        default_game_dir_button.setFixedSize(100, 30)
        default_game_dir_button.clicked.connect(lambda: self.reset_game_dir_to_default(self.game_dir_entry))

        browse_game_dir_button = QPushButton("Browse")
        browse_game_dir_button.setFixedSize(100, 30)
        browse_game_dir_button.clicked.connect(lambda: self.browse_directory(self.game_dir_entry))

        open_game_dir_button = QPushButton("Open")
        open_game_dir_button.setFixedSize(100, 30)
        open_game_dir_button.clicked.connect(lambda: self.open_directory(self.game_dir_entry.text().strip()))

        # Layout for buttons BELOW the directory field
        game_button_layout = QHBoxLayout()
        game_button_layout.addStretch()  # Push buttons to the right
        game_button_layout.addWidget(default_game_dir_button)
        game_button_layout.addWidget(browse_game_dir_button)
        game_button_layout.addWidget(open_game_dir_button)

        layout.addWidget(game_dir_label)
        layout.addWidget(self.game_dir_entry)
        layout.addLayout(game_button_layout)

        # Mods Directory
        mods_dir_label = QLabel("Mods Directory:")
        self.mods_dir = self.get_expanded_path("mods_directory")
        self.mods_dir_entry = QLineEdit(str(self.mods_dir))
        self.mods_dir_entry.setReadOnly(True)  # Make it non-editable
        self.mods_dir_entry.setFixedHeight(30)
        logging.info(f"[Settings] Loaded mods directory: {self.mods_dir_entry.text()}")

        open_mods_dir_button = QPushButton("Open")
        open_mods_dir_button.setFixedSize(100, 30)
        open_mods_dir_button.clicked.connect(lambda: self.open_directory(self.mods_dir_entry.text().strip()))

        # Layout for Mods directory button BELOW input field
        mods_button_layout = QHBoxLayout()
        mods_button_layout.addStretch()
        mods_button_layout.addWidget(open_mods_dir_button)

        layout.addWidget(mods_dir_label)
        layout.addWidget(self.mods_dir_entry)
        layout.addLayout(mods_button_layout)

        # Modpack Download Directory
        modpack_dir_label = QLabel("Modpacks Download Directory:")
        self.modpack_dir = self.get_expanded_path("modpack_directory")
        self.modpack_dir_entry = QLineEdit(str(self.modpack_dir))
        self.modpack_dir_entry.setFixedHeight(30)
        self.modpack_dir_entry.textChanged.connect(lambda: self.save_settings(modpack_directory=self.modpack_dir_entry.text()))
        logging.info(f"[Settings] Loaded modpack download directory: {self.modpack_dir_entry.text()}")

        browse_modpack_dir_button = QPushButton("Browse")
        browse_modpack_dir_button.setFixedSize(100, 30)
        browse_modpack_dir_button.clicked.connect(lambda: self.browse_directory(self.modpack_dir_entry))

        reset_modpack_dir_button = QPushButton("Default")
        reset_modpack_dir_button.setFixedSize(100, 30)
        reset_modpack_dir_button.clicked.connect(lambda: self.reset_modpack_dir_to_default(self.modpack_dir_entry))

        open_modpack_dir_button = QPushButton("Open")
        open_modpack_dir_button.setFixedSize(100, 30)
        open_modpack_dir_button.clicked.connect(lambda: self.open_directory(self.modpack_dir_entry.text().strip()))

        # Layout for buttons
        modpack_button_layout = QHBoxLayout()
        modpack_button_layout.addStretch()
        modpack_button_layout.addWidget(reset_modpack_dir_button)
        modpack_button_layout.addWidget(browse_modpack_dir_button)
        modpack_button_layout.addWidget(open_modpack_dir_button)

        layout.addWidget(modpack_dir_label)
        layout.addWidget(self.modpack_dir_entry)
        layout.addLayout(modpack_button_layout)

        # Profile Name Selection
        profile_label = QLabel("Profile Name:")
        self.profile_name_var = QComboBox()
        self.profile_name_var.setEditable(True)
        self.profile_name_var.addItems(exe_files)
        self.profile_name_var.setCurrentText(self.settings.get("profile_name", DEFAULT_SETTINGS["profile_name"]))

        profile_name_set_button = QPushButton("Set/Create")
        profile_name_set_button.setFixedSize(130, 30)
        profile_name_set_button.clicked.connect(lambda: self.set_profile_name(self.profile_name_var.currentText(), self.mods_dir_entry))

        profile_button_layout = QHBoxLayout()
        profile_button_layout.addStretch()
        profile_button_layout.addWidget(profile_name_set_button)

        layout.addWidget(profile_label)
        layout.addWidget(self.profile_name_var)
        layout.addLayout(profile_button_layout)

        # Floating Play Button
        self.floating_play_checkbox = QCheckBox("Show Floating Play Button", parent)
        self.floating_play_checkbox.setChecked(self.settings.get("show_floating_play_button", False))
        self.floating_play_checkbox.stateChanged.connect(self.toggle_floating_play_button)
        layout.addWidget(self.floating_play_checkbox)

        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_installation_tab(self, parent=None):
        """Create the Installation settings tab."""
        logging.debug("[Settings] Loading Installation tab.")

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to the top
        layout.setSpacing(12)  # Reduce spacing between checkboxes

        # Always create new checkboxes when opening settings
        self.backup_checkbox = QCheckBox("Backup Mods Folder")
        self.backup_checkbox.setChecked(self.settings.get("backup_mods", False))
        self.backup_checkbox.stateChanged.connect(self.update_descriptions)

        self.backup_description = QLabel()
        self.backup_description.setWordWrap(True)  # Enable word wrapping

        self.remove_checkbox = QCheckBox("Remove Mods Folder")
        self.remove_checkbox.setChecked(self.settings.get("remove_mods", True))
        self.remove_checkbox.stateChanged.connect(self.update_descriptions)

        self.remove_description = QLabel()
        self.remove_description.setWordWrap(True)  # Enable word wrapping

        self.auto_install_checkbox = QCheckBox("Install Mods After Download / Update")
        self.auto_install_checkbox.setChecked(self.settings.get("auto_install", False))
        self.auto_install_checkbox.stateChanged.connect(self.update_descriptions)

        self.auto_install_description = QLabel()
        self.auto_install_description.setWordWrap(True)  # Enable word wrapping

        self.skip_mod_selection_checkbox = QCheckBox("Skip Mod Selection")
        self.skip_mod_selection_checkbox.setChecked(self.settings.get("skip_mod_selection", False))
        self.skip_mod_selection_checkbox.stateChanged.connect(self.update_descriptions)

        self.skip_mod_selection_description = QLabel()
        self.skip_mod_selection_description.setWordWrap(True)  # Enable word wrapping

        # Call `update_descriptions()` immediately to set initial values
        self.update_descriptions()

        layout.addWidget(self.backup_checkbox)
        layout.addWidget(self.backup_description)
        layout.addWidget(self.remove_checkbox)
        layout.addWidget(self.remove_description)
        layout.addWidget(self.auto_install_checkbox)
        layout.addWidget(self.auto_install_description)
        layout.addWidget(self.skip_mod_selection_checkbox)
        layout.addWidget(self.skip_mod_selection_description)

        tab.setLayout(layout)
        return tab

    def update_descriptions(self):
        """Dynamically update descriptions based on checkbox states."""
        if hasattr(self, "backup_description"):
            self.backup_description.setText(
                "Create a backup of the Mods folder before installing mods.\n" if self.backup_checkbox.isChecked()
                else "Don't create a backup of the Mods folder before installing mods.\n"
            )

        if hasattr(self, "remove_description"):
            self.remove_description.setText(
                "Remove the Mods folder before installing mods.\n" if self.remove_checkbox.isChecked()
                else "Keep the Mods folder before installing mods.\n"
            )

        if hasattr(self, "auto_install_description"):
            self.auto_install_description.setText(
                "Automatically install mods after downloading or updating.\n" if self.auto_install_checkbox.isChecked()
                else "Manually install mods after downloading or updating.\n"
            )

        if hasattr(self, "skip_mod_selection_description"):
            self.skip_mod_selection_description.setText(
                "Skip the mods selection dialog and install all mods automatically.\n" if self.skip_mod_selection_checkbox.isChecked()
                else "Manually select mods to install.\n"
            )

        # Automatically save settings whenever a checkbox is toggled
        self.save_settings(
            backup_mods=self.backup_checkbox.isChecked(),
            remove_mods=self.remove_checkbox.isChecked(),
            auto_install=self.auto_install_checkbox.isChecked(),
            skip_mod_selection=self.skip_mod_selection_checkbox.isChecked()
        )

    def create_theme_tab(self, parent=None):
        """Create the Theme settings tab."""
        logging.debug("[Settings] Loading Theme tab.")

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to the top
        layout.setSpacing(12)  # Reduce spacing between elements

        theme_layout = QHBoxLayout()

        # Label for Theme Selection
        theme_label = QLabel("Select Theme:")
        theme_layout.addWidget(theme_label)

        # Theme Dropdown
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Light", "Dark"])
        self.theme_dropdown.setFixedSize(100, 30)
        
        # Load saved theme preference
        current_theme = self.settings.get("theme", "Light")
        if current_theme in ["Light", "Dark"]:
            self.theme_dropdown.setCurrentText(current_theme)
        
        self.theme_dropdown.currentIndexChanged.connect(self.apply_selected_theme)
        
        theme_layout.addWidget(self.theme_dropdown)
        theme_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(theme_layout)

        # Add checkbox to disable rainbow effect
        self.disable_rainbow_checkbox = QCheckBox("Disable Rainbow Title", self)
        self.disable_rainbow_checkbox.setChecked(self.settings.get("disable_rainbow_title", False))
        self.disable_rainbow_checkbox.stateChanged.connect(self.toggle_rainbow_effect)
        layout.addWidget(self.disable_rainbow_checkbox)

        tab.setLayout(layout)
        return tab

    def apply_selected_theme(self):
        """Apply the selected theme from the dropdown and save preference."""
        selected_theme = self.theme_dropdown.currentText()
        
        if selected_theme == "Dark":
            self.apply_theme(DARK_THEME)
        elif selected_theme == "Light":
            self.apply_theme(LIGHT_THEME)

        # Save the selected theme to settings
        self.save_settings(theme=selected_theme)
        logging.info(f"[Settings] Theme changed to {selected_theme}")
        self.update_build_info()  # Update the label dynamically

    def apply_theme(self, theme):
        """Apply the selected theme."""
        self.setStyleSheet(theme)
        QApplication.instance().setStyleSheet(theme)

    def toggle_rainbow_effect(self):
        """Enable or disable the rainbow effect on the title."""
        disabled = self.disable_rainbow_checkbox.isChecked()
        self.settings["disable_rainbow_title"] = disabled
        self.save_settings()
        logging.info(f"[Settings] Rainbow title effect {'disabled' if disabled else 'enabled'}")

    def create_advanced_tab(self, parent=None):
        """Create the General settings tab."""
        logging.debug("[Settings] Loading Advanced tab.")

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(12)

        # Logging Level Dropdown
        log_level_layout = QHBoxLayout()
        log_level_label = QLabel("Logging Level:")
        log_level_layout.addWidget(log_level_label)

        self.log_level_dropdown = QComboBox()
        self.log_level_dropdown.addItems(["debug", "info", "warning", "error"])
        self.log_level_dropdown.setCurrentText(self.settings.get("log.level", "info"))
        self.log_level_dropdown.currentIndexChanged.connect(lambda: self.apply_log_setting("log.level", self.log_level_dropdown.currentText()))
        self.log_level_dropdown.setFixedSize(100, 30)
        log_level_layout.addWidget(self.log_level_dropdown)
        
        log_level_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(log_level_layout)

        # Log Output File Selection
        log_folder_layout = QHBoxLayout()
        log_folder_label = QLabel("Log Folder:")
        log_folder_layout.addWidget(log_folder_label)

        self.log_folder_input = QLineEdit(str(self.settings.get("log.folder", str(LOGS_DIR))))
        log_folder_layout.addWidget(self.log_folder_input)

        open_log_folder_button = QPushButton("Open")
        open_log_folder_button.setFixedSize(100, 30)
        open_log_folder_button.clicked.connect(lambda: self.open_directory(self.log_folder_input.text().strip()))

        # Layout for buttons BELOW the directory field
        log_button_layout = QHBoxLayout()
        log_button_layout.addStretch()  # Push buttons to the right
        log_button_layout.addWidget(open_log_folder_button)

        layout.addLayout(log_folder_layout)
        layout.addLayout(log_button_layout)

        # Enable Stack Trace Checkbox
        self.stacktrace_checkbox = QCheckBox("Enable Stack Trace Logging")
        self.stacktrace_checkbox.setChecked(self.settings.get("log.enable_stacktrace", False))
        self.stacktrace_checkbox.stateChanged.connect(lambda: self.apply_log_setting("log.enable_stacktrace", self.stacktrace_checkbox.isChecked()))
        layout.addWidget(self.stacktrace_checkbox)
        
        # Add checkbox to Launch game via Steam (Windows)
        self.use_steam_launch_checkbox = QCheckBox("Launch game via Steam (Windows)", self)
        self.use_steam_launch_checkbox.setChecked(self.settings.get("use_steam_launch", False))
        self.use_steam_launch_checkbox.stateChanged.connect(lambda: self.save_settings(use_steam_launch=self.use_steam_launch_checkbox.isChecked()))
        self.use_steam_launch_checkbox.setEnabled(system_platform == "Windows")  # Hide properly
        layout.addWidget(self.use_steam_launch_checkbox)

        # LuaJIT2 Experimental Checkbox
        self.luajit_checkbox = QCheckBox("Enable LuaJIT2 (Experimental)", self)
        self.luajit_checkbox.setChecked(self.settings.get("use_luajit2", False))
        self.luajit_checkbox.stateChanged.connect(self.toggle_luajit_option)
        self.luajit_checkbox.setEnabled(system_platform == "Windows")  # Hide properly
        layout.addWidget(self.luajit_checkbox)

        # "Remove user_settings.json" Button
        remove_settings_button = QPushButton("Remove user_settings.json")
        remove_settings_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        remove_settings_button.clicked.connect(lambda: self.remove_user_settings(parent))
        layout.addWidget(remove_settings_button)

        tab.setLayout(layout)
        return tab

    def apply_log_setting(self, setting_key, value):
        """Apply logging settings and save them persistently."""
        self.settings[setting_key] = value  # Update in-memory settings
        self.save_settings()  # Persist settings to file
        logging.debug(f"[Settings] {setting_key} set to {value}")
        self.setup_logging()  # Reapply logging immediately
        
    def setup_logging(self):
        """Configure logging based on user settings."""
        log_level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR
        }

        log_folder = self.settings.get("log.folder", LOGS_DIR)
        log_level = self.settings.get("log.level", "info").lower()
        enable_stacktrace = self.settings.get("log.enable_stacktrace", False)

        # Ensure log directory exists
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Only create a single log file per session
        if not hasattr(self, "log_filename"):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.log_filename = os.path.join(log_folder, f"modpack_manager_{timestamp}.log")

        print(f"[DEBUG] Log file will be: {self.log_filename}")

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(log_level_map.get(log_level, logging.INFO))

        # Remove existing handlers to prevent duplication
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create file handler
        file_handler = logging.FileHandler(self.log_filename, mode='w', encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        if enable_stacktrace:
            logger.setLevel(logging.DEBUG)     

        logging.info("[LOGGING] Modpack Manager started.")
        logging.info("[LOGGING] Logging system initialized.")

    def toggle_luajit_option(self):
        """Update settings when LuaJIT2 checkbox is toggled."""
        self.settings["use_luajit2"] = self.luajit_checkbox.isChecked()
        self.save_settings(use_luajit2=self.luajit_checkbox.isChecked())
        logging.info(f"[Settings] LuaJIT2 {'enabled' if self.luajit_checkbox.isChecked() else 'disabled'}")
        self.install_lovely_injector()

    def remove_user_settings(self, parent):
        """Deletes the user_settings.json file and resets to defaults."""
        confirm = QMessageBox.question(
            parent, "Confirm Removal", 
            "Are you sure you want to delete 'user_settings.json'?\nThis will reset all settings.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            logging.info("[Settings] User confirmed settings file removal.")

            try:
                if os.path.exists(SETTINGS_FILE):
                    os.remove(SETTINGS_FILE)
                    logging.info(f"[Settings] Successfully removed {SETTINGS_FILE}.")

                    self.settings = DEFAULT_SETTINGS.copy()  # Reset to default
                    logging.info("[Settings] Settings reset to default.")

                    # Inform user that the app needs to restart
                    QMessageBox.information(parent, "Restart Required", "Settings file removed. The app will now close.\nPlease relaunch manually.")

                    # Close the application
                    logging.info("[Settings] Closing application after settings reset.")
                    sys.exit(0)   # Gracefully quit the app

                else:
                    logging.warning(f"[Settings] {SETTINGS_FILE} not found. No action taken.")
                    QMessageBox.warning(parent, "Warning", "Settings file not found.")

            except Exception as e:
                logging.error(f"[Settings] Failed to remove settings file: {e}", exc_info=True)
                QMessageBox.critical(parent, "Error", f"Failed to remove settings file:\n{e}")

    def create_git_settings_tab(self, parent=None):
        """Create the General settings tab."""
        logging.debug("[Settings] Loading Git settings tab.")

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to the top
        layout.setSpacing(12)  # Reduce spacing between elements

        # Load default values
        default_values = {
            "http_post_buffer": 1,
            "http_max_request_buffer": 1,
            "http_low_speed_limit": 0,
            "http_low_speed_time": 999999,
            "core_compression": 3,
        }
        
        # Load current settings (or use default if missing)
        for key, default_val in default_values.items():
            self.settings.setdefault(key, default_val)

        # Warning Label
        warning_label = QLabel(
            "⚠️Dangerous Zone⚠️\n"
            "Be cautious when modifying these settings.\n"
            "Only modify them if you understand what you are doing."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(warning_label)

        # Horizontal layout for Git HTTP Version
        git_http_layout = QHBoxLayout()
        git_http_label = QLabel("Git HTTP Version:")
        git_http_layout.addWidget(git_http_label)

        # Git HTTP Version Dropdown
        self.git_http_dropdown = QComboBox()
        self.git_http_dropdown.addItems(["HTTP/2", "HTTP/1.1"])
        self.git_http_dropdown.setCurrentText(self.settings.get("git_http_version", "HTTP/2"))  # Load saved setting
        self.git_http_dropdown.currentIndexChanged.connect(self.apply_git_http_version)  # Apply when changed
        self.git_http_dropdown.setFixedSize(100, 30)
        git_http_layout.addWidget(self.git_http_dropdown)

        git_http_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(git_http_layout)

        # Create sliders
        self.create_slider(layout, "Git HTTP Post Buffer", "MB", "http_post_buffer", 1, 1024, default_values["http_post_buffer"], is_buffer=True)
        self.create_slider(layout, "Git HTTP Max Request Buffer", "MB", "http_max_request_buffer", 1, 1024, default_values["http_max_request_buffer"], is_buffer=True)
        self.create_slider(layout, "Git HTTP Low Speed Limit", "KB/s", "http_low_speed_limit", 0, 100, default_values["http_low_speed_limit"], is_buffer=False)
        self.create_slider(layout, "Git HTTP Low Speed Time", "sec", "http_low_speed_time", 0, 999999, default_values["http_low_speed_time"], is_buffer=False)
        self.create_slider(layout, "Git Core Compression Level", "", "core_compression", -1, 9, default_values["core_compression"], is_buffer=False)
        
        tab.setLayout(layout)
        return tab

    def apply_git_http_version(self):
        """Change Git HTTP version based on user selection."""
        selected_version = self.git_http_dropdown.currentText()

        try:
            if selected_version == "HTTP/1.1":
                subprocess.run(["git", "config", "--global", "http.version", "HTTP/1.1"], check=False)
                logging.info("[Settings] Set Git HTTP version to HTTP/1.1.")
            elif selected_version == "HTTP/2":
                subprocess.run(["git", "config", "--global", "--unset", "http.version"], check=False)
                logging.info("[Settings] Reset Git HTTP version to HTTP/2 (default).")

            self.save_settings(git_http_version=selected_version)

        except subprocess.CalledProcessError as e:
            logging.error(f"[Settings] Failed to set Git HTTP version: {e}", exc_info=True)

    def create_slider(self, layout, label_text, unit, setting_key, min_val, max_val, default_val, is_buffer=False):
        """Generic function to create sliders with correct unit conversions."""
        
        raw_value = self.settings.get(setting_key, default_val)

        # Ensure conversion only applies to buffer values
        try:
            if is_buffer:
                current_value = int(raw_value) // (1024 * 1024)  # Convert bytes to MB
            else:
                current_value = int(raw_value)
        except ValueError:
            current_value = default_val  # Fallback in case of invalid stored values

        # Label showing both the current value and default
        label = QLabel(f"{label_text}: {current_value} {unit} (Default: {default_val} {unit})")
        layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(current_value)

        # Update label live while moving slider
        slider.valueChanged.connect(lambda: self.update_slider_label(label, label_text, slider, unit, default_val))

        # Only apply settings when slider is released
        slider.sliderReleased.connect(lambda: self.apply_git_setting(setting_key, slider.value(), is_buffer))

        layout.addWidget(slider)

    def apply_git_setting(self, setting_key, value, is_buffer=False):
        """Apply Git setting only when the slider is released, converting MB to bytes if needed."""
        
        git_command_map = {
            "http_post_buffer": "http.postBuffer",
            "http_max_request_buffer": "http.maxRequestBuffer",
            "http_low_speed_limit": "http.lowSpeedLimit",
            "http_low_speed_time": "http.lowSpeedTime",
            "core_compression": "core.compression"
        }

        git_command = git_command_map.get(setting_key)
        if not git_command:
            logging.warning(f"[Settings] Invalid Git setting key: {setting_key}")
            return  # Invalid setting

        # Convert MB to bytes before applying Git settings for buffers
        applied_value = str(value * 1024 * 1024) if is_buffer else str(value)

        try:
            subprocess.run(['git', 'config', '--global', git_command, applied_value], check=True)
            logging.info(f"[Settings] Applied Git setting {git_command} = {applied_value}")

            self.save_settings(**{setting_key: applied_value if is_buffer else value})

        except subprocess.CalledProcessError as e:
            logging.error(f"[Settings] Failed to apply Git setting {git_command}: {e}", exc_info=True)

    def update_slider_label(self, label, label_text, slider, unit, default_val):
        """Update label text dynamically while keeping the default value visible."""
        current_value = slider.value()
        label.setText(f"{label_text}: {current_value} {unit} (Default: {default_val} {unit})")

############################################################
# Read and load user preferences
############################################################

    # Function to load settings from the JSON file
    def load_settings(self):
        """Load settings from file and add missing defaults if needed."""

        settings = {}

        # Try to load existing settings
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                logging.debug("[Settings] Loaded settings from file.")
            
            # Check for missing keys and add default values
            updated = False
            for key, default_value in DEFAULT_SETTINGS.items():
                if key not in settings or settings[key] is None or settings[key] == "":
                    settings[key] = default_value  # Add missing key
                    updated = True
                    logging.warning(f"[Settings] Missing key '{key}' added with default value.")

            # If any keys were missing, update the settings file
            if updated:
                self.save_settings(**settings)
                logging.info("[Settings] Updated settings with missing defaults.")

        except (FileNotFoundError, json.JSONDecodeError):
            # If the file is missing or corrupt, create a new settings file with default values
            settings = DEFAULT_SETTINGS.copy()
            self.save_settings(settings)
            logging.error("[Settings] Corrupt or missing settings file. Resetting to defaults.")

        return settings

    def save_settings(self, **kwargs):
        """Save settings to the JSON file, handling optional arguments and UI values."""

        if not hasattr(self, "settings") or not isinstance(self.settings, dict):
            self.settings = {}

        # Update settings with provided key-value pairs
        for key, value in kwargs.items():
            if value is not None:
                self.settings[key] = value

        # Convert Path objects to strings to prevent JSON serialization issues
        json_safe_settings = {
            key: str(value) if isinstance(value, Path) else value for key, value in self.settings.items()
        }

        # Write updated settings to the JSON file
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(json_safe_settings, f, indent=4)
            logging.info("[Settings] Settings saved successfully.")

            # Reload only if needed (to avoid unnecessary I/O operations)
            if kwargs:
                self.load_settings()
                logging.info("[Settings] Settings reloaded after save.")

        except Exception as e:
            logging.error(f"[Settings] Failed to save settings: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    # Function to reset settings to defaults
    def reset_game_dir_to_default(self, game_dir_entry):
        """Reset game directory setting to default."""
        logging.info("[Settings] Resetting game directory to default.")
        self.settings["game_directory"] = DEFAULT_SETTINGS["game_directory"]
        
        # Reset game directory
        self.game_dir = self.get_expanded_path("game_directory")
        game_dir_entry.setText(str(self.game_dir))

    def reset_modpack_dir_to_default(self, modpack_dir_entry):
        """Reset modpack directory setting to default."""
        logging.info("[Settings] Resetting modpack directory to default.")
        self.settings["modpack_directory"] = DEFAULT_SETTINGS["modpack_directory"]
        
        # Reset game directory
        self.modpack_dir = self.get_expanded_path("modpack_directory")
        modpack_dir_entry.setText(str(self.modpack_dir))

    def check_game_directory(self):
        """Check if the game executable exists, otherwise prompt the user to select the correct game directory."""
        game_executables = {
            "Darwin": "Balatro.app",
            "Linux": "Balatro.exe",
            "Windows": "balatro.exe"
        }

        game_exe = game_executables.get(system_platform, "balatro.exe")  # Default to Windows/Linux exe if unknown
        game_path = self.get_expanded_path("game_directory") / game_exe  # Get directory and append game exe

        if not game_path.exists():
            QMessageBox.warning(None, "Game Not Found", "Game was not found in the default directory. Please select the correct game directory.")
            logging.warning(f"[Settings] Game was not found in the default directory: {game_path}")

            # Open file dialog to select the correct game folder
            game_dir = QFileDialog.getExistingDirectory(None, "Select Balatro Game Directory", "")

            if game_dir:
                self.settings["game_directory"] = game_dir
                self.save_settings()
                logging.info(f"[Settings] Game directory saved: {game_dir}")
                QMessageBox.information(None, "Game Directory Set", f"Game directory saved: {game_dir}")
            else:
                logging.warning("[Settings] Game directory selection was canceled. Some features may not work correctly.")
                QMessageBox.critical(None, "Error", "Game directory selection was canceled. Some features may not work correctly.")
                
    # Function to browse and update the directory
    def browse_directory(self, entry_widget):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_selected:
            # Update the entry with the selected folder path
            entry_widget.setText(folder_selected)
            logging.info(f"[FileDialog] Directory selected: {folder_selected}")

    # Function to open the directory in file explorer
    def open_directory(self, directory_path):
        """
        Opens the specified directory in the file explorer.
        Supports macOS, Windows, and Linux.
        """
            
        # Handle empty input gracefully
        if not directory_path:
            logging.warning("[Directory] No directory path provided.")
            QMessageBox.warning(self, "Warning", "No directory specified.")
            return

        directory = Path(directory_path).resolve()

        logging.info(f"[Directory] Attempting to open directory: {directory}")

        try:
            # Check if the directory exists, ask user before creating it
            if not directory.exists():
                response = QMessageBox.question(
                    self, "Create Directory?",
                    f"The directory does not exist:\n{directory}\nDo you want to create it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if response == QMessageBox.StandardButton.Yes:
                    directory.mkdir(parents=True, exist_ok=True)
                    logging.info(f"[Directory] Created missing directory: {directory}")
                    QMessageBox.information(self, "Info", f"Directory was created: {directory}")
                else:
                    logging.info("[Directory] User declined directory creation.")
                    return  # Exit if user chooses not to create the directory
                
            # Platform-specific commands to open the directory
            if system_platform == "Darwin":  # macOS
                subprocess.run(["open", str(directory)], check=True)
            elif system_platform == "Windows":
                os.startfile(str(directory))  # Windows uses os.startfile
            elif system_platform == "Linux":
                subprocess.run(["xdg-open", str(directory)], check=True)
            else:
                QMessageBox.critical(None, "Error", "Unsupported operating system.")
                logging.error(f"[Directory] Unsupported OS when opening: {directory}")
        except Exception as e:
            logging.error(f"[Directory] Failed to open directory: {directory}. Error: {e}", exc_info=True)
            QMessageBox.critical(None, "Error", f"Failed to open directory:\n{directory}\nError: {e}")

    def set_profile_name(self, profile_name, mods_dir_entry):
        """Set profile name and update mods directory and executable/app."""
        if not profile_name:
            logging.warning("[Profile] No profile name provided. Skipping profile creation.")
            return
        
        logging.info(f"[Profile] Setting profile name to: {profile_name}")

        # Construct the new mods directory path based on profile name
        if system_platform == "Darwin":  # macOS
            new_mods_dir = Path(f"~/Library/Application Support/{profile_name}/Mods").expanduser()
        elif system_platform in ["Windows", "Linux"]:
            new_mods_dir = Path(os.path.expandvars(f"%AppData%\\{profile_name}\\Mods")).resolve()

        self.settings["mods_directory"] = str(new_mods_dir)  # Update the settings with the string path
        self.mods_dir = new_mods_dir  # Store the `Path` object for further use

        # Update the mods_dir_entry to show the new directory
        mods_dir_entry.setReadOnly(False)  # Temporarily make it writable
        mods_dir_entry.setText(str(new_mods_dir))  # Insert the new directory
        mods_dir_entry.setReadOnly(True)  # Set back to readonly

        # Construct the source and destination paths
        source_exe = self.game_dir / ("balatro.exe" if system_platform != "Darwin" else "balatro.app")
        destination_exe = self.game_dir / (f"{profile_name}.exe" if system_platform != "Darwin" else f"{profile_name}.app")

        # Check if the original game executable exists, otherwise prompt the user
        if not source_exe.exists():
            logging.warning(f"[Profile] Source executable not found: {source_exe}")
            QMessageBox.warning(self, "File Not Found",
                f"{source_exe.name} not found in the game directory. Please choose a file to copy.")

            # Prompt user to select the game executable manually
            file_filter = "Executable Files (*.exe)" if system_platform != "Darwin" else "App Bundles (*.app)"
            chosen_file, _ = QFileDialog.getOpenFileName(None, "Select Executable", "", file_filter)

            if not chosen_file:  # If the user cancels the file selection
                logging.info("[Profile] No file selected. Profile creation aborted.")
                QMessageBox.information(self, "Operation Cancelled", "No file selected. Profile creation aborted.")
                return

            # Set the source_exe to the chosen file
            source_exe = Path(chosen_file)  # Convert chosen file to a `Path` object

        # Try copying the executable/app to the new profile name
        try:
            if system_platform == "Darwin" and source_exe.is_dir():
                if str(source_exe).lower() != str(destination_exe).lower():
                    shutil.copytree(source_exe, destination_exe, dirs_exist_ok=True)
                else:
                    logging.info("[Profile Name] Skipping copy: Source and destination are the same.")

            else:  # Windows & Linux (or macOS if it's a file)
                if str(source_exe).lower() != str(destination_exe).lower():
                    shutil.copy2(source_exe, destination_exe)
                else:
                    logging.info("[Profile Name] Skipping copy: Source and destination are the same.")

            # Save the profile name directly
            self.save_settings(profile_name=profile_name)
            logging.info(f"[Profile] Profile name '{profile_name}' saved in settings.json")

            # Update UI if needed
            if hasattr(self, "profile_name_label"):
                self.profile_name_label.setText(f"Profile: {profile_name}")

            logging.info(f"[Profile] Created profile executable: {destination_exe}")
            QMessageBox.information(self, "Success",
                f"Profile file {os.path.basename(destination_exe)} created successfully!")

        except Exception as e:
            logging.error(f"[Profile] Failed to create {destination_exe.name}: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create {destination_exe.name}: {e}")

    def get_exe_files(self, directory):
        """Get a list of executables or app bundles in the directory, stripping extensions."""
        try:
            directory = Path(directory).expanduser()  # Expand user paths
            logging.info(f"[Profile] Fetching executables from directory: {directory}")

            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")

            # Detect the platform and fetch the corresponding files            
            if system_platform == "Darwin":  # macOS
                # Fetch .app bundles and strip the extension
                return [file.stem for file in directory.iterdir() if file.suffix == ".app" and file.is_dir()]

            
            elif system_platform in ["Windows", "Linux"]:
                # Fetch .exe files and strip the extension
                return [file.stem for file in directory.iterdir() if file.suffix == ".exe"]

            return []  # Return an empty list if no executables are found

        except FileNotFoundError:
            logging.error(f"[Profile] {e}")
            QMessageBox.critical(self, "Error", str(e))
            return []
        except Exception as e:
            logging.error(f"[Profile] Unexpected error: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return []

############################################################
# Top functions (Play, installed info, refresh)
############################################################

    def play_game(self):
        """Launch the game based on the platform and settings."""
        self.settings = self.load_settings()

        # Check if Lovely Injector is installed
        if not self.check_lovely_injector_installed():
            logging.warning("[Game] Lovely Injector is missing. Cannot launch game.")
            QMessageBox.warning(self, "Cannot Launch Game", "Lovely Injector is required to play the modded game. Launch aborted.")
            return

        # Windows Toggle: Use Steam Launch or Direct Launch
        use_steam_launch = self.settings.get("use_steam_launch", True)  # Default: Steam Launch

        # Common Steam launch command
        steam_command = "steam://rungameid/2379780"

        self.game_dir = self.get_expanded_path("game_directory")
        self.profile_name = self.settings.get("profile_name")
        self.mods_path = self.get_expanded_path("mods_directory")
        
        # Remove debug folders from the Mods directory
        remove_debug_folders(self.mods_path)

        try:
            if system_platform == "Windows":

                    if use_steam_launch:
                        logging.info("[Game] Launching game via Steam.")
                        self.process = QProcess(self)
                        self.process.start("cmd.exe", ["/c", "start", steam_command])
                    else:
                        # Construct the path to the game executable
                        game_executable = self.game_dir / f"{self.profile_name}.exe"

                        if game_executable.exists():
                            logging.info(f"[Game] Launching {game_executable}")
                            self.process = QProcess(self)
                            self.process.start(str(game_executable))
                        else:
                            raise FileNotFoundError(f"Game executable not found: {game_executable}")

            elif system_platform == "Linux":
                logging.info("[Game] Launching game via Steam on Linux.")
                self.process = QProcess(self)
                self.process.start("steam", [steam_command])

            elif system_platform == "Darwin":  # macOS
                lovely_script = self.game_dir / "run_lovely.sh"

                if not lovely_script.exists():
                    logging.error(f"[Game] Failed to launch game via run_lovely.sh on MacOS: Script not found.")
                    QMessageBox.critical(self, "Error", f"The script 'run_lovely.sh' was not found in the expected location:\n{lovely_script}")
                    return
                
                # Launch the script
                logging.info("[Game] Launching game via run_lovely.sh on MacOS.")
                self.process = QProcess(self)
                self.process.start("bash", [str(lovely_script)])

            else:
                logging.warning(f"[Game] Unsupported Platform, your OS is not supported for launching the game.")
                QMessageBox.warning(self, "Unsupported Platform", "Your OS is not supported for launching the game.")

        except Exception as e:
            logging.error(f"[Game] Failed to launch game: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to launch game: {e}")
        
    def apply_default_play_button_style(self):
        """ Apply default play button color (Green) """
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #00D600;  /* Green for default */
                color: white;
                padding: 10px;
                font: 30pt 'Helvetica';
                border: 2px solid transparent;
            }
            QPushButton:hover {
                background-color: #00C400;  /* Darker Green on hover */
                border: 2px solid #00A800;  /* Dark Green border on hover */
            }
            QPushButton:pressed {
                background-color: #008c00;  /* Even darker Green on press */
                padding-top: 12px;
                padding-bottom: 8px;
            }
        """)

    def get_latest_commit_message(self, owner, repo, branch="main"):
        """Fetch the latest commit message for a specific branch of a GitHub repository."""
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"

        try:
            response = requests.get(api_url, timeout=10)  # Added timeout for better reliability
            response.raise_for_status()  # Raise HTTPError for bad responses

            commit_data = response.json()
            return commit_data.get("commit", {}).get("message", "No commit message available")

        except requests.exceptions.RequestException as e:
            logging.error(f"[GitHub] Error fetching commit message for {repo} ({branch}): {e}", exc_info=True)
            return f"Error fetching commit message: {str(e)}"

    def fetch_commit_messages(self):
        """Fetch the latest commit messages for the Dimserene modpack repositories."""
        repos = {}

        # Load the modpack data from the JSON file
        if self.modpack_data:
            for category in self.modpack_data.get("modpack_categories", []):
                if category.get("category") == "Dimserene":
                    for modpack in category.get("modpacks", []):
                        name, url = modpack.get("name"), modpack.get("url")
                        branches = modpack.get("branches", ["main"])  # Default to 'main' if branches are not specified
                        
                        if name and url:
                            # Extract owner and repo name from URL
                            match = re.match(r"https://github\.com/([^/]+)/([^/.]+)", url)
                            if match:
                                owner, repo_name = match.groups()
                                repos[name] = {"owner": owner, "repo": repo_name, "branches": branches}

        commit_messages = {}

        # Fetch the latest commit messages for each branch in each repository
        for repo_name, repo_data in repos.items():
            owner, repo, branches = repo_data["owner"], repo_data["repo"], repo_data["branches"]
            branch_messages = [
                f"[{branch}]: {self.get_latest_commit_message(owner, repo, branch)}"
                for branch in branches
            ]
            
            # Combine messages for all branches of a repository
            commit_messages[repo_name] = "\n".join(branch_messages)

        return commit_messages

    def get_version_info(self):
        """Retrieve installed modpack version and pack name with structured logging."""
        logging.info("[Version] Retrieving installed modpack version and name.")

        # Paths for version and modpack name files
        mods_path = self.get_expanded_path("mods_directory") / "ModpackUtil"
        current_version_file = mods_path / "CurrentVersion.txt"
        modpack_name_file = mods_path / "ModpackName.txt"
        modpack_util_file = mods_path / "ModpackUtil.lua"

        current_version, pack_name = None, ""

        # Load the current version if available
        if current_version_file.exists():
            logging.info(f"[Version] Found CurrentVersion.txt at {current_version_file}. Reading...")
            current_version = self.read_file_content(current_version_file) or "Unknown"
        else:
            logging.warning(f"[Version] CurrentVersion.txt not found at {current_version_file}.")

        # Attempt to load the modpack name from ModpackName.txt
        if modpack_name_file.exists():
            logging.info(f"[Version] Found ModpackName.txt at {modpack_name_file}. Reading...")
            pack_name = self.read_file_content(modpack_name_file)
        else:
            logging.warning(f"[Version] ModpackName.txt not found at {modpack_name_file}. Using fallback.")
            # Fallback to extracting from ModpackUtil.lua if ModpackName.txt is missing
            pack_name = self.extract_pack_name(modpack_util_file)
        
        logging.info(f"[Version] Retrieved Modpack: {pack_name}, Version: {current_version}")
        return current_version, pack_name

    def update_installed_info(self):
        """Update the installed modpack information with macOS support."""
        # Load user settings once
        self.settings = self.load_settings()

        # Detect the operating system and resolve the install path
        mods_path = self.get_expanded_path("mods_directory") / "ModpackUtil"
        current_version_file = mods_path / "CurrentVersion.txt"
        modpack_name_file = mods_path / "ModpackName.txt"
        modpack_util_file = mods_path / "ModpackUtil.lua"

        # Attempt to read the current version
        current_version = self.read_file_content(current_version_file)

        # Attempt to read the modpack name from ModpackName.txt, or fallback to ModpackUtil.lua
        pack_name = self.read_file_content(modpack_name_file) or self.extract_pack_name(modpack_util_file)

        # Update installed info label with pack name and version
        info_text = (f"Installed pack: {pack_name} ({current_version})" if pack_name else "No modpack installed or ModpackUtil mod removed.")
        self.installed_info_label.setText(info_text)
        self.installed_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logging.info(f"[Installed Info] {info_text}")

    def read_file_content(self, file_path: Path):
        """Helper function to read content from a file safely."""
        file_path = Path(file_path)  # Ensure it's a Path object

        if not file_path.exists():
            logging.warning(f"[File] Missing file: {file_path}. Returning None.")
            return None  # Return None instead of throwing an error

        try:
            return file_path.read_text(encoding="utf-8").strip()
        except IOError as e:
            logging.error(f"[File] IOError reading {file_path}: {e}", exc_info=True)
            return None  # Return None on error

    def extract_pack_name(self, lua_file_path):
        """Helper to extract the pack name from ModpackUtil.lua."""
        try:
            lua_file_path = Path(lua_file_path)  # Ensure it's a Path object
            with lua_file_path.open(encoding="utf-8") as file:
                for line in file:
                    if line.startswith('--- VERSION:'):
                        return line.split(':')[1].strip()
        except IOError as e:
            logging.error(f"IOError reading {lua_file_path}: {e}", exc_info=True)
        return None

    def update_modpack_description(self):
        """Update the description label based on the selected modpack."""
        if not hasattr(self, 'description_label'):
            logging.error("Error: description_label is not initialized.")
            return
        
        selected_modpack = self.modpack_var.currentText()
        modpack_info = self.get_modpack_info(selected_modpack)

        self.description_label.setText(
            modpack_info['description'] if modpack_info else "Description not available."
        )

############################################################
# Middle functions (Download, install, update, uninstall)
############################################################

    def get_modpack_info(self, modpack_name):
        """Retrieve modpack information by name."""
        logging.info(f"[Modpack] Retrieving modpack info for: {modpack_name}")

        return next(
            (modpack for category in self.modpack_data.get('modpack_categories', [])
            for modpack in category.get('modpacks', [])
            if modpack['name'] == modpack_name),
            self._log_and_return_none(modpack_name)
        )

    def get_modpack_url(self, modpack_name):
        """Retrieve the URL for a given modpack."""
        modpack_info = self.get_modpack_info(modpack_name)
        modpack_url = modpack_info.get('url', '') if modpack_info else ''

        logging.info(f"[Modpack] Retrieved URL for {modpack_name}: {modpack_url}" if modpack_url
                    else f"[Modpack] URL not found for modpack: {modpack_name}")
        
        return modpack_url

    def _log_and_return_none(self, modpack_name):
        """Helper function to log and return None when modpack info is not found."""
        logging.warning(f"[Modpack] No information found for modpack: {modpack_name}")
        return None

    def prompt_for_installation(self):
        modpack_name = self.modpack_var.currentText()
        logging.info(f"[Modpack] User selected modpack for installation: {modpack_name}")

        modpack_url = self.get_modpack_url(modpack_name)
        if modpack_url:
            logging.info(f"[Modpack] Initiating download for {modpack_name} from {modpack_url}")
            self.download_modpack(main_window=self, clone_url=modpack_url)
        else:
            logging.error(f"[Modpack] Installation failed. Invalid modpack selected: {modpack_name}")
            QMessageBox.critical(self, "Error", "Invalid modpack selected.")

    def setup_button_blinking(self):
        """Blink the Download or Install button based on user's modpack status."""
        logging.debug("[Blink] Setting up button blinking...")

        if not hasattr(self, 'branch_var'):
            logging.warning("Warning: branch_var is not initialized yet. Delaying execution.")
            QTimer.singleShot(100, self.setup_button_blinking)  # Retry after a short delay
            return
        
        # Ensure settings are loaded before using them
        self.settings = self.load_settings()
        selected_modpack = self.modpack_var.currentText()
        selected_branch = self.branch_var.currentText()
        repo_name = f"{selected_modpack}-{selected_branch}" if selected_branch != "main" else selected_modpack

        modpack_directory = self.get_expanded_path("modpack_directory")
        repo_path = modpack_directory / repo_name
        modpack_downloaded = repo_path.exists()  # Check if folder exists

        mods_path = self.get_expanded_path("mods_directory") / "ModpackUtil"
        modpack_installed = mods_path.exists()  # Check if ModpackUtil folder exists
        lovely_injector_installed = self.check_lovely_injector_installed()

        # Paths for ModpackName.txt
        installed_modpack_name_file = mods_path / "ModpackName.txt"
        selected_modpack_name_file = repo_path / "Mods" / "ModpackUtil" / "ModpackName.txt"

        # Read content of both ModpackName.txt files, defaulting to empty string if missing
        installed_modpack_name = self.read_file_content(str(installed_modpack_name_file)) or ""
        logging.debug(f"installed_modpack_name = {installed_modpack_name}")
        selected_modpack_name = self.read_file_content(str(selected_modpack_name_file)) or ""
        logging.debug(f"selected_modpack_name = {selected_modpack_name}")

        is_different_modpack = installed_modpack_name != selected_modpack_name

        # Stop all previous blinking before setting new ones
        self.stop_blinking()

        # Stop blinking if modpack is installed and matches the selected one
        if modpack_installed and not is_different_modpack:
            logging.info("[Blink] Modpack is installed correctly and matches selected. Stopping all blinking.")
            self.stop_blinking()
            return  # Exit the function immediately

        # Ensure that NO buttons blink if a download is in progress
        if hasattr(self, "worker") and self.worker is not None and self.worker.isRunning():
            logging.info("[Blink] Download is still running. No buttons will blink.")
            return  # Exit early, preventing any blinking

        # Blink Install Lovely button if missing
        if not lovely_injector_installed:
            logging.debug("[Blink] Lovely Injector is missing. Blinking Install Lovely button.")
            self.blink_button(self.install_lovely_button)

        # Blink Download button if modpack isn't downloaded
        if not modpack_downloaded:
            logging.debug(f"[Blink] Modpack '{selected_modpack}' is not downloaded. Blinking Download button.")
            self.blink_button(self.download_button)

        # Blink Install button only if modpack is downloaded but not installed (or different)
        if modpack_downloaded and  is_different_modpack:
            logging.debug(f"[Blink] Modpack '{selected_modpack}' is downloaded but different from current install. Blinking Install button.")
            self.blink_button(self.install_button)

    def blink_button(self, button):
        """Make the given button blink with a soft yellow effect, preventing multiple timers."""
        
        if not hasattr(self, "blink_timers"):  
            self.blink_timers = {}  # Store active blink timers for each button

        # Stop existing blink timer if it exists
        if button in self.blink_timers and self.blink_timers[button].isActive():
            self.blink_timers[button].stop()
            del self.blink_timers[button]

        self.blink_state = True  # Track blinking state
        self.blink_timers[button] = QTimer(self)

        def toggle_button_style():
            """Toggle the button color for blinking effect."""
            self.blink_state = not self.blink_state
            if self.blink_state:
                button.setStyleSheet("""
                QPushButton {
                    font: 12pt 'Helvetica';
                    background-color: rgba(255, 255, 150, 180);
                }
                QPushButton:hover {
                    background-color: #dadada;
                }
                QPushButton:pressed {
                    background-color: #bcbcbc;
                }
            """)
                
            else:
                button.setStyleSheet("""
                QPushButton {
                    font: 12pt 'Helvetica';
                    background-color: none;
                }
                QPushButton:hover {
                    background-color: #dadada;
                }
                QPushButton:pressed {
                    background-color: #bcbcbc;
                }
            """)

        self.blink_timers[button].timeout.connect(toggle_button_style)
        self.blink_timers[button].start(500)  # Set blinking interval (500ms)

    def stop_blinking(self):
        """Stops all active blink timers and resets button styles."""
        if hasattr(self, "blink_timers"):
            for button, timer in self.blink_timers.items():
                timer.stop()
                button.setStyleSheet("""
                QPushButton {
                    font: 12pt 'Helvetica';
                    background-color: none;
                }
                QPushButton:hover {
                    background-color: #dadada;
                }
                QPushButton:pressed {
                    background-color: #bcbcbc;
                }
            """)

            self.blink_timers.clear()  # Remove all stored timers

    def download_modpack(self, main_window=None, clone_url=None):
        """Download the selected modpack with a prompt for overwriting."""
        modpack_name = self.modpack_var.currentText()
        selected_branch = self.branch_var.currentText()
        repo_url = clone_url or self.get_modpack_url(modpack_name)

        if not repo_url:
            logging.error(f"[Download] Invalid modpack URL for {modpack_name}.")
            QMessageBox.critical(self, "Error", "Invalid modpack URL.")
            return

        # Define the full path for the repository
        folder_name = f"{modpack_name}-{selected_branch}" if selected_branch != "main" else modpack_name
        modpack_directory = self.get_expanded_path("modpack_directory")
        repo_path = modpack_directory / folder_name

        logging.info(f"[Download] Preparing to download {modpack_name} from {repo_url} to {repo_path}.")

        # Stop all blinking when download starts (Download & Install)
        self.stop_blinking()

        # Check if the folder already exists
        if repo_path.exists():
            logging.info(f"[Download] Folder '{folder_name}' already exists. Prompting for overwrite.")
            response = QMessageBox.question(
                self,
                "Overwrite Existing Modpack",
                f"The folder '{folder_name}' already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if response == QMessageBox.StandardButton.No:
                logging.info(f"[Download] User chose not to overwrite {repo_path}.")
                return  # Exit early if the user does not want to overwrite

            # If Yes, delete the existing folder
            try:
                shutil.rmtree(repo_path, onerror=readonly_handler)  # Remove the folder and its contents
                logging.info(f"[Download] Deleted existing folder: {repo_path}")
            except Exception as e:
                logging.error(f"[Download] Failed to delete existing folder {repo_path}: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to delete existing folder: {str(e)}")
                return

        # Ensure the Modpacks folder exists
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Create and display the progress dialog for updating
        self.progress_dialog = QProgressDialog("", None, 0, 0)  # Pass None to remove the cancel button
        self.progress_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No title bar
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)  # Modal
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)

        theme_styles = {
            "Light": """
                QProgressDialog {
                    border: 3px solid #555;
                    background-color: #fefefe;
                }
                QLabel {
                    font: 24px 'Helvetica';
                    font-weight: bold;
                    color: #000000;
                    background-color: transparent;
                }
            """,
            "Dark": """
                QProgressDialog {
                    border: 3px solid #555;
                    background-color: #222222;
                }
                QLabel {
                    font: 24px 'Helvetica';
                    font-weight: bold;
                    color: #ffffff;
                    background-color: transparent;
                }
            """
        }
        self.progress_dialog.setStyleSheet(theme_styles.get(self.settings.get("theme"), theme_styles["Light"]))

        # Create a custom QLabel for the message with the modpack name
        self.label = QLabel(f"Downloading {modpack_name}({selected_branch})...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("QLabel { background-color: transparent; }")

        self.elapsed_time_label = QLabel("Elapsed time: 00:00\n\n")  # Show the elapsed time
        self.elapsed_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.elapsed_time_label.setStyleSheet("QLabel { font: 10pt 'Helvetica'; font-weight: normal; background-color: transparent; }")

        # Create a layout for the dialog and add the label
        layout = QVBoxLayout(self.progress_dialog)
        layout.addWidget(self.label)
        layout.addWidget(self.elapsed_time_label)

        self.progress_dialog.setLayout(layout)
        self.progress_dialog.show()

        # Center the progress dialog relative to the parent window
        if isinstance(self, QWidget):
            parent_geometry = self.geometry()
            dialog_geometry = self.progress_dialog.frameGeometry()
            dialog_geometry.moveCenter(parent_geometry.center())
            self.progress_dialog.move(dialog_geometry.topLeft())

        QApplication.processEvents()

        # Start the timer
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.timer.start(1000)  # Update every second

        # Create a ModpackDownloadWorker instance
        self.worker = ModpackDownloadWorker(repo_url, folder_name, selected_branch, modpack_directory, force_update=True)
        self.worker.finished.connect(self.on_download_finished)

        # Start the worker thread
        logging.info(f"[Download] Starting modpack download for {modpack_name} ({selected_branch}).")
        self.worker.start()

    def update_elapsed_time(self):
        """Update elapsed time in the progress dialog."""
        elapsed_seconds = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_seconds, 60)
        self.elapsed_time_label.setText(f"Elapsed time: {minutes:02}:{seconds:02}\n")
        QApplication.processEvents()

    def on_download_finished(self, success, message):

        # Stop the timer
        self.timer.stop()
        elapsed_seconds = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_seconds, 60)

        # Close the progress dialog
        self.progress_dialog.close()
        logging.info(f"[Download] Finished in {minutes:02}:{seconds:02} - {message}")

        # Show the result message (success or failure)
        QMessageBox.information(
            self, "Download Status", f"{message}\nElapsed time: {minutes:02}:{seconds:02}"
        ) if success else QMessageBox.critical(
            self, "Error", f"{message}\nElapsed time: {minutes:02}:{seconds:02}"
        )

        # If successful, verify the integrity of the downloaded modpack
        if success:
            logging.info(f"[Download] Successfully downloaded {self.modpack_var.currentText()}. Verifying integrity.")
            self.verify_modpack_integrity()

        # Only now should Install button blink
        self.setup_button_blinking()
        self.load_settings()  # Reload the settings after the download

        # Check the setting and install modpack if needed
        if success and self.settings.get("auto_install", False):
            logging.info("[Download] Auto-install enabled. Installing modpack.")
            self.install_modpack()

    def update_modpack(self):
        """Update the selected modpack with branch support."""
        modpack_name = self.modpack_var.currentText()
        repo_url = self.get_modpack_url(modpack_name)
        selected_branch = self.branch_var.currentText()

        if not repo_url:
            logging.error(f"[Update] Invalid modpack URL for {modpack_name}.")
            QMessageBox.critical(self, "Error", "Invalid modpack URL.")
            return
    
        # Ensure consistent use of the Modpacks folder
        modpack_directory = self.get_expanded_path("modpack_directory")
        modpack_directory.mkdir(parents=True, exist_ok=True)

        repo_name = f"{modpack_name}-{selected_branch}" if selected_branch != "main" else modpack_name
        repo_path = modpack_directory / repo_name

        logging.info(f"[Update] Starting update for {modpack_name} ({selected_branch}). Repo path: {repo_path}")

        # Check if the repository exists in the Modpacks folder
        if not repo_path.is_dir():
            logging.warning(f"[Update] Repository {repo_name} not found. Prompting user for cloning.")
            response = QMessageBox.question(
                self, "Repository Not Found",
                f"Repository '{repo_name}' not found. Attempt to clone?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if response == QMessageBox.StandardButton.No:
                return
            
            try:
                logging.info(f"[Update] Cloning repository {repo_url} for {modpack_name}.")
                self.download_modpack(main_window=self, clone_url=repo_url)
                return  # Exit early since cloning will take over

            except Exception as e:
                logging.error(f"[Update] Failed to clone repository {repo_url}: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to clone repository: {str(e)}")
                return

        # Create and display the progress dialog for updating
        self.progress_dialog = QProgressDialog("", None, 0, 0)  # Pass None to remove the cancel button
        self.progress_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No title bar
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)  # Modal
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)

        theme_styles = {
            "Light": """
                QProgressDialog {
                    border: 3px solid #555;
                    background-color: #fefefe;
                }
                QLabel {
                    font: 24px 'Helvetica';
                    font-weight: bold;
                    color: #000000;
                    background-color: transparent;
                }
            """,
            "Dark": """
                QProgressDialog {
                    border: 3px solid #555;
                    background-color: #222222;
                }
                QLabel {
                    font: 24px 'Helvetica';
                    font-weight: bold;
                    color: #ffffff;
                    background-color: transparent;
                }
            """
        }
        self.progress_dialog.setStyleSheet(theme_styles.get(self.settings.get("theme"), theme_styles["Light"]))

        # Create a custom QLabel for the message with the modpack name
        self.label = QLabel(f"Updating {modpack_name}({selected_branch})...")  # Show the name of the modpack
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align the text
        self.label.setStyleSheet("QLabel { background-color: transparent; }")

        self.elapsed_time_label = QLabel("Elapsed time: 00:00\n\n")
        self.elapsed_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.elapsed_time_label.setStyleSheet("QLabel { font: 10pt 'Helvetica'; font-weight: normal; background-color: transparent; }")

        # Create a layout for the dialog and add the label
        layout = QVBoxLayout(self.progress_dialog)
        layout.addWidget(self.label)
        layout.addWidget(self.elapsed_time_label)

        self.progress_dialog.setLayout(layout)
        self.progress_dialog.show()

        # Center the progress dialog relative to the parent window
        if isinstance(self, QWidget):
            parent_geometry = self.geometry()
            dialog_geometry = self.progress_dialog.frameGeometry()
            dialog_geometry.moveCenter(parent_geometry.center())
            self.progress_dialog.move(dialog_geometry.topLeft())

        QApplication.processEvents()

        self.start_time = time.time()  # Start the timer

        # Set a timer to update elapsed time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.timer.start(1000)  # Update every second

        # Create the worker for updating the modpack
        self.worker = ModpackUpdateWorker(repo_url, repo_name, selected_branch, modpack_directory)
        self.worker.finished.connect(self.on_update_finished)

        # Start the worker (background task)
        logging.info(f"[Update] Starting background update process for {modpack_name} ({selected_branch}).")
        self.worker.start()

    def on_update_finished(self, success, message):
        """Handle the completion of the update process."""

        # Stop the timer
        self.timer.stop()
        elapsed_seconds = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_seconds, 60)

        # Close the progress dialog
        self.progress_dialog.close()
        logging.info(f"[Update] Finished in {minutes:02}:{seconds:02} - {message}")

        # Show the result message (success or failure)
        QMessageBox.information(
            self, "Update Status", f"{message}\nElapsed time: {minutes:02}:{seconds:02}"
        ) if success else QMessageBox.critical(
            self, "Error", f"{message}\nElapsed time: {minutes:02}:{seconds:02}"
        )

        # If successful, verify the integrity of the downloaded modpack
        if success:
            logging.info(f"[Update] Successfully updated {self.modpack_var.currentText()}. Verifying integrity.")
            self.verify_modpack_integrity()
            self.blink_button(self.install_button)

            # Check the setting and install modpack if needed
            if self.settings.get("auto_install", False):
                logging.info("[Update] Auto-install enabled. Installing modpack.")
                self.install_modpack()

        else:
            logging.warning("[Update] Update failed. Attempting full redownload.")
            user_response = QMessageBox.question(
                self, "Update Failed",
                "Quick update failed. Do you want to redownload the modpack?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if user_response == QMessageBox.StandardButton.Yes:
                self.download_modpack(main_window=self)

        self.load_settings()  # Reload the settings after the update

    def install_modpack(self):
        """Install the selected modpack with platform auto-detection for paths."""
        logging.info("[Install] Starting modpack installation.")

        self.settings = self.load_settings()
        skip_mod_selection = self.settings.get("skip_mod_selection", False)
        modpack_name = self.modpack_var.currentText()
        selected_branch = self.branch_var.currentText()
        modpack_info = self.get_modpack_info(modpack_name)

        if not modpack_info:
            logging.error(f"[Install] Modpack information not found for {modpack_name}.")
            QMessageBox.critical(self, "Error", "Modpack information not found.")
            return

        # Handle repository name and path
        repo_name = f"{modpack_name}-{selected_branch}" if selected_branch != "main" else modpack_name
        modpack_directory = self.get_expanded_path("modpack_directory")
        repo_path = modpack_directory / repo_name
        mods_src = repo_path / "Mods"

        # Determine the install path based on the platform
        install_path = self.get_expanded_path("mods_directory")

        mod_list = self.get_mod_list(mods_src) if mods_src.is_dir() else []

        # Handle special cases based on URL type
        repo_name = modpack_info["url"].split("/")[-1].replace(".git", "") if modpack_info["url"].endswith(".git") else modpack_name.replace(" ", "_")

        try:
            # If a modpack is selected but doesn't exist, show an error
            if not repo_path.is_dir():
                logging.error(f"[Install] Modpack repository does not exist: {repo_path}")
                QMessageBox.critical(self, "Error", f"Modpack {repo_path} does not exist. Please download first.")
                return

            # Check if the Mods folder exists in the repository
            if not mods_src.is_dir():
                logging.error(f"[Install] Mods folder missing in repository: {mods_src}")
                QMessageBox.critical(self, "Error", f"Mods folder not found in {repo_path}. Please force download and try again.")
                return

            # Create install path if necessary
            install_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"[Install] Ensured mods install path exists: {install_path}")

            # If skipping mod selection, install all mods immediately
            if skip_mod_selection:
                # Install all mods without showing the mod selection popup
                logging.info("[Install] Skipping mod selection. Installing all mods.")
                self.excluded_mods = []  # No mods are excluded
                self.install_mods(None)  # Pass None as we don't have a popup

                # Delay opening of custom mod selection popup to ensure UI updates
                QTimer.singleShot(100, self.popup_custom_mod_selection)
            else:
                # Show mod selection popup
                logging.info("[Install] Showing mod selection popup.")
                self.popup_mod_selection(mod_list, dependencies)
        
            logging.info(f"[Install] Modpack {modpack_name} installation process completed.")

        except Exception as e:
            logging.error(f"[Install] Unexpected error during installation: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred during installation: {str(e)}")

    def get_mod_list(self, mods_src):
        """Retrieve a sorted list of mods from the mods folder."""
        try:
            mod_list = sorted(
                [folder.name for folder in mods_src.iterdir() if folder.is_dir()],
                key=str.lower
            )
            logging.debug(f"[Install] Retrieved mod list from {mods_src}: {mod_list}")
            return mod_list
        except FileNotFoundError:
            logging.error(f"[Install] Mods folder not found: {mods_src}")
            QMessageBox.critical(self, "Error", f"Mods folder not found.")
            return []

    def popup_mod_selection(self, mod_list, dependencies):
        logging.info("[Mod Selection] Opening mod selection popup.")

        mod_vars = []  # Clear any existing data
        always_installed = {"Steamodded", "ModpackUtil"}  # Mods that are always installed and not displayed

        if self.install_popup_open:
            logging.warning("[Mod Selection] Install popup is already open. Skipping re-opening.")
            return

        self.install_popup_open = True

        # Ensure metadata is available
        if not self.metadata:
            logging.error("[Mod Selection] Metadata is missing. Cannot load mod list.")
            QMessageBox.critical(self, "Error", "Metadata for mods is not loaded. Please check your internet connection.")
            return

        # Create a popup window for mod selection
        popup = QDialog(self)
        popup.setWindowTitle("Mod Selection")
        popup.resize(600, 500)

        # Create a QSplitter to divide left (filters) and middle (mods) panels
        splitter = QSplitter(popup)
        splitter.setOrientation(Qt.Orientation.Horizontal)

        # Get the currently available mod list (only mods in the loaded modpack)
        self.current_mods = set(mod_list)

        # Extract unique genres and tags from metadata and count their occurrences
        genre_counts = {}
        tag_counts = {}

        self.favorite_count = 0
        self.selected_count = -2
        self.deselected_count = 0

        for mod in self.current_mods:
            if mod in self.metadata:
                mod_info = self.metadata[mod]

                if mod_info.get("Genre"):
                    genre = mod_info["Genre"]
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1  # Count genres

                if isinstance(mod_info.get("Tags"), list):
                    for tag in mod_info["Tags"]:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1  # Count tags

            # Count Favorites
            if mod in self.favorite_mods:
                self.favorite_count += 1

            # Count Selected and Deselected Mods
            if mod in self.excluded_mods:
                self.deselected_count += 1
            else:
                self.selected_count += 1

        # Sort genres and tags based on names
        genres = sorted(genre_counts.keys())
        tags = sorted(tag_counts.keys())

        # Left panel (Filters)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 0)

        # Create a container for the search bar and search result count
        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # Search bar
        self.search_bar = QLineEdit(popup)
        self.search_bar.setPlaceholderText("Search mods...")
        self.search_bar.textChanged.connect(self.filter_mods)
        search_layout.addWidget(self.search_bar)

        # Search results count label
        self.search_result_label = QLabel("Results: 0", popup)
        self.search_result_label.hide()  # Hide initially
        search_layout.addWidget(self.search_result_label)

        # Add search container to the left panel (ensuring it's pinned at the top)
        left_layout.addWidget(search_container)

        filters_scroll_area = QScrollArea()
        filters_scroll_area.setWidgetResizable(True)

        # Container for filters & mod list (inside scroll area)
        filters_container = QWidget()
        filters_layout = QVBoxLayout(filters_container)
        filters_layout.setContentsMargins(0, 0, 0, 0)

        # Favorite mods filter
        self.favorite_filter_checkbox = QCheckBox(f"Favorites ({self.favorite_count})", popup)
        self.show_checked_checkbox = QCheckBox(f"Selected ({self.selected_count})", popup)
        self.show_unchecked_checkbox = QCheckBox(f"Deselected ({self.deselected_count})", popup)

        filters_layout.addWidget(self.favorite_filter_checkbox)
        filters_layout.addWidget(self.show_checked_checkbox)
        filters_layout.addWidget(self.show_unchecked_checkbox)

        # Connect the "Show favorites" checkbox to the filter function
        self.favorite_filter_checkbox.stateChanged.connect(self.filter_mods)
        self.show_checked_checkbox.stateChanged.connect(self.filter_mods)
        self.show_unchecked_checkbox.stateChanged.connect(self.filter_mods)
        self.search_bar.textChanged.connect(self.filter_mods)

        # **Fix Toggle Issues: Ensure Only One of the Checkboxes is Checked at a Time**
        def handle_exclusive_filtering(checkbox_triggered):
            if checkbox_triggered == "checked":
                self.show_unchecked_checkbox.blockSignals(True)  # Temporarily disable signal to prevent loop
                self.show_unchecked_checkbox.setChecked(False)
                self.show_unchecked_checkbox.blockSignals(False)
            elif checkbox_triggered == "unchecked":
                self.show_checked_checkbox.blockSignals(True)
                self.show_checked_checkbox.setChecked(False)
                self.show_checked_checkbox.blockSignals(False)
            self.filter_mods()  # Always apply filters after state change

        self.show_checked_checkbox.stateChanged.connect(lambda: handle_exclusive_filtering("checked") if self.show_checked_checkbox.isChecked() else self.filter_mods())
        self.show_unchecked_checkbox.stateChanged.connect(lambda: handle_exclusive_filtering("unchecked") if self.show_unchecked_checkbox.isChecked() else self.filter_mods())

        # Genre filter section (only if genres exist)
        self.genre_checkboxes = []
        if genres:
            genre_label = QLabel("Genres", popup)
            genre_label.setStyleSheet("font-weight: bold;")
            filters_layout.addWidget(genre_label)

            for genre in genres:
                genre_checkbox = QCheckBox(f"{genre} ({genre_counts[genre]})", popup)  # Add count
                filters_layout.addWidget(genre_checkbox)
                self.genre_checkboxes.append(genre_checkbox)

        # Tags filter section (only if tags exist)
        self.tag_checkboxes = []
        if tags:
            tags_label = QLabel("Tags", popup)
            tags_label.setStyleSheet("font-weight: bold;")
            filters_layout.addWidget(tags_label)

            for tag in tags:
                tag_checkbox = QCheckBox(f"{tag} ({tag_counts[tag]})", popup)  # Add count
                filters_layout.addWidget(tag_checkbox)
                self.tag_checkboxes.append(tag_checkbox)

        # Set the scrollable content
        filters_container.setLayout(filters_layout)
        filters_scroll_area.setWidget(filters_container)

        # Add the search container and scrollable filters to the left layout
        left_layout.addWidget(filters_scroll_area)  # Filters & mod list are scrollable

        # Apply the layout to the left panel
        left_panel.setLayout(left_layout)

        # Middle panel (Scrollable mod list)
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)

        middle_scroll_area = QScrollArea(popup)
        middle_scroll_area.setWidgetResizable(True)

        mod_container = QWidget()
        mod_layout = QVBoxLayout(mod_container)
        mod_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align mods to the top of the container

        def add_context_menu(mod_row_container, mod, metadata):
            """Add a right-click context menu to the mod row."""
            def open_discord():
                discord_url = metadata.get(mod, {}).get("Discord Link", None)
                if discord_url:
                    webbrowser.open(discord_url)
                else:
                    QMessageBox.information(mod_row_container, "Info", "Discord link not available for this mod.")

            def open_mod_page():
                mod_page_url = metadata.get(mod, {}).get("Page Link", None)
                if mod_page_url:
                    webbrowser.open(mod_page_url)
                else:
                    QMessageBox.information(mod_row_container, "Info", "Mod page link not available for this mod.")

            # Add context menu to mod row
            def show_context_menu(event):
                if event.button() == Qt.MouseButton.RightButton:
                    context_menu = QMenu(mod_row_container)
                    discord_action = context_menu.addAction("Visit Discord Channel")
                    github_action = context_menu.addAction("Visit Mod Page")

                    # Connect actions to their respective functions
                    discord_action.triggered.connect(open_discord)
                    github_action.triggered.connect(open_mod_page)

                    # Show the menu at the cursor's position
                    context_menu.exec(event.globalPosition().toPoint())

            mod_row_container.mousePressEvent = show_context_menu

        def toggle_favorite(label, mod):
            """Toggle favorite state for the given mod."""
            if mod in self.favorite_mods:
                self.favorite_mods.remove(mod)
                label.setText("☆")  # Empty star
            else:
                self.favorite_mods.add(mod)
                label.setText("★")  # Solid star
            
            self.save_favorites()  # Save favorites whenever they are toggled
            self.filter_mods()  # Reapply the filter to reflect changes immediately

        for mod in mod_list:
            if mod in always_installed:
                continue  # Skip mods in the excluded list

            mod_row_container = QWidget(mod_container)
            mod_row_layout = QHBoxLayout(mod_row_container)
            mod_row_layout.setContentsMargins(0, 0, 0, 0)
            mod_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            mod_checkbox = QCheckBox(mod, popup)
            mod_checkbox.setChecked(mod not in self.excluded_mods)  # Default to checked

            # Ensure changing a mod checkbox updates the filter
            mod_checkbox.stateChanged.connect(self.filter_mods)

            # Add a star label for favorite mods
            star_label = QLabel("★" if mod in self.favorite_mods else "☆", popup)
            star_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Clickable star
            star_label.mousePressEvent = lambda _, mod=mod, label=star_label: toggle_favorite(label, mod)

            if self.settings.get("theme") == "Light":
                star_label.setStyleSheet("font-size: 20px; color: black;")

            elif self.settings.get("theme") == "Dark":
                star_label.setStyleSheet("font-size: 20px; color: white;")

            # Attach the context menu to the mod row container
            add_context_menu(mod_row_container, mod, self.metadata)

            # Retrieve metadata for the mod
            mod_metadata = self.metadata.get(mod, {})
            genre = mod_metadata.get("Genre", "Unknown")
            tags = ", ".join(mod_metadata.get("Tags", []))
            description = mod_metadata.get("Description", "No description available.")
            
            # Combine metadata into a tooltip text
            tooltip_text = f"<b>Genre:</b> {genre}<br><b>Tags:</b> {tags}<br><b>Description:</b> {description}"
            
            # Set the tooltip for the checkbox
            mod_checkbox.setToolTip(tooltip_text)

            # Append all elements to mod_vars
            mod_vars.append((mod_row_container, mod, mod_checkbox, star_label))

            # Add widgets to the layout
            mod_row_layout.addWidget(star_label)
            mod_row_layout.addWidget(mod_checkbox)
            mod_layout.addWidget(mod_row_container)

            # Connect state change event for dependency handling
            mod_checkbox.stateChanged.connect(
                lambda _, mod_name=mod, mod_var=mod_checkbox: self.handle_dependencies(mod_name, mod_var, mod_vars, dependencies)
            )

        middle_scroll_area.setWidget(mod_container)
        middle_layout.addWidget(middle_scroll_area)

        # Add a right panel for presets
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_label = QLabel("Modpack Presets", popup)
        right_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(right_label)

        # List of presets
        self.presets_dropdown = QComboBox(popup)
        self.update_presets_dropdown()  # Populate the dropdown
        right_layout.addWidget(self.presets_dropdown)

        # Buttons to manage presets
        save_preset_button = QPushButton("Save Preset", popup)
        save_preset_button.clicked.connect(lambda: self.save_preset(mod_vars))
        right_layout.addWidget(save_preset_button)

        load_preset_button = QPushButton("Load Preset", popup)
        load_preset_button.clicked.connect(lambda: self.load_preset(mod_vars))
        right_layout.addWidget(load_preset_button)

        delete_preset_button = QPushButton("Delete Preset", popup)
        delete_preset_button.clicked.connect(self.delete_preset)
        right_layout.addWidget(delete_preset_button)

        # Spacer to align elements at the top
        right_layout.addStretch()

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(middle_scroll_area)
        splitter.addWidget(right_panel)

        # Set fixed width for left panel
        splitter.setSizes([500, 700, 300])

        # Layout for popup
        main_layout = QVBoxLayout(popup)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add the splitter (which contains the left, middle, and right panels)
        main_layout.addWidget(splitter, 1)  # The '1' makes it stretchable
        
        self.mod_vars = mod_vars

        for checkbox in self.genre_checkboxes + self.tag_checkboxes:
            checkbox.stateChanged.connect(self.filter_mods)

        # Buttons for actions
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Buttons for actions
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)

        clear_button = QPushButton("Clear All", popup)
        reverse_button = QPushButton("Reverse Select", popup)
        feel_lucky_button = QPushButton("I Feel Lucky", popup)
        save_button = QPushButton("Save && Install", popup)

        clear_button.clicked.connect(lambda: [checkbox.setChecked(False) for _, _, checkbox, _ in mod_vars])
        reverse_button.clicked.connect(lambda: self.reverse_select_with_dependencies(mod_vars, dependencies))
        feel_lucky_button.clicked.connect(lambda: [checkbox.setChecked(random.choice([True, False])) for _, _, checkbox, _ in mod_vars])
        save_button.clicked.connect(lambda: self.save_and_install([(mod, checkbox) for _, mod, checkbox, _ in mod_vars], popup))

        button_layout.addWidget(clear_button)
        button_layout.addWidget(reverse_button)
        button_layout.addWidget(feel_lucky_button)
        button_layout.addWidget(save_button)

        bottom_layout.addWidget(button_container)

        # Add checkboxes for Backup and Remove Mods
        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)

        # Create the "Backup Mods Folder" and "Remove Mods Folder" checkboxes
        self.backup_checkbox = QCheckBox("Backup Mods Folder", popup)
        self.remove_checkbox = QCheckBox("Remove Mods Folder", popup)

        self.backup_checkbox.setChecked(self.settings.get("backup_mods", False))
        self.remove_checkbox.setChecked(self.settings.get("remove_mods", True))

        checkbox_layout.addWidget(self.backup_checkbox)
        checkbox_layout.addWidget(self.remove_checkbox)

        bottom_layout.addWidget(checkbox_container)

        # Add the bottom layout to the main layout **AFTER** the splitter
        main_layout.addStretch()  # This makes the top stretchable
        main_layout.addWidget(bottom_container)  # Keeps bottom elements fixed

        # Close event handler to reset the flag when the window is closed
        def on_close():
            self.install_popup_open = False
            logging.info("[Mod Selection] Mod selection popup closed.")
            popup.close()

        popup.finished.connect(on_close)
        popup.exec()

    # Integrate the "Show favorites" filter
    def filter_mods(self):
        """Dynamically filter the mod list based on search queries, genre/tags, and favorites."""
        logging.info("[Filter] Applying mod filters...")

        query = self.search_bar.text().strip().lower()

        selected_filters = {
            "genres": {checkbox.text().split(" (")[0] for checkbox in self.genre_checkboxes if checkbox.isChecked()},
            "tags": {checkbox.text().split(" (")[0] for checkbox in self.tag_checkboxes if checkbox.isChecked()},
        }
        
        show_only_favorites = self.favorite_filter_checkbox.isChecked()
        show_only_checked = self.show_checked_checkbox.isChecked()
        show_only_unchecked = self.show_unchecked_checkbox.isChecked()

        # Reset counts before recalculating
        favorite_count = 0
        selected_count = 0
        deselected_count = 0
        match_count = 0

        always_installed = {"Steamodded", "ModpackUtil"}  # Mods that are always installed

        for mod_row_container, mod, checkbox, _ in self.mod_vars:
            if mod not in self.current_mods or mod in always_installed:  # Ignore mods not in the loaded modpack
                mod_row_container.setVisible(False)
                continue

            mod_metadata = self.metadata.get(mod, {})
            mod_genre = mod_metadata.get("Genre", "Unknown")
            mod_tags = set(mod_metadata.get("Tags", []))

            is_favorite = mod in self.favorite_mods  # Use self.favorite_mods directly
            is_checked = checkbox.isChecked()

            # Update counts dynamically
            if is_favorite:
                favorite_count += 1
            if is_checked:
                selected_count += 1
            else:
                deselected_count += 1

            matches_query = query in mod.lower()
            matches_genre = not selected_filters["genres"] or mod_genre in selected_filters["genres"]
            matches_tags = not selected_filters["tags"] or bool(selected_filters["tags"].intersection(mod_tags))

            # Determine visibility
            should_show = matches_query and matches_genre and matches_tags

            if show_only_favorites:
                should_show = should_show and is_favorite
            if show_only_checked and show_only_unchecked:
                should_show = False  # Prevent both filters from being active at once
            if show_only_checked:
                should_show = should_show and is_checked  # Checkbox is checked
            if show_only_unchecked:
                should_show = should_show and not is_checked

            mod_row_container.setVisible(should_show)

            if should_show:
                match_count += 1  # Count visible mods

        # Log the filtering results
        logging.debug(f"[Filter] Query: '{query}', Genres: {selected_filters['genres']}, Tags: {selected_filters['tags']}")
        logging.debug(f"[Filter] Showing {match_count} mods. Favorites: {favorite_count}, Selected: {selected_count}, Deselected: {deselected_count}")

        # Update the search results count dynamically
        if query:
            self.search_result_label.setText(f"Results: {match_count}")
            self.search_result_label.show()
        else:
            self.search_result_label.hide()  # Hide label when search bar is empty

        # Update checkboxes to reflect new counts dynamically
        self.favorite_filter_checkbox.setText(f"Favorites ({favorite_count})")
        self.show_checked_checkbox.setText(f"Selected ({selected_count})")
        self.show_unchecked_checkbox.setText(f"Deselected ({deselected_count})")

        logging.info("[Filter] Mod filtering completed successfully.")

    def popup_custom_mod_selection(self):
        """Displays the custom mod selection screen after the main modpack selection."""
        logging.info("[Custom Mods] Opening custom mod selection popup.")

        popup = QDialog(self)
        popup.setWindowTitle("Custom Mod Selection")

        layout = QVBoxLayout(popup)

        # Title
        title_label = QLabel("Select Custom Mods to Install")
        layout.addWidget(title_label)

        # Always initialize custom_mod_checkboxes before use
        self.custom_mod_checkboxes = {}

        # Check if the Custom Mods folder exists
        modpack_directory = self.get_expanded_path("modpack_directory")
        custom_mods_dir = modpack_directory / "Custom"
        
        if not custom_mods_dir.exists() or not any(custom_mods_dir.iterdir()):
            logging.warning("[Custom Mods] No custom mods found for installation.")
            QMessageBox.warning(self, "No Custom Mods Found", "No custom mods are available for installation.")
            popup.close()
            return

        # Get the list of available custom mods
        mod_list = [mod.name for mod in custom_mods_dir.iterdir() if mod.is_dir()]
        logging.info(f"[Custom Mods] Available custom mods: {mod_list}")

        # Scroll Area for Mod List
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        mod_container = QWidget()
        mod_layout = QVBoxLayout(mod_container)

        # Create checkboxes for each mod
        for mod in mod_list:
            mod_checkbox = QCheckBox(mod)
            mod_checkbox.setChecked(True)  # Default to checked
            mod_layout.addWidget(mod_checkbox)
            self.custom_mod_checkboxes[mod] = mod_checkbox  # Store checkboxes for custom mods

        mod_container.setLayout(mod_layout)
        scroll_area.setWidget(mod_container)
        layout.addWidget(scroll_area)

        # Buttons
        next_button = QPushButton("Install")
        next_button.clicked.connect(lambda: self.install_custom_modpack(popup))
        layout.addWidget(next_button)

        popup.setLayout(layout)
        logging.info("[Custom Mods] Custom mod selection popup displayed.")
        popup.exec()

    def install_custom_modpack(self, popup):
        """Installs the selected custom modpack after the Next button is clicked."""
        popup.close()  # Close the selection window
        logging.info("[Custom Mods] Starting installation of selected custom mods.")
            
        # Ensure custom_mod_checkboxes is initialized before accessing it
        if not hasattr(self, "custom_mod_checkboxes") or not self.custom_mod_checkboxes:
            logging.warning("[Custom Mods] No mods selected for installation.")
            QMessageBox.warning(self, "No Mods Selected", "No custom mods were selected for installation.")
            return

        # Determine the Mods folder path
        mods_dir = self.get_expanded_path("mods_directory")
        mods_dir.mkdir(parents=True, exist_ok=True)  # Ensure Mods directory exists

        # Copy selected mods into the Mods directory
        selected_mods = [mod for mod, checkbox in self.custom_mod_checkboxes.items() if checkbox.isChecked()]

        if not selected_mods:
            logging.warning("[Custom Mods] No mods were selected. Installation aborted.")
            QMessageBox.warning(self, "No Mods Selected", "No custom mods will be installed.")
            return

        logging.info(f"[Custom Mods] Selected mods for installation: {selected_mods}")

        modpack_directory = self.get_expanded_path("modpack_directory")
        custom_mods_dir = modpack_directory / "Custom"

        for mod in selected_mods:
            source_path = custom_mods_dir / mod
            dest_path = mods_dir / mod

            try:
                if source_path.exists():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    logging.info(f"[Custom Mods] Installed mod: {mod}")
                else:
                    logging.error(f"[Custom Mods] Source path missing: {source_path}")

            except Exception as e:
                logging.error(f"[Custom Mods] Error installing {mod}: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to install mod {mod}: {str(e)}")
        
        logging.info("[Custom Mods] Installation complete.")
        QMessageBox.information(self, "Install Complete", "Custom mods have been installed.")

    def handle_dependencies(self, mod, var, mod_vars, dependencies):
        """
        Handle mod dependencies when a checkbox state changes.
        Args:
            mod (str): The mod whose state changed.
            var (QCheckBox): The checkbox associated with the mod.
            mod_vars (list): List of (mod_row_container, mod_name, QCheckBox, star_label).
            dependencies (dict): Dependency mapping of mods.
        """
        logging.info(f"[Dependencies] Processing dependencies for {mod}")

        mod_dict = {mod_name: (mod_var, mod_row_container) for mod_row_container, mod_name, mod_var, _ in mod_vars}

        def include_required_mods(dependent_mod):
            required_mods = dependencies.get(dependent_mod, [])
            for required_mod in required_mods:
                required_var, required_container = mod_dict.get(required_mod, (None, None))
                if required_var and not required_var.isChecked() and required_container.isVisible():
                    logging.info(f"[Dependencies] Enabling required mod: {required_mod}")
                    required_var.blockSignals(True)
                    required_var.setChecked(True)
                    required_var.blockSignals(False)
                    include_required_mods(required_mod)

        def exclude_dependent_mods(required_mod):
            for dependent_mod, required_mods in dependencies.items():
                if required_mod in required_mods:
                    dependent_var, dependent_container = mod_dict.get(dependent_mod, (None, None))
                    if dependent_var and dependent_var.isChecked() and dependent_container.isVisible():
                        logging.info(f"[Dependencies] Disabling dependent mod: {dependent_mod}")
                        dependent_var.blockSignals(True)
                        dependent_var.setChecked(False)
                        dependent_var.blockSignals(False)
                        exclude_dependent_mods(dependent_mod)

        if var.isChecked():  # Include the mod
            include_required_mods(mod)
        else:  # Exclude the mod
            exclude_dependent_mods(mod)
        
        self.filter_mods()

    def reverse_select_with_dependencies(self, mod_vars, dependencies):
        """
        Reverse the checked state of visible mods and process dependencies afterward.
        Args:
            mod_vars (list): List of (mod_row_container, mod_name, QCheckBox, star_label).
            dependencies (dict): Dependency mapping of mods.
        """
        # Step 1: Flip the checked state of all visible mods
        for mod_row_container, mod_name, checkbox, _ in mod_vars:
            if mod_row_container.isVisible():
                checkbox.blockSignals(True)  # Prevent triggering dependency logic during the flip
                checkbox.setChecked(not checkbox.isChecked())
                checkbox.blockSignals(False)

        # Step 2: Process dependencies for all visible mods based on their new state
        for mod_row_container, mod_name, checkbox, _ in mod_vars:
            if mod_row_container.isVisible():
                self.handle_dependencies(mod_name, checkbox, mod_vars, dependencies)
                
        self.filter_mods()

    def save_preferences(self, mod_vars):
        # Collect mods that are unchecked (excluded from installation)
        excluded_mods = [mod for mod, var in mod_vars if not var.isChecked()]
        try:
            INSTALL_FILE.write_text(json.dumps(excluded_mods, indent=4))
            logging.info(f"[Preferences] Excluded mods saved: {excluded_mods}")
        except Exception as e:
            logging.error(f"[Preferences] Failed to save excluded mods: {e}", exc_info=True)

    def read_preferences(self):
        try:
            return json.loads(INSTALL_FILE.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("[Preferences] No saved preferences found. Returning empty list.")
            return []

    # Load favorites from the file
    def load_favorites(self):
        """Load favorite mods from a JSON file."""
        try:
            if FAVORITES_FILE.exists():
                self.favorite_mods = set(json.loads(FAVORITES_FILE.read_text()))
                logging.info("[Favorites] Loaded favorite mods.")
            else:
                self.favorite_mods = set()  # Initialize as an empty set if the file doesn't exist
                logging.info("[Favorites] No favorite mods file found. Initializing empty set.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"[Favorites] Error loading favorite mods: {e}", exc_info=True)
            self.favorite_mods = set()  # Default to empty set on failure

    # Save favorites to the file
    def save_favorites(self):
        """Save favorite mods to a JSON file."""
        try:
            FAVORITES_FILE.write_text(json.dumps(list(self.favorite_mods), indent=4))
            logging.info(f"[Favorites] Favorite mods saved: {self.favorite_mods}")
        except IOError as e:
            logging.error(f"[Favorites] Error saving favorite mods: {e}", exc_info=True)

    def reset_favorites_file(self):
        """Reset the favorites file if corrupted."""
        try:
            FAVORITES_FILE.write_text(json.dumps([]))  # Reset to an empty list
            logging.info("[Favorites] Reset favorite mods file to empty.")
        except Exception as e:
            logging.error(f"[Favorites] Failed to reset favorite mods file: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to reset favorite mods file. Error: {e}")

    def save_preset(self, mod_vars):
        """Save the current mod selection as a preset."""
        preset_name, ok = QInputDialog.getText(self, "Save Preset", "Enter a name for this preset:")
        if not ok or not preset_name.strip():
            return

        # Save selected mods as a preset
        selected_mods = [mod for _, mod, checkbox, _ in mod_vars if checkbox.isChecked()]
        presets = self.load_presets()
        presets[preset_name] = selected_mods
        self.write_presets(presets)

        logging.info(f"[Presets] Saved preset '{preset_name}' with mods: {selected_mods}")
        QMessageBox.information(self, "Preset Saved", f"Preset '{preset_name}' saved successfully.")
        self.update_presets_dropdown()

    def load_preset(self, mod_vars):
        """Load the selected preset and apply it to the mod selection."""
        preset_name = self.presets_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Load Preset", "No preset selected.")
            return

        presets = self.load_presets()
        selected_mods = presets.get(preset_name, [])
        if not selected_mods:
            logging.warning(f"[Presets] Attempted to load empty or invalid preset '{preset_name}'.")
            QMessageBox.warning(self, "Load Preset", f"Preset '{preset_name}' is empty or invalid.")
            return

        logging.info(f"[Presets] Loading preset '{preset_name}' with mods: {selected_mods}")

        for _, mod, checkbox, _ in mod_vars:
            checkbox.setChecked(mod in selected_mods)

    def delete_preset(self):
        """Delete the selected preset."""
        preset_name = self.presets_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Delete Preset", "No preset selected.")
            return

        presets = self.load_presets()
        if preset_name in presets:
            del presets[preset_name]
            self.write_presets(presets)
            logging.info(f"[Presets] Deleted preset '{preset_name}'.")
            QMessageBox.information(self, "Preset Deleted", f"Preset '{preset_name}' deleted successfully.")
            self.update_presets_dropdown()

    def load_presets(self):
        """Load presets from the JSON file."""
        try:
            return json.loads(PRESETS_FILE.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("[Presets] No presets file found or file is corrupted. Returning empty dictionary.")
            return {}

    def write_presets(self, presets):
        """Write presets to the JSON file."""
        # Ensure the settings folder exists
        SETTINGS_FOLDER.mkdir(parents=True, exist_ok=True)

        try:
            PRESETS_FILE.write_text(json.dumps(presets, indent=4))
            logging.info(f"[Presets] Presets saved to {PRESETS_FILE}")
        except Exception as e:
            logging.error(f"[Presets] Error saving presets: {e}", exc_info=True)

    def update_presets_dropdown(self):
        """Update the presets dropdown with the available presets."""
        presets = self.load_presets()
        self.presets_dropdown.clear()
        self.presets_dropdown.addItems(presets.keys())

    def install_mods(self, popup):
        """
        Install mods with a progress bar showing the current mod being copied.
        Args:
            popup (QDialog): The mod selection popup (optional).
        """
        logging.info("[Install] Starting mod installation.")

        # Read excluded mods
        excluded_mods = self.read_preferences()
        modpack_name = self.modpack_var.currentText()
        selected_branch = self.branch_var.currentText()
        repo_name = f"{modpack_name}-{selected_branch}" if selected_branch != "main" else modpack_name

        modpack_directory = self.get_expanded_path("modpack_directory")
        repo_path = modpack_directory / repo_name
        mods_src = repo_path / "Mods"

        """Check if the Mods directory exists and optionally back it up."""
        # Resolve platform-specific mods directory path
        mods_dir = self.get_expanded_path("mods_directory")

        # Ensure source Mods directory exists
        if not mods_src.exists():
            logging.error("[Install] Source Mods folder not found. Installation aborted.")
            QMessageBox.critical(self, "Error", "Source Mods folder not found. Installation aborted.")
            return

        # Check if the Mods directory exists
        if mods_dir.is_dir() and self.backup_checkbox.isChecked():
            # Create a timestamped backup folder name
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_folder = mods_dir.parent / f"Mods-backup-{timestamp}"

            try:
                # Move the Mods directory to the backup folder
                shutil.move(str(mods_dir), str(backup_folder))
                logging.info(f"[Install] Backup created at: {backup_folder}")
                QMessageBox.information(self, "Backup Successful", f"Mods folder successfully backed up to:\n{backup_folder}")

            except Exception as e:
                logging.error(f"[Install] Failed to backup Mods folder: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to backup Mods folder. Error: {str(e)}")
                return

        if self.remove_checkbox.isChecked():
            response = QMessageBox.question(
                self, "Warning",
                "The current 'Mods' folder will be erased. Do you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if response == QMessageBox.StandardButton.No:
                logging.info("[Install] Mods folder removal canceled by user.")
                return

            try:
                # Remove the Mods directory
                if os.path.exists(mods_dir):
                    shutil.rmtree(mods_dir, ignore_errors=True)
                    logging.info("[Install] Mods folder removed successfully.")
                    QMessageBox.information(self, "Success", "The 'Mods' folder has been removed successfully.")
            except Exception as e:
                logging.error(f"[Install] Failed to remove Mods folder: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to remove Mods folder. Error: {str(e)}")

        # Create a progress dialog
        progress_dialog = QProgressDialog("Installing mods...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Installation Progress")
        progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)

        # Ensure Mods directory exists
        mods_dir.mkdir(parents=True, exist_ok=True)

        # Always install "Steamodded" and "ModpackUtil"
        mandatory_mods = {"Steamodded", "ModpackUtil"}
        all_mods = mandatory_mods.union(set(os.listdir(mods_src)))
        filtered_mods = sorted([mod for mod in all_mods if mod not in excluded_mods or mod in mandatory_mods])

        try:
            # Iterate through mods and copy them
            total_mods = len(filtered_mods)
            for index, mod in enumerate(filtered_mods, start=1):
                source_mod_path = mods_src / mod
                destination_mod_path = mods_dir / mod

                # Update progress dialog
                progress_percentage = int((index / total_mods) * 100)
                progress_dialog.setValue(progress_percentage)
                progress_dialog.setLabelText(f"Copying mod: {mod} ({index}/{total_mods})")
                QApplication.processEvents()  # Keep the UI responsive

                # Handle user cancellation
                if progress_dialog.wasCanceled():
                    logging.warning("[Install] Installation canceled by user.")
                    QMessageBox.warning(self, "Installation Canceled", "The installation process was canceled.")
                    return

                # Perform the copy operation
                try:
                    shutil.copytree(source_mod_path, destination_mod_path, dirs_exist_ok=True)
                    logging.info(f"[Install] Installed mod: {mod}")
                except Exception as copy_error:
                    logging.error(f"[Install] Failed to copy {mod}: {copy_error}", exc_info=True)
                    QMessageBox.warning(self, "Copy Error", f"Failed to copy {mod}. Error: {copy_error}")

            # Close the progress dialog
            progress_dialog.close()

            logging.info("[Install] Mod installation completed successfully.")
            QMessageBox.information(self, "Install Status", "Successfully installed modpack.")

            # Mark modpack as installed
            self.stop_blinking()
            self.setup_button_blinking()

        except Exception as e:
            progress_dialog.close()
            logging.error(f"[Install] An error occurred during installation: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred during installation: {e}")

        finally:
            # Ensure mods_path is updated and debug folders are removed
            mods_path = self.get_expanded_path("mods_directory")
            remove_debug_folders(mods_path)
            self.update_installed_info()

            # Ensure the installation popup is closed
            if popup:
                self.install_popup_open = False
                popup.close()
                self.popup_custom_mod_selection()

    def save_and_install(self, mod_vars, popup):
        self.save_preferences(mod_vars)
        self.excluded_mods = self.read_preferences()
        self.install_mods(popup)

    def uninstall_modpack(self):
        """Uninstall the modpack by deleting the Mods folder."""
        logging.info("[Uninstall] Starting modpack uninstallation.")

        self.settings = self.load_settings()
        install_path = self.get_expanded_path("mods_directory")

        # Confirm the uninstallation
        response = QMessageBox.question(
            self, "Confirm Uninstallation",
            "Are you sure you want to uninstall the modpack? This will wipe your Mods folder and its contents. Cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if response != QMessageBox.StandardButton.Yes:
            logging.info("[Uninstall] Uninstallation canceled by user.")
            return

        try:
            if install_path.exists():
                shutil.rmtree(install_path, onerror=readonly_handler)
                logging.info("[Uninstall] Modpack uninstalled successfully.")
                QMessageBox.information(self, "Uninstall Status", "Modpack uninstalled successfully.")
                self.update_installed_info()
            else:
                logging.warning("[Uninstall] No modpack found to uninstall.")
                QMessageBox.warning(self, "Uninstall Status", "No modpack found to uninstall.")

        except Exception as e:
            logging.error(f"[Uninstall] Error during uninstallation: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred during uninstallation: {str(e)}")

############################################################
# Bottom functions (Check versions, lovely, browser links)
############################################################

    def is_empty_or_git_only(self, folder_path):
        """Check if a folder is empty or contains only a .git directory."""
        try:
            folder = Path(folder_path)
            items = [item for item in os.listdir(folder_path) if not item.startswith('.')]
            is_empty = len(items) == 0 or (len(items) == 1 and items[0] == '.git')

            if is_empty:
                logging.warning(f"[Verification] Folder '{folder}' is empty or contains only .git.")
            return is_empty
        
        except Exception as e:
            logging.error(f"[Verification] Error processing {folder_path}: {e}", exc_info=True)
            return False

    def verify_modpack_integrity(self, max_display_mods=10):
        """Verify the integrity of the selected modpack."""
        logging.info("[Verification] Starting modpack integrity check.")

        self.settings = self.load_settings()
        modpack_name = self.modpack_var.currentText()
        selected_branch = self.branch_var.currentText()

        # Handle repository name and path
        repo_name = f"{modpack_name}-{selected_branch}" if selected_branch != "main" else modpack_name

        # Ensure the folder is inside the 'Modpacks' directory
        
        modpack_directory = self.get_expanded_path("modpack_directory")
        modpack_folder = modpack_directory / repo_name
        mods_folder = modpack_folder / "Mods"

        if not mods_folder.exists():
            logging.warning(f"[Verification] Mods folder not found: {mods_folder}")
            QMessageBox.warning(self, "Mods Folder Not Found", f"The 'Mods' folder for {modpack_name} was not found in '{mods_folder}'.")
            return

        # Get the top-level mod folders inside 'Mods'
        mod_folders = [folder for folder in mods_folder.iterdir() if folder.is_dir()]

        # Identify empty or .git-only mod folders (top-level only)
        empty_or_git_only = [folder.name for folder in mod_folders if self.is_empty_or_git_only(folder)]

        # Display verification results
        if empty_or_git_only:
            total_mods = len(empty_or_git_only)
            if total_mods > max_display_mods:
                displayed_mods = empty_or_git_only[:max_display_mods]
                additional_count = total_mods - max_display_mods
                folder_list = "\n".join(displayed_mods) + f"\n...and {additional_count} more mods."
            else:
                folder_list = "\n".join(empty_or_git_only)

            logging.warning(f"[Verification] The following mods are incomplete:\n{folder_list}")
            QMessageBox.information(
                self, "Verification Result",
                f"The following mods are not downloaded correctly. Please attempt reclone:\n\n{folder_list}"
            )
        else:
            logging.info("[Verification] All mods are properly populated.")
            QMessageBox.information(self, "Verification Complete", f"All folders in the 'Mods' folder for {modpack_name} are properly populated.")

    def check_versions(self):
        """Check latest modpack versions from GitHub repositories."""
        logging.info("[Version Check] Fetching modpack versions.")
        
        try:
            # Fetch commit messages for repositories
            commit_messages = self.fetch_commit_messages()

            # HTML Formatting - Fixing spacing issues
            version_info = """
            <style>
                ul { padding-left: 15px; }
                li { margin-bottom: 6px; } /* Slightly space out modpacks */
                .modpack-name { font-weight: bold; display: block; margin-bottom: 2px; } /* Force new line */
                .modpack-version { margin-left: 20px; display: block; } /* Indent sub-versions */
            </style>
            <h3><b>Modpack Versions:</b></h3><ul>
            """

            for repo_name, commit_message in commit_messages.items():
                commit_message_html = commit_message.replace("\n", "<br><span class='modpack-version'>") + "</span>"
                version_info += f"<li><span class='modpack-name'>{repo_name}:</span>{commit_message_html}</li>"

            # Display the version and update information
            logging.info("[Version Check] Successfully fetched modpack versions.")
            msg_box = QMessageBox(self)  # Attach to main window
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Version Information")
            msg_box.setTextFormat(Qt.TextFormat.RichText)  # ✅ Correct usage on instance
            msg_box.setText(version_info)
            msg_box.exec()
            
        except Exception as e:
            # Handle errors and display them in a critical message box
            logging.error(f"[Version Check] Error fetching modpack versions: {e}", exc_info=True)
            error_msg = f"An error occurred while checking versions:\n{str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

    def extract_pack_name(self, lua_file_path):
        """Helper to extract the pack name from ModpackUtil.lua."""
        lua_path = Path(lua_file_path)

        if not lua_path.exists():
            logging.warning(f"[File] Missing file: {lua_path}. Returning None.")
            return None
        
        try:
            for line in lua_path.read_text().splitlines():
                if line.startswith('--- VERSION:'):
                    pack_name = line.split(':', 1)[1].strip()
                    logging.info(f"[File] Extracted pack name: {pack_name}")
                    return pack_name
        except IOError as e:
            logging.error(f"[File] IOError reading {lua_file_path}: {e}", exc_info=True)
        return None

    def install_lovely_injector(self):
        """Install Lovely Injector with optional LuaJIT2 support."""
        logging.info("[Lovely Injector] Starting installation process.")

        self.settings = self.load_settings()

        # Resolve the game directory path
        game_dir = self.get_expanded_path("game_directory")
        system_arch = platform.machine()

        if system_platform == "Darwin":  # macOS
            game_exe = "Balatro.app"
        elif system_platform == "Windows":
            game_exe = "balatro.exe"
        else:  # Linux
            game_exe = "Balatro.exe"

        game_path = game_dir / game_exe
        if not game_path.exists():
            logging.warning("[Lovely Injector] Game executable not found. Installation aborted.")
            QMessageBox.warning(self, "Warning", "Game executable not found in the default directory. Please specify it in settings.")
            return

        use_luajit2 = self.settings.get("use_luajit2", False)
        logging.info(f"[Lovely Injector] Installing {'LuaJIT2' if use_luajit2 else 'Standard'} version.")

        msg = (
            "This installation requires disabling antivirus software temporarily and whitelisting the Balatro game directory.\nDo you want to proceed?"
        )
        if use_luajit2:
            msg = "LuaJIT2 (Experimental) will be installed along with Lovely Injector.\n\n" + msg

        if QMessageBox.question(self, "Install Lovely Injector", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
            logging.info("[Lovely Injector] Installation canceled by user.")
            
            # Revert the toggle in settings
            self.settings["use_luajit2"] = False
            self.save_settings()
            self.load_settings()

            # Revert the toggle in UI if applicable
            if hasattr(self, "luajit_checkbox"):
                self.luajit_checkbox.setChecked(False)

            return

        def install_luajit2():
            """Installs Lovely Injector with LuaJIT2 runtime (Experimental)."""
            logging.info("[Lovely Injector] Installing LuaJIT2.")

            """Prevent users from enabling LuaJIT2 on unsupported OS."""
            if system_platform != "Windows":
                logging.error("[Lovely Injector] LuaJIT2 is only supported on Windows.")
                QMessageBox.critical(None, "Error", "LuaJIT2 is only supported on Windows.")
                return

            lua_jit_url = "https://raw.githubusercontent.com/Dimserene/Balatro-ModpackManager/main/luajit2/lua51.dll"
            lovely_url = "https://raw.githubusercontent.com/Dimserene/Balatro-ModpackManager/main/luajit2/version.dll"

            lua_jit_path = game_dir / "lua51.dll"
            lovely_path = game_dir / "version.dll"
            
            # Backup existing LuaJIT
            original_lua_path = game_dir / "lua51.dll.old"
            if lua_jit_path.exists():
                shutil.move(lua_jit_path, original_lua_path)

            try:
                lua_jit_path.write_bytes(requests.get(lua_jit_url, stream=True).content)
                lovely_path.write_bytes(requests.get(lovely_url, stream=True).content)

                logging.info("[Lovely Injector] LuaJIT2 installed successfully.")
                QMessageBox.information(None, "Installation Complete", "Lovely Injector with LuaJIT2 installed successfully!")

            except requests.RequestException as e:
                logging.error(f"[Lovely Injector] Failed to download files: {e}", exc_info=True)
                QMessageBox.critical(None, "Error", f"Failed to download files: {e}")

        def install_standard_lovely():
            """Install the standard Lovely Injector (without LuaJIT2)."""
            logging.info("[Lovely Injector] Installing standard version.")
            
            # Use recommended URL if available
            release_url = recommanded_lovely
            archive_name = "lovely-injector"
            extracted_files = []

            if system_platform == "Darwin":  # macOS
                if system_arch  == "arm64":
                    url = f"{release_url}lovely-aarch64-apple-darwin.tar.gz"
                elif system_arch  == "x86_64":
                    url = f"{release_url}lovely-x86_64-apple-darwin.tar.gz"
                else:
                    QMessageBox.critical(None, "Error", "Unsupported macOS architecture.")
                    return
                archive_name += ".tar.gz"
                extracted_files = ["liblovely.dylib", "run_lovely.sh"]
                
            elif system_platform in ["Windows", "Linux"]:
                url = f"{release_url}lovely-x86_64-pc-windows-msvc.zip"
                archive_name = "lovely-injector.zip"
                extracted_files = ["version.dll"]

            archive_path = game_dir / archive_name

            # Download and extract the archive
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                archive_path.write_bytes(response.content)

                if archive_name.endswith(".zip"):
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(game_dir)
                elif archive_name.endswith(".tar.gz"):
                    with tarfile.open(archive_path, "r:gz") as tar:
                        tar.extractall(game_dir)

                # Verify extracted files
                missing_files = [f for f in extracted_files if not (game_dir / f).exists()]
                if missing_files:
                    raise FileNotFoundError(f"Missing files after extraction: {', '.join(missing_files)}")

                archive_path.unlink()  # Clean up the archive
                logging.info("[Lovely Injector] Standard version installed successfully.")
                QMessageBox.information(None, "Install Status", "Lovely Injector installed successfully.")

            except (requests.RequestException, zipfile.BadZipFile, tarfile.TarError, FileNotFoundError) as e:
                logging.error(f"[Lovely Injector] Installation failed: {e}", exc_info=True)
                QMessageBox.critical(None, "Error", f"Failed to install Lovely Injector: {e}")

        if use_luajit2:
            if not (game_dir / "lua51.dll.old").exists():
                install_luajit2()
            else:
                self.uninstall_luajit2()
                install_luajit2()
            
        else:
            if (game_dir / "lua51.dll.old").exists():
                self.uninstall_luajit2()
                install_standard_lovely()
            else:
                install_standard_lovely()

        # Stop any existing blinking safely
        if hasattr(self, "blink_timer") and self.blink_timer and self.blink_timer.isActive():
            self.blink_timer.stop()

        # Reset button styles
        buttons = [self.download_button, self.install_button, self.install_lovely_button]

        for button in buttons:
            if hasattr(self, button.objectName()):  # Ensure it's a valid string
                getattr(self, button.objectName()).setStyleSheet("""
                    QPushButton {
                        font: 12pt 'Helvetica';
                        background-color: none;
                    }
                    QPushButton:hover {
                        background-color: #dadada;
                    }
                    QPushButton:pressed {
                        background-color: #bcbcbc;
                    }
                """)

    def uninstall_luajit2(self):
        """Uninstall LuaJIT2 and restore Balatro's default Lua runtime."""
        logging.info("[Lovely Injector] Uninstalling LuaJIT2.")
        
        game_dir = self.get_expanded_path("game_directory")
        lua_jit_path = game_dir / "lua51.dll"
        original_lua_path = game_dir / "lua51.dll.old"

        if QMessageBox.question(
            None, "Uninstall LuaJIT2",
            "LuaJIT2 will be removed, and Balatro's original Lua runtime will be restored.\n\nDo you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.No:
            logging.info("[Lovely Injector] Uninstallation canceled by user.")
            return

        try:
            if lua_jit_path.exists():
                lua_jit_path.unlink()

            # Restore the original Lua runtime
            if original_lua_path.exists():
                shutil.move(original_lua_path, lua_jit_path)

            logging.info("[Lovely Injector] LuaJIT2 removed and original Lua restored.")
            QMessageBox.information(None, "Uninstall Complete", "LuaJIT2 removed. Balatro's original LuaJIT restored.")

        except Exception as e:
            logging.error(f"[Lovely Injector] Failed to uninstall LuaJIT2: {e}", exc_info=True)
            QMessageBox.critical(None, "Error", f"Failed to uninstall LuaJIT2: {e}")

    def check_lovely_injector_installed(self):
        """Check if Lovely Injector is installed and prompt the user to install if not."""

        # Expand and normalize the game directory path
        game_dir = self.get_expanded_path("game_directory")

        # Define the expected injector path based on OS
        if system_platform == "Darwin":  # macOS
            lovely_path = game_dir / "liblovely.dylib"
        else:  # Windows & Linux
            lovely_path = game_dir / "version.dll"

        if not lovely_path.exists():
            logging.warning("[Lovely Injector] Not installed. Prompting user to install.")
            if QMessageBox.question(None, "Lovely Injector Not Found", "Lovely Injector is not installed. Install now?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.install_lovely_injector()
                return lovely_path.exists()

        logging.info("[Lovely Injector] Found installed version of lovely injector.")
        return True  # Lovely Injector is installed

    def open_discord(self):
        # Check if the user has already joined the official Discord
        webbrowser.open("https://discord.gg/vUcg8UY8rZ")

############################################################
# Misc functions
############################################################

def readonly_handler(func, path, _):
    """Remove read-only attribute and retry the operation, ensuring Git processes are terminated first."""
    path = Path(path)  # Ensure it's a Path object

    try:
        # Ensure the file is writable
        path.chmod(stat.S_IWRITE)  # ✅ Correct usage

        # Retry the operation
        func(str(path))
        logging.debug(f"[File] Removed read-only attribute: {path}")

    except PermissionError:
        logging.warning(f"[File] Permission denied: {path}. Attempting to terminate Git processes.")
        terminate_git_processes()
        
        try:
            # Retry after terminating Git processes
            path.chmod(stat.S_IWRITE)
            func(str(path))
            logging.info(f"[Retry] Successfully retried operation for: {path}")
        except Exception as e:
            logging.error(f"[Retry] Operation failed again: {path}, Error: {e}", exc_info=True)

def terminate_git_processes():
    """Force shut down all running Git processes."""
    try:
        if system_platform == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "git.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # macOS/Linux
            subprocess.run(["pkill", "-f", "git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        logging.info("[Git] Forcefully terminated all running Git processes.")
    except Exception as e:
        logging.error(f"[Git] Failed to terminate Git processes: {e}", exc_info=True)

def retry_operation(func, path):
    """Retry the failed operation after terminating Git processes."""
    try:
        logging.info("[Retry] Retrying the operation after terminating Git processes.")
        path.chmod(stat.S_IWRITE)  # Ensure the file is writable again
        func(str(path))  # Retry the operation
        logging.debug(f"[Retry] Successfully retried operation for: {path}")
    except Exception as e:
        logging.error(f"[Retry] Operation failed again: {path}, Error: {e}", exc_info=True)

def center_window(window, width, height):
    """Center the given window on the screen."""
    try:
        screen_geometry = window.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.setGeometry(int(x), int(y), width, height)
        logging.debug(f"[UI] Window centered at ({x}, {y}) with size ({width}x{height}).")

    except Exception as e:
        logging.error(f"[UI] Error centering window: {e}", exc_info=True)

if __name__ == "__main__":

    logging.info("==== Modpack Manager Started ====")
    logging.info(f"Logging to file: {log_filename}")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        app = QApplication([])  # Initialize the QApplication

        root = ModpackManagerApp()  # No need to pass 'root', since the window is handled by PyQt itself

        # Center the window
        screen_geometry = app.primaryScreen().availableGeometry()
        window_width = root.sizeHint().width()
        window_height = root.sizeHint().height()

        # Calculate position for the window to be centered
        position_x = (screen_geometry.width() - window_width) // 2
        position_y = (screen_geometry.height() - window_height) // 2

        # Set the window size and position
        root.setGeometry(position_x, position_y, window_width, window_height)
        logging.debug(f"[Startup] Window initialized at ({position_x}, {position_y}) with size ({window_width}x{window_height}).")

        root.show()  # Show the main window
        logging.info("[Startup] Application started successfully.")

        app.exec()   # Execute the application's event loop

    except Exception as e:
        logging.critical(f"[Startup] Application encountered a critical error: {e}", exc_info=True)