import os
import shutil
import time
import threading
import hashlib
from tkinter import Tk, Button, Label, Text, Scrollbar, filedialog, END, Toplevel
import tkinter.messagebox as messagebox 

# Source and destination directories
SOURCE_DIR = os.path.join(os.getenv("USERPROFILE"), "AppData", "LocalLow", "semiwork", "Repo", "saves")
LOG_FILE = "backup_log.txt"

# Global variable to control the monitoring loop
monitoring = False
monitoring_thread = None
DEST_DIR = None

def log_event(message):
    """Log events to a file and print to console."""
    if DEST_DIR:  # Ensure the destination directory is set before logging
        log_path = os.path.join(DEST_DIR, LOG_FILE)  # Create log file in DEST_DIR
        with open(log_path, "a") as log:
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

def is_folder_empty(folder_path):
    """Check if a folder is empty."""
    return not any(os.scandir(folder_path))

def calculate_file_hash(file_path):
    """Calculate the SHA256 hash of a file."""
    log_event(f"Calculating hash for file: {file_path}")
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        log_event(f"Hash calculated for file: {file_path}")
    except Exception as e:
        log_event(f"Error calculating hash for file: {file_path}. Exception: {e}")
    return hash_sha256.hexdigest()

def backup_folder(folder_name):
    """Backup a folder to the destination directory, overwriting by default and copying missing files."""
    log_event(f"--- backup_folder CALLED for: {folder_name} ---")
    src_path = os.path.join(SOURCE_DIR, folder_name)
    dest_path = os.path.join(DEST_DIR, folder_name)

    log_event(f"Starting backup for folder: {folder_name}")
    log_event(f"Source path: {src_path}")
    log_event(f"Destination path: {dest_path}")

    # Ensure the destination folder exists
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        log_event(f"Created destination folder: {dest_path}")

    # Copy all files from the source to the destination, overwriting if necessary
    for root, _, files in os.walk(src_path):
        log_event(f"Processing directory: {root}")
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, src_path)
            dest_file = os.path.join(dest_path, relative_path)

            log_event(f"Processing file: {relative_path}")
            dest_folder = os.path.dirname(dest_file)
            os.makedirs(dest_folder, exist_ok=True)  # Ensure the destination folder exists

            # Copy if missing or if source is newer
            try:
                shutil.copy2(src_file, dest_file)
                log_event(f"Copied file: {relative_path} to destination.")
            except Exception as e:
                log_event(f"Error copying file: {relative_path}. Exception: {e}")
                
            else:
                log_event(f"File up to date: {relative_path}")

def get_latest_mtime(folder_path):
    """Return the latest modification time of any file in the folder (recursively)."""
    latest = os.path.getmtime(folder_path)
    for root, _, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(fp)
                if mtime > latest:
                    latest = mtime
            except Exception:
                pass
    return latest
                
def monitor_directory():
    """Monitor the source directory for changes."""
    global monitoring

    log_event("Monitoring started.")
    if not DEST_DIR:  # Ensure DEST_DIR is set before monitoring
        log_event("Error: No destination directory selected. Monitoring stopped.")
        monitoring = False
        return

    last_modified = {}  # Track last modified times
    last_file_set = {}  # Track file sets

    while monitoring:
        log_event("Checking source directory for changes...")
        for folder_name in os.listdir(SOURCE_DIR):
            folder_path = os.path.join(SOURCE_DIR, folder_name)

            if os.path.isdir(folder_path):
                # Get set of files in source
                src_files = set()
                for root, _, files in os.walk(folder_path):
                    for f in files:
                        src_files.add(os.path.relpath(os.path.join(root, f), folder_path))

                # Get set of files in destination
                dest_folder_path = os.path.join(DEST_DIR, folder_name)
                dest_files = set()
                if os.path.exists(dest_folder_path):
                    for root, _, files in os.walk(dest_folder_path):
                        for f in files:
                            dest_files.add(os.path.relpath(os.path.join(root, f), dest_folder_path))

                if src_files != dest_files:
                    log_event(f"Folder {folder_name} has different files in source and destination. Starting backup.")
                    backup_folder(folder_name)
                elif not is_folder_empty(folder_path):
                    log_event(f"Folder {folder_name} already backed up: files match.")
                else:
                    log_event(f"Folder {folder_name} is empty. Skipping.")
            else:
                log_event(f"Skipping non-folder item: {folder_name}")

        # Sleep loop
        for _ in range(30):
            if not monitoring:
                log_event("Monitoring stopped.")
                return
            time.sleep(1)

def start_monitoring_with_directory(status_label):
    """Start monitoring and prompt the user to select a destination directory."""
    global DEST_DIR
    # Ask the user to select a destination directory
    selected_dir = filedialog.askdirectory(title="Select Backup Destination Directory")
    if selected_dir:  # If the user selects a directory
        DEST_DIR = selected_dir
        log_event(f"Selected backup destination: {DEST_DIR}")
        start_monitoring()
        update_status_label(status_label)
    else:
        log_event("No directory selected. Monitoring not started.")

