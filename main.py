import sys
import os
import ctypes

# Windows 작업 표시줄 아이콘 분리 표시
try:
    myappid = "photoclustering.organizer.app.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# 현재 디렉터리를 sys.path에 추가 (상대 패키지 import 지원)
if getattr(sys, "frozen", False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    # 고해상도 DPI 화면 대응
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("PhotoClustering")
    app.setOrganizationName("PhotoClustering")

    # 애플리케이션 아이콘 설정
    icon_candidates = [
        os.path.join(current_dir, "icon.ico"),
        os.path.join(os.path.dirname(sys.executable), "icon.ico"),
    ]
    for ic in icon_candidates:
        if os.path.isfile(ic):
            app_icon = QIcon(ic)
            app.setWindowIcon(app_icon)
            break

    window = MainWindow()
    if not app.windowIcon().isNull():
        window.setWindowIcon(app.windowIcon())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
