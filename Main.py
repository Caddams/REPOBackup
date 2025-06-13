import os
import shutil
import time
import threading
import hashlib
from tkinter import Tk, Button, Label, Text, Scrollbar, filedialog, END, Toplevel, StringVar, ttk
import tkinter.messagebox as messagebox

# Source and destination directories
SOURCE_DIR = os.path.join(os.getenv("USERPROFILE"), "AppData", "LocalLow", "semiwork", "Repo", "saves")
LOG_FILE = "backup_log.txt"
log_window = None


# Global variable to control the monitoring loop
monitoring = False
monitoring_thread = None
DEST_DIR = None

# Localization dictionary
LOCALIZATION = {
    "en": {
        "language": "English",
        "title": "Backup Program",
        "main_label": "R.E.P.O Backup Program",
        "start_monitoring": "Start Monitoring",
        "stop_monitoring": "Stop Monitoring",
        "restore_backup": "Restore Backup",
        "view_logs": "View Logs",
        "monitor_running": "REPO Monitor is running",
        "monitor_not_running": "REPO Monitor is not running",
        "restore_complete": "The backup has been successfully restored.",
        "error_no_dest": "No destination directory selected. Please start monitoring first to select a directory.",
        "display_language": "Languages",
        "log_file_not_found": "Log file not found.",
        "error": "Error",
        "error_dest_not_exist": "Destination directory does not exist.",
        "warning": "Warning",
        "backup_older_overwrite_confirm": "The backup folder '{folder_name}' is older than the source folder. Do you want to overwrite the source folder with the backup?",
        "permission_denied": "Permission Denied",
        "access_denied": "Access denied to {src_path}. Please relaunch the program as an administrator and try again.",
        "restore_complete": "The backup has been successfully restored."
        # ...add more keys as needed...
    },
    "ua": {
        "language": "українська",
        "title": "Програма резервного копіювання",
        "main_label": "Програма резервного копіювання R.E.P.O",
        "start_monitoring": "Почати моніторинг",
        "stop_monitoring": "Зупинити моніторинг",
        "restore_backup": "Відновити резервну копію",
        "view_logs": "Переглянути журнали",
        "monitor_running": "Монітор REPO працює",
        "monitor_not_running": "Монітор REPO не працює",
        "restore_complete": "Резервну копію успішно відновлено.",
        "error_no_dest": "Не вибрано каталог призначення. Спочатку запустіть моніторинг, щоб вибрати каталог.",
        "display_language": "Мови",
        "log_file_not_found": "Файл журналу не знайдено.",
        "error": "Помилка",
        "error_dest_not_exist": "Каталог призначення не існує.",
        "warning": "Попередження",
        "backup_older_overwrite_confirm": "Резервна копія '{folder_name}' старіша за вихідну папку. Ви хочете перезаписати вихідну папку резервною копією?",
        "permission_denied": "Доступ заборонено",
        "access_denied": "Доступ заборонено до {src_path}. Будь ласка, перезапустіть програму з правами адміністратора та спробуйте ще раз.",
        "restore_complete": "Резервну копію успішно відновлено."
        # ...add more keys as needed...
    },
    "es": {
        "language": "Español",
        "title": "Programa de Copias de Seguridad",
        "main_label": "Programa de Copias de Seguridad R.E.P.O",
        "start_monitoring": "Iniciar Monitoreo",
        "stop_monitoring": "Detener Monitoreo",
        "restore_backup": "Restaurar Copia",
        "view_logs": "Ver Registros",
        "monitor_running": "El monitor REPO está en ejecución",
        "monitor_not_running": "El monitor REPO no está en ejecución",
        "restore_complete": "La copia de seguridad se ha restaurado correctamente.",
        "error_no_dest": "No se ha seleccionado un directorio de destino. Inicie el monitoreo primero para seleccionar un directorio.",
        "display_language": "Idiomas",
        "log_file_not_found": "Archivo de registro no encontrado.",
        "error": "Error",
        "error_dest_not_exist": "El directorio de destino no existe.",
        "warning": "Advertencia",
        "backup_older_overwrite_confirm": "La carpeta de respaldo '{folder_name}' es más antigua que la carpeta de origen. ¿Desea sobrescribir la carpeta de origen con la copia de seguridad?",
        "permission_denied": "Permiso Denegado",
        "access_denied": "Acceso denegado a {src_path}. Por favor, reinicie el programa como administrador e inténtelo de nuevo.",
        "restore_complete": "La copia de seguridad se ha restaurado correctamente."
        # ...add more keys as needed...
    },
        "de": {
        "language": "Deutsch",
        "title": "Backup-Programm",
        "main_label": "Backup-Programm R.E.P.O",
        "start_monitoring": "Überwachung starten",
        "stop_monitoring": "Überwachung stoppen",
        "restore_backup": "Backup wiederherstellen",
        "view_logs": "Protokolle anzeigen",
        "monitor_running": "REPO-Überwachung läuft",
        "monitor_not_running": "REPO-Überwachung läuft nicht",
        "restore_complete": "Das Backup wurde erfolgreich wiederhergestellt.",
        "error_no_dest": "Kein Zielverzeichnis ausgewählt. Bitte starten Sie zuerst die Überwachung, um ein Verzeichnis auszuwählen.",
        "display_language": "Sprachen",
        "log_file_not_found": "Protokolldatei nicht gefunden.",
        "error": "Fehler",
        "error_dest_not_exist": "Das Zielverzeichnis existiert nicht.",
        "warning": "Warnung",
        "backup_older_overwrite_confirm": "Das Backup-Ordner '{folder_name}' ist älter als der Quellordner. Möchten Sie den Quellordner mit dem Backup überschreiben?",
        "permission_denied": "Zugriff verweigert",
        "access_denied": "Zugriff verweigert auf {src_path}. Bitte starten Sie das Programm als Administrator neu und versuchen Sie es erneut.",
        "restore_complete": "Das Backup wurde erfolgreich wiederhergestellt."
        # ...add more keys as needed...
    },
    "fr": {
        "language":"Francese",
        "title": "Programme de Sauvegarde",
        "main_label": "Programme de Sauvegarde R.E.P.O",
        "start_monitoring": "Démarrer la Surveillance",
        "stop_monitoring": "Arrêter la Surveillance",
        "restore_backup": "Restaurer la Sauvegarde",
        "view_logs": "Voir les Journaux",
        "monitor_running": "Le moniteur REPO est en cours d'exécution",
        "monitor_not_running": "Le moniteur REPO n'est pas en cours d'exécution",
        "restore_complete": "La sauvegarde a été restaurée avec succès.",
        "error_no_dest": "Aucun dossier de destination sélectionné. Veuillez d'abord démarrer la surveillance pour sélectionner un dossier.",
        "display_language": "Langues",
        "log_file_not_found": "Fichier journal non trouvé.",
        "error": "Erreur",
        "error_dest_not_exist": "Le répertoire de destination n'existe pas.",
        "warning": "Avertissement",
        "backup_older_overwrite_confirm": "Le dossier de sauvegarde '{folder_name}' est plus ancien que le dossier source. Voulez-vous écraser le dossier source avec la sauvegarde?",
        "permission_denied": "Permission refusée",
        "access_denied": "Accès refusé à {src_path}. Veuillez relancer le programme en tant qu'administrateur et réessayer.",
        "restore_complete": "La sauvegarde a été restaurée avec succès."
        # ...add more keys as needed...
    },
        "it": {
        "language":"Italiano",
        "title": "Programma di Copie di Sicurezza",
        "main_label": "Programma di Copie di Sicurezza R.E.P.O",
        "start_monitoring": "Inizia Monitoraggio",
        "stop_monitoring": "Ferma Monitoraggio",
        "restore_backup": "Ripristina Copia",
        "view_logs": "Visualizza Registri",
        "monitor_running": "Il monitor REPO è in esecuzione",
        "monitor_not_running": "Il monitor REPO non è in esecuzione",
        "restore_complete": "La copia di sicurezza è stata ripristinata correttamente.",
        "error_no_dest": "Nessuna cartella di destinazione selezionata. Inizia il monitoraggio prima di selezionare una cartella.",
        "display_language": "Lingue",
        "log_file_not_found": "File di registro non trovato.",
        "error": "Errore",
        "error_dest_not_exist": "La cartella di destinazione non esiste.",
        "warning": "Avvertenza",
        "backup_older_overwrite_confirm": "La cartella di backup '{folder_name}' è più vecchia della cartella di origine. Vuoi sovrascrivere la cartella di origine con il backup?",
        "permission_denied": "Accesso negato",
        "access_denied": "Accesso negato a {src_path}. Si prega di riavviare il programma come amministratore e riprovare.",
        "restore_complete": "La copia di sicurezza è stata ripristinata correttamente."
        # ...add more keys as needed...
    },
        "zh": {
        "language": "官话",
        "title": "备份程序",
        "main_label": "备份程序 R.E.P.O",
        "start_monitoring": "开始监控",
        "stop_monitoring": "停止监控",
        "restore_backup": "恢复备份",
        "view_logs": "查看日志",
        "monitor_running": "REPO 监控正在运行",
        "monitor_not_running": "REPO 监控未运行",
        "restore_complete": "备份已成功恢复。",
        "error_no_dest": "未选择目标目录。请先启动监控以选择目录。",
        "display_language": "语言",
        "log_file_not_found": "未找到日志文件。",
        "error": "错误",
        "error_dest_not_exist": "目标目录不存在。",
        "warning": "警告",
        "backup_older_overwrite_confirm": "备份文件夹 '{folder_name}' 比源文件夹旧。您想用备份覆盖源文件夹吗？",
        "permission_denied": "访问被拒绝",
        "access_denied": "访问被拒绝到 {src_path}。请重新以管理员身份启动程序并重试。",
        "restore_complete": "备份已成功恢复。"
        # ...add more keys as needed...
    }
}