def start_monitoring():
    """Start the monitoring process."""
    global monitoring, monitoring_thread
    if not monitoring:
        monitoring = True
        log_event("Started monitoring.")
        # Start the monitoring process in a separate thread
        monitoring_thread = threading.Thread(target=monitor_directory, daemon=True)
        monitoring_thread.start()

def stop_monitoring():
    """Stop the monitoring process."""
    global monitoring, monitoring_thread
    if monitoring:
        monitoring = False
        log_event("Stopped monitoring.")
        # Wait for the thread to finish if it exists
        if monitoring_thread and monitoring_thread.is_alive():
            monitoring_thread.join(timeout=1) 

def show_logs():
    """Display the log file in a new window."""
    if not DEST_DIR:
        messagebox.showerror(
            "Error",
            "No destination directory selected. Please start monitoring first to select a directory."
        )
        return

    log_path = os.path.join(DEST_DIR, LOG_FILE)
    log_window = Toplevel()
    log_window.title("Backup Logs")

    scrollbar = Scrollbar(log_window)
    scrollbar.pack(side="right", fill="y")

    text = Text(log_window, wrap="word", yscrollcommand=scrollbar.set)
    text.pack(expand=True, fill="both")

    scrollbar.config(command=text.yview)

    if os.path.exists(log_path):
        with open(log_path, "r") as log:
            text.insert(END, log.read())
    else:
        text.insert(END, "No logs available.")

def update_status_label(status_label):
    """Update the status label based on the monitoring state."""
    if monitoring:
        status_label.config(text="REPO Monitor is running", fg="green")
    else:
        status_label.config(text="REPO Monitor is not running", fg="red")

def restore_backup():
    """Restore the backup from the destination directory to the source directory."""
    if not DEST_DIR:
        messagebox.showerror("Error", "No destination directory selected. Cannot restore backup.")
        return

    if not os.path.exists(DEST_DIR):
        messagebox.showerror("Error", "The destination directory does not exist.")
        return

    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)  # Create the source directory if it doesn't exist

    # Check if the source directory is empty
    source_is_empty = not any(os.scandir(SOURCE_DIR))

    for folder_name in os.listdir(DEST_DIR):
        # Skip the log file during restoration
        if folder_name == LOG_FILE:
            log_event(f"Skipped restoring log file: {LOG_FILE}")
            continue

        src_path = os.path.join(SOURCE_DIR, folder_name)
        dest_path = os.path.join(DEST_DIR, folder_name)

        if os.path.isdir(dest_path):
            if os.path.exists(src_path) and not source_is_empty:
                # Compare modified dates
                source_modified = os.path.getmtime(src_path)
                dest_modified = os.path.getmtime(dest_path)

                if dest_modified < source_modified:
                    # Warn the user if the destination files are older
                    response = messagebox.askyesno(
                        "Warning",
                        f"The backup folder '{folder_name}' is older than the source folder. "
                        "Do you want to overwrite the source folder with the backup?"
                    )
                    if not response:
                        continue  # Skip restoring this folder

            # Copy the folder from the destination to the source
            try:
                if os.path.exists(src_path):
                    shutil.rmtree(src_path)  # Remove the existing source folder
                shutil.copytree(dest_path, src_path)
                log_event(f"Restored folder: {folder_name}")
            except PermissionError:
                messagebox.showerror(
                    "Permission Denied",
                    f"Access denied while trying to modify '{src_path}'.\n"
                    "Please relaunch the program as an administrator and try again."
                )
                return  # Exit the function if a permission error occurs
        else:
            log_event(f"Skipped non-folder item in backup: {folder_name}")

    messagebox.showinfo("Restore Complete", "The backup has been successfully restored.")

def create_gui():
    """Create the GUI for the program."""
    root = Tk()
    root.title("Backup Program")

    Label(root, text="R.E.P.O Backup Program", font=("Arial", 16)).pack(pady=10)

    # Status label to show monitoring state
    status_label = Label(root, text="REPO Monitor is not running", font=("Arial", 12), fg="red")
    status_label.pack(pady=5)

    # Update the status label when monitoring starts or stops
    def stop_monitoring_with_status():
        stop_monitoring()
        update_status_label(status_label)

    # Use start_monitoring_with_directory to prompt for a directory
    Button(root, text="Start Monitoring", command=lambda: start_monitoring_with_directory(status_label), width=20).pack(pady=5)
    Button(root, text="Stop Monitoring", command=stop_monitoring_with_status, width=20).pack(pady=5)
    Button(root, text="Restore Backup", command=restore_backup, width=20).pack(pady=5)  # Add Restore button
    Button(root, text="View Logs", command=show_logs, width=20).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
