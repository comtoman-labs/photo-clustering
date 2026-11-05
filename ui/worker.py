from PySide6.QtCore import QThread, Signal

from core.organizer import (
    ScanResult,
    scan_folder,
    organize_photos,
)


class ScanWorker(QThread):
    progress = Signal(int, int, str)  # current, total, filename
    finished = Signal(object)         # ScanResult
    error = Signal(str)

    def __init__(
        self,
        base_folder: str,
        prefer_exif: bool = True,
        allow_mtime: bool = False,
        min_count: int = 10,
        folder_prefix: str = "",
        folder_suffix: str = "_",
        parent=None
    ):
        super().__init__(parent)
        self.base_folder = base_folder
        self.prefer_exif = prefer_exif
        self.allow_mtime = allow_mtime
        self.min_count = min_count
        self.folder_prefix = folder_prefix
        self.folder_suffix = folder_suffix
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            def on_progress(current, total, filename):
                if not self._is_cancelled:
                    self.progress.emit(current, total, filename)

            result = scan_folder(
                base_folder=self.base_folder,
                prefer_exif=self.prefer_exif,
                allow_mtime_fallback=self.allow_mtime,
                min_count=self.min_count,
                folder_prefix=self.folder_prefix,
                folder_suffix=self.folder_suffix,
                progress_callback=on_progress
            )
            if not self._is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class OrganizeWorker(QThread):
    progress = Signal(int, int, str)  # current, total, filename
    log = Signal(str)                 # log text
    finished = Signal(dict)           # stats dict
    error = Signal(str)

    def __init__(
        self,
        base_folder: str,
        scan_result: ScanResult,
        mode: str = "move",
        min_count: int = 10,
        folder_prefix: str = "",
        folder_suffix: str = "_",
        organize_small_files: bool = False,
        small_files_folder_name: str = "_기타(미분류)",
        parent=None
    ):
        super().__init__(parent)
        self.base_folder = base_folder
        self.scan_result = scan_result
        self.mode = mode
        self.min_count = min_count
        self.folder_prefix = folder_prefix
        self.folder_suffix = folder_suffix
        self.organize_small_files = organize_small_files
        self.small_files_folder_name = small_files_folder_name
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            def on_progress(current, total, filename):
                if not self._is_cancelled:
                    self.progress.emit(current, total, filename)

            def on_log(msg):
                if not self._is_cancelled:
                    self.log.emit(msg)

            stats = organize_photos(
                base_folder=self.base_folder,
                scan_result=self.scan_result,
                mode=self.mode,
                min_count=self.min_count,
                folder_prefix=self.folder_prefix,
                folder_suffix=self.folder_suffix,
                organize_small_files=self.organize_small_files,
                small_files_folder_name=self.small_files_folder_name,
                progress_callback=on_progress,
                log_callback=on_log
            )
            if not self._is_cancelled:
                self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))