# Set the current language
CURRENT_LANG = "en"

def select_language(refresh_callback=None):
    """Prompt the user to select a language from a dropdown at startup."""
    global CURRENT_LANG

    root = Tk()
    root.withdraw()

    lang_win = Toplevel()
    lang_win.title("Select Language")
    lang_win.geometry("300x120")
    lang_win.resizable(False, False)

    Label(lang_win, text="Select your language:", font=("Arial", 12)).pack(pady=10)

    languages = list(LOCALIZATION.keys())
    lang_display = [f"{code} - {LOCALIZATION[code]['language']}" for code in languages]

    selected_lang = StringVar(value=lang_display[0])

    combo = ttk.Combobox(lang_win, values=lang_display, state="readonly", textvariable=selected_lang, width=28)
    combo.pack(pady=5)

    def confirm():
        global CURRENT_LANG
        idx = lang_display.index(combo.get())
        CURRENT_LANG = languages[idx]
        lang_win.destroy()
        root.destroy()
        if refresh_callback:
            refresh_callback()

    Button(lang_win, text="OK", command=confirm, width=10).pack(pady=10)

    lang_win.grab_set()
    lang_win.mainloop()

def t(key):
    """Translate a key using the current language."""
    return LOCALIZATION.get(CURRENT_LANG, LOCALIZATION["en"]).get(key, key)


