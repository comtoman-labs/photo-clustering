import os
import sys
from datetime import datetime
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QSpinBox, QRadioButton,
    QButtonGroup, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QPlainTextEdit, QFrame, QMessageBox,
    QSplitter
)

from core.organizer import ScanResult
from ui.worker import ScanWorker, OrganizeWorker
from ui.style import get_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoClustering - 사진 날짜별 자동 분류기")
        self.resize(1180, 860)
        self.setMinimumSize(1020, 700)
        self.setAcceptDrops(True)

        self.current_theme = "dark"
        self.scan_result: ScanResult = None
        self.scan_worker: ScanWorker = None
        self.organize_worker: OrganizeWorker = None

        # 아이콘 설정
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._setup_ui()
        self.setStyleSheet(get_stylesheet("dark"))

        # 테마 전환 단축키 (F6)
        toggle_action = QAction("테마 전환", self)
        toggle_action.setShortcut(QKeySequence("F6"))
        toggle_action.triggered.connect(self.toggle_theme)
        self.addAction(toggle_action)

    def toggle_theme(self):
        from PySide6.QtWidgets import QApplication
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        new_style = get_stylesheet(self.current_theme)

        # MainWindow 인스턴스와 QApplication 전체에 스타일시트 동시 적용
        self.setStyleSheet(new_style)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(new_style)

        if self.current_theme == "dark":
            self.theme_btn.setText("🌙 Dark")
            self.theme_btn.setToolTip("Light 모드로 전환 (F6)")
        else:
            self.theme_btn.setText("☀️ Light")
            self.theme_btn.setToolTip("Dark 모드로 전환 (F6)")

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Header (제목 + 설명 + 우측 테마 토글 버튼)
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)
        title_label = QLabel("PhotoClustering")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel("사진 메타데이터(EXIF) 및 파일명 날짜를 분석하여 10장 이상의 날짜별 폴더를 자동 생성·정리합니다.")
        subtitle_label.setObjectName("SubtitleLabel")
        header_text_layout.addWidget(title_label)
        header_text_layout.addWidget(subtitle_label)
        header_row.addLayout(header_text_layout, 1)

        self.theme_btn = QPushButton("🌙 Dark")
        self.theme_btn.setObjectName("SecondarySmallBtn")
        self.theme_btn.setToolTip("Light 모드로 전환 (F6)")
        self.theme_btn.setMinimumHeight(32)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_row.addWidget(self.theme_btn, 0, Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(header_row)

        # 2. Folder Select Card
        folder_card = QFrame()
        folder_card.setObjectName("CardFrame")
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setSpacing(10)

        folder_header = QLabel("📁 작업 대상 폴더 선택 (탐색기에서 폴더를 창으로 끌어다 놓아도 됩니다)")
        folder_header.setObjectName("SectionTitle")
        folder_layout.addWidget(folder_header)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("정리할 사진이 들어있는 폴더 경로를 입력하거나 선택하세요...")
        self.path_edit.setMinimumHeight(38)
        self.path_edit.textChanged.connect(self._on_folder_changed)

        self.btn_browse = QPushButton("폴더 선택...")
        self.btn_browse.setMinimumHeight(38)
        self.btn_browse.setMinimumWidth(105)
        self.btn_browse.clicked.connect(self._browse_folder)

        self.btn_open_folder = QPushButton("폴더 열기")
        self.btn_open_folder.setMinimumHeight(38)
        self.btn_open_folder.setMinimumWidth(95)
        self.btn_open_folder.clicked.connect(self._open_current_folder)

        path_row.addWidget(self.path_edit)
        path_row.addWidget(self.btn_browse)
        path_row.addWidget(self.btn_open_folder)
        folder_layout.addLayout(path_row)

        main_layout.addWidget(folder_card)

        # 3. Settings Card
        settings_card = QFrame()
        settings_card.setObjectName("CardFrame")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(12)

        settings_title = QLabel("⚙️ 분류 설정")
        settings_title.setObjectName("SectionTitle")
        settings_layout.addWidget(settings_title)

        # Settings Grid / Rows
        row1 = QHBoxLayout()
        row1.setSpacing(24)

        # Min Count SpinBox
        lbl_min_count = QLabel("최소 사진 수 (폴더 생성 기준):")
        self.spin_min_count = QSpinBox()
        self.spin_min_count.setRange(1, 1000)
        self.spin_min_count.setValue(10)
        self.spin_min_count.setSuffix(" 장")
        self.spin_min_count.setMinimumWidth(100)
        row1.addWidget(lbl_min_count)
        row1.addWidget(self.spin_min_count)

        # Work Mode (Move vs Copy)
        lbl_mode = QLabel("작업 방식:")
        self.rb_move = QRadioButton("이동 (Move)")
        self.rb_copy = QRadioButton("복사 (Copy)")
        self.rb_move.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.rb_move)
        self.mode_group.addButton(self.rb_copy)
        row1.addWidget(lbl_mode)
        row1.addWidget(self.rb_move)
        row1.addWidget(self.rb_copy)

        row1.addStretch()
        settings_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(24)

        # Priority (EXIF vs Filename)
        lbl_priority = QLabel("날짜 우선순위:")
        self.rb_exif_first = QRadioButton("촬영정보(EXIF) 우선")
        self.rb_name_first = QRadioButton("파일명 우선")
        self.rb_exif_first.setChecked(True)
        self.priority_group = QButtonGroup(self)
        self.priority_group.addButton(self.rb_exif_first)
        self.priority_group.addButton(self.rb_name_first)
        row2.addWidget(lbl_priority)
        row2.addWidget(self.rb_exif_first)
        row2.addWidget(self.rb_name_first)

        # Folder Suffix
        lbl_suffix = QLabel("폴더명 접미사:")
        self.edit_suffix = QLineEdit("_")
        self.edit_suffix.setMinimumWidth(60)
        self.edit_suffix.setMaximumWidth(90)
        row2.addWidget(lbl_suffix)
        row2.addWidget(self.edit_suffix)

        # Small files handling
        self.chk_small_files = QCheckBox("기준 미만 파일도 '_기타' 폴더로 모으기")
        self.chk_small_files.setChecked(False)
        row2.addWidget(self.chk_small_files)

        row2.addStretch()
        settings_layout.addLayout(row2)

        main_layout.addWidget(settings_card)

        # 4. Preview Table + Log Console (Splitter)
        splitter = QSplitter(Qt.Vertical)

        # Preview Section
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        table_header_layout = QHBoxLayout()
        self.lbl_table_summary = QLabel("📊 스캔 결과: 폴더를 지정한 후 [스캔 및 미리보기] 버튼을 누르세요.")
        self.lbl_table_summary.setObjectName("SectionTitle")
        table_header_layout.addWidget(self.lbl_table_summary)
        preview_layout.addLayout(table_header_layout)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["날짜", "사진 수", "폴더 생성 여부", "생성될 폴더명"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 140)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 110)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 230)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        preview_layout.addWidget(self.table)

        splitter.addWidget(preview_container)

        # Log Section
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(8)

        log_header_layout = QHBoxLayout()
        lbl_log = QLabel("📝 실행 로그")
        btn_clear_log = QPushButton("로그 지우기")
        btn_clear_log.setObjectName("SecondarySmallBtn")
        btn_clear_log.clicked.connect(lambda: self.log_view.clear())
        log_header_layout.addWidget(lbl_log)
        log_header_layout.addStretch()
        log_header_layout.addWidget(btn_clear_log)
        log_layout.addLayout(log_header_layout)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("LogView")
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(160)
        log_layout.addWidget(self.log_view)

        splitter.addWidget(log_container)
        splitter.setSizes([340, 150])
        main_layout.addWidget(splitter, 1)

        # 5. Progress Bar & Status
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(6)
        self.lbl_status = QLabel("대기 중...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.lbl_status)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        # 6. Bottom Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        self.btn_scan = QPushButton("🔍 1. 스캔 및 미리보기")
        self.btn_scan.setObjectName("PrimaryBtn")
        self.btn_scan.setMinimumHeight(48)
        self.btn_scan.clicked.connect(self._start_scan)

        self.btn_organize = QPushButton("🚀 2. 정리 실행")
        self.btn_organize.setObjectName("SuccessBtn")
        self.btn_organize.setMinimumHeight(48)
        self.btn_organize.setEnabled(False)
        self.btn_organize.clicked.connect(self._start_organize)

        btn_layout.addWidget(self.btn_scan, 1)
        btn_layout.addWidget(self.btn_organize, 1)
        main_layout.addLayout(btn_layout)

    # --- Drag & Drop Support ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and os.path.isdir(urls[0].toLocalFile()):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.path_edit.setText(path)
                self.log(f"📁 폴더가 드롭되었습니다: {path}")

    # --- UI Helpers ---
    def log(self, message: str):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_view.appendPlainText(f"[{now}] {message}")
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "정리할 폴더 선택", self.path_edit.text() or "")
        if folder:
            self.path_edit.setText(folder)

    def _open_current_folder(self):
        folder = self.path_edit.text().strip().strip('"')
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        else:
            QMessageBox.warning(self, "경고", "올바른 폴더 경로가 아닙니다.")

    def _on_folder_changed(self):
        self.btn_organize.setEnabled(False)
        self.scan_result = None

    # --- Scan Logic ---
    def _start_scan(self):
        folder = self.path_edit.text().strip().strip('"')
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "경고", "먼저 올바른 폴더 경로를 선택해 주세요.")
            return

        self.btn_scan.setEnabled(False)
        self.btn_organize.setEnabled(False)
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("폴더 내 파일 스캔 및 날짜 분석 중...")
        self.log(f"🔍 스캔 시작: {folder}")

        min_count = self.spin_min_count.value()
        prefer_exif = self.rb_exif_first.isChecked()
        suffix = self.edit_suffix.text()

        self.scan_worker = ScanWorker(
            base_folder=folder,
            prefer_exif=prefer_exif,
            allow_mtime=False,
            min_count=min_count,
            folder_suffix=suffix
        )
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.error.connect(self._on_worker_error)
        self.scan_worker.start()

    def _on_scan_progress(self, current: int, total: int, filename: str):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.lbl_status.setText(f"분석 중 ({current}/{total}): {filename}")

    def _on_scan_finished(self, result: ScanResult):
        self.scan_result = result
        self.btn_scan.setEnabled(True)
        self.lbl_status.setText(f"스캔 완료! (총 {result.total_files}개 파일 발견)")

        # Populate Table
        clusters = result.clusters
        self.table.setRowCount(len(clusters))

        will_create_count = 0
        total_cluster_files = 0

        for row, cluster in enumerate(clusters):
            # Date item
            item_date = QTableWidgetItem(cluster.date)
            item_date.setTextAlignment(Qt.AlignCenter)

            # Count item
            item_count = QTableWidgetItem(f"{cluster.count} 장")
            item_count.setTextAlignment(Qt.AlignCenter)

            # Status item
            if cluster.will_create_folder:
                will_create_count += 1
                total_cluster_files += cluster.count
                status_text = f"✅ 폴더 생성 ({self.spin_min_count.value()}장 이상)"
                target_folder = cluster.target_folder_name
            else:
                if self.chk_small_files.isChecked():
                    status_text = "📦 '_기타' 폴더로 이동"
                    target_folder = "_기타(미분류)"
                else:
                    status_text = "⏸️ 보류 (원본 위치 유지)"
                    target_folder = "-"

            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignCenter)

            item_folder = QTableWidgetItem(target_folder)

            self.table.setItem(row, 0, item_date)
            self.table.setItem(row, 1, item_count)
            self.table.setItem(row, 2, item_status)
            self.table.setItem(row, 3, item_folder)

        unclassified_len = len(result.unclassified_files)
        summary_text = (
            f"📊 총 대상 파일: {result.total_files}개 | "
            f"날짜 인식: {result.classified_files_count}개 | "
            f"미인식: {unclassified_len}개 | "
            f"생성 예정 폴더: {will_create_count}개"
        )
        self.lbl_table_summary.setText(summary_text)
        self.log(summary_text)

        if will_create_count > 0 or (self.chk_small_files.isChecked() and result.total_files > 0):
            self.btn_organize.setEnabled(True)
            self.log("💡 [정리 실행] 버튼을 누르면 파일 이동/복사가 시작됩니다.")
        else:
            self.btn_organize.setEnabled(False)
            self.log(f"⚠️ {self.spin_min_count.value()}장 이상인 날짜가 없어 생성할 폴더가 없습니다.")

    # --- Organize Logic ---
    def _start_organize(self):
        if not self.scan_result:
            return

        folder = self.path_edit.text().strip().strip('"')
        mode_text = "이동" if self.rb_move.isChecked() else "복사"
        min_count = self.spin_min_count.value()

        reply = QMessageBox.question(
            self,
            "정리 실행 확인",
            f"선택한 옵션으로 파일 {mode_text} 작업을 진행하시겠습니까?\n\n"
            f"• 대상 폴더: {folder}\n"
            f"• 작업 모드: {mode_text}\n"
            f"• 최소 기준: {min_count}장 이상",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        self.btn_scan.setEnabled(False)
        self.btn_organize.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(f"파일 {mode_text} 작업 진행 중...")
        self.log(f"🚀 파일 {mode_text} 작업 시작...")

        mode = "move" if self.rb_move.isChecked() else "copy"
        suffix = self.edit_suffix.text()
        organize_small = self.chk_small_files.isChecked()

        self.organize_worker = OrganizeWorker(
            base_folder=folder,
            scan_result=self.scan_result,
            mode=mode,
            min_count=min_count,
            folder_suffix=suffix,
            organize_small_files=organize_small
        )
        self.organize_worker.progress.connect(self._on_organize_progress)
        self.organize_worker.log.connect(self.log)
        self.organize_worker.finished.connect(self._on_organize_finished)
        self.organize_worker.error.connect(self._on_worker_error)
        self.organize_worker.start()

    def _on_organize_progress(self, current: int, total: int, filename: str):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.lbl_status.setText(f"처리 중 ({current}/{total}): {filename}")

    def _on_organize_finished(self, stats: dict):
        self.btn_scan.setEnabled(True)
        self.btn_organize.setEnabled(False)
        self.lbl_status.setText("✅ 모든 파일 정리가 완료되었습니다!")

        summary_msg = (
            f"정리 작업이 완료되었습니다!\n\n"
            f"• 생성된 폴더: {stats['created_folders']}개\n"
            f"• 이동된 파일: {stats['moved_files']}개\n"
            f"• 복사된 파일: {stats['copied_files']}개\n"
            f"• 보류된 파일: {stats['skipped_files']}개\n"
            f"• 오류: {stats['errors']}개"
        )
        self.log(f"🎉 {summary_msg.replace(chr(10), ' ')}")

        reply = QMessageBox.information(
            self,
            "완료",
            summary_msg + "\n\n폴더를 열어 확인하시겠습니까?",
            QMessageBox.Open | QMessageBox.Ok,
            QMessageBox.Open
        )
        if reply == QMessageBox.Open:
            self._open_current_folder()

    def _on_worker_error(self, error_msg: str):
        self.btn_scan.setEnabled(True)
        self.lbl_status.setText("❌ 작업 중 오류가 발생했습니다.")
        self.log(f"❌ 오류: {error_msg}")
        QMessageBox.critical(self, "오류", f"작업 중 오류가 발생했습니다:\n{error_msg}")