def log_event(message):
    """Log events to a file and print to console. Keeps only the last 100 lines."""
    if DEST_DIR:  # Ensure the destination directory is set before logging
        log_path = os.path.join(DEST_DIR, LOG_FILE)
        # Write the new log entry
        with open(log_path, "a") as log:
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        # Trim the log file to the last 100 lines
        try:
            with open(log_path, "r") as log:
                lines = log.readlines()
            if len(lines) > 100:
                with open(log_path, "w") as log:
                    log.writelines(lines[-100:])
        except Exception as e:
            print(f"Error trimming log file: {e}")
    print(message)

def is_folder_empty(folder_path):
    """Check if a folder is empty."""
    return not any(os.scandir(folder_path))

def calculate_file_hash(file_path):
    """Calculate the SHA256 hash of a file."""
    # log_event(f"Calculating hash for file: {file_path}")
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        # log_event(f"Hash calculated for file: {file_path}")
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
    """Display the log file in a new window, with error handling for missing DEST_DIR."""
    global log_window

    if not DEST_DIR:
        messagebox.showerror(
            t("view_logs"),
            t("error_no_dest") if "error_no_dest" in LOCALIZATION[CURRENT_LANG] else "No destination directory selected. Please start monitoring first to select a directory."
        )
        return

    log_path = os.path.join(DEST_DIR, LOG_FILE)

    # Only one log window at a time
    if 'log_window' in globals() and log_window is not None and log_window.winfo_exists():
        for widget in log_window.winfo_children():
            widget.destroy()
        display_log_content(log_window, log_path)
        log_window.deiconify()
        log_window.lift()
        log_window.focus_force()
        return

    log_window = Toplevel()
    log_window.title(t("view_logs"))
    log_window.geometry("600x400")
    display_log_content(log_window, log_path)

def display_log_content(window, log_path):
    """Helper to display log content in the given window."""
    Label(window, text=t("view_logs"), font=("Arial", 14)).pack(pady=5)
    scrollbar = Scrollbar(window)
    scrollbar.pack(side="right", fill="y")
    text_area = Text(window, wrap="word", yscrollcommand=scrollbar.set)
    text_area.pack(expand=True, fill="both", padx=10, pady=10)
    scrollbar.config(command=text_area.yview)
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as log:
            text_area.insert(END, log.read())
        text_area.see(END)
    else:
        msg = t("log_file_not_found") if "log_file_not_found" in LOCALIZATION[CURRENT_LANG] else "No logs available."
        text_area.insert(END, msg)
    text_area.config(state="disabled")

def update_status_label(status_label):
    """Update the status label based on the monitoring state."""
    if monitoring:
        status_label.config(text=t("monitor_running"), fg="green")
    else:
        status_label.config(text=t("monitor_not_running"), fg="red")

def restore_backup():
    """Restore the backup from the destination directory to the source directory, without deleting anything in the source."""
    if not DEST_DIR:
        messagebox.showerror(t("error"), t("error_no_dest"))
        return

    if not os.path.exists(DEST_DIR):
        messagebox.showerror(t("error"), t("error_dest_not_exist"))
        return

    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)  # Create the source directory if it doesn't exist

    for folder_name in os.listdir(DEST_DIR):
        # Skip the log file during restoration
        if folder_name == LOG_FILE:
            log_event(f"Skipped restoring log file: {LOG_FILE}")
            continue

        src_path = os.path.join(SOURCE_DIR, folder_name)
        dest_path = os.path.join(DEST_DIR, folder_name)

        if os.path.isdir(dest_path):
            warn_user = False
            if os.path.exists(src_path):
                # Compare modified dates
                source_modified = os.path.getmtime(src_path)
                dest_modified = os.path.getmtime(dest_path)
                if dest_modified < source_modified:
                    warn_user = True

            if warn_user:
                response = messagebox.askyesno(
                    t("warning"),
                    t("backup_older_overwrite_confirm").format(folder_name=folder_name)
                )
                if not response:
                    continue  # Skip restoring this folder

            # Copy files/folders from backup to source, only overwrite or add, never delete
            try:
                for root, dirs, files in os.walk(dest_path):
                    rel_root = os.path.relpath(root, dest_path)
                    target_root = os.path.join(src_path, rel_root) if rel_root != "." else src_path
                    os.makedirs(target_root, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(target_root, file)
                        dest_file = os.path.join(root, file)
                        shutil.copy2(dest_file, src_file)
                log_event(f"Restored (merged/overwritten) folder: {folder_name}")
            except PermissionError as e:
                messagebox.showerror(
                    t("permission_denied"),
                    t("access_denied").format(src_path=src_path)
                )
                log_event(f"PermissionError while restoring '{src_path}': {e}")
                return  # Exit the function if a permission error occurs
        else:
            log_event(f"Skipped non-folder item in backup: {folder_name}")

    messagebox.showinfo(t("restore_complete"))

def create_gui():
    root = Tk()
    root.title(t("title"))

    # Store widgets for refreshing
    widgets = {}

    widgets['main_label'] = Label(root, text=t("main_label"), font=("Arial", 16))
    widgets['main_label'].pack(pady=10)

    widgets['status_label'] = Label(root, text=t("monitor_not_running"), font=("Arial", 12), fg="red")
    widgets['status_label'].pack(pady=5)

    def stop_monitoring_with_status():
        stop_monitoring()
        update_status_label(widgets['status_label'])

    widgets['start_btn'] = Button(
        root,
        text=t("start_monitoring"),
        command=lambda: start_monitoring_with_directory(widgets['status_label']),
        width=20
    )
    widgets['start_btn'].pack(pady=5)

    widgets['stop_btn'] = Button(
        root,
        text=t("stop_monitoring"),
        command=stop_monitoring_with_status,
        width=20
    )
    widgets['stop_btn'].pack(pady=5)

    widgets['restore_btn'] = Button(
        root,
        text=t("restore_backup"),
        command=restore_backup,
        width=20
    )
    widgets['restore_btn'].pack(pady=5)

    widgets['logs_btn'] = Button(
        root,
        text=t("view_logs"),
        command=show_logs,
        width=20
    )
    widgets['logs_btn'].pack(pady=5)

    def refresh_gui():
        root.title(t("title"))
        widgets['main_label'].config(text=t("main_label"))
        # Optionally update status label text based on monitoring state
        update_status_label(widgets['status_label'])
        widgets['start_btn'].config(text=t("start_monitoring"))
        widgets['stop_btn'].config(text=t("stop_monitoring"))
        widgets['restore_btn'].config(text=t("restore_backup"))
        widgets['logs_btn'].config(text=t("view_logs"))
        widgets['lang_btn'].config(text=t("display_language"))

    widgets['lang_btn'] = Button(
        root,
        text=t("display_language"),
        command=lambda: select_language(refresh_gui),
        width=20
    )
    widgets['lang_btn'].pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    select_language()
    create_gui()
