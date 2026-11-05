import os
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from core.date_extractor import get_photo_date

SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif',
    '.heic', '.mp4', '.mov', '.avi', '.mkv', '.wmv'
)


@dataclass
class FileItem:
    filename: str
    file_path: str
    date: Optional[str]
    source: str  # 'exif', 'filename', 'mtime', 'unknown'


@dataclass
class ClusterInfo:
    date: str
    count: int
    will_create_folder: bool
    target_folder_name: str
    files: List[FileItem] = field(default_factory=list)


@dataclass
class ScanResult:
    base_folder: str
    total_files: int = 0
    classified_files_count: int = 0
    clusters: List[ClusterInfo] = field(default_factory=list)
    unclassified_files: List[FileItem] = field(default_factory=list)


def get_unique_destination(dest_folder: str, filename: str) -> str:
    """대상 폴더에 이미 동일한 이름의 파일이 존재할 경우 _1, _2 넘버링을 부여합니다."""
    dest_path = os.path.join(dest_folder, filename)
    if not os.path.exists(dest_path):
        return dest_path

    base_name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{base_name}_{counter}{ext}"
        new_dest_path = os.path.join(dest_folder, new_filename)
        if not os.path.exists(new_dest_path):
            return new_dest_path
        counter += 1


def scan_folder(
    base_folder: str,
    prefer_exif: bool = True,
    allow_mtime_fallback: bool = False,
    min_count: int = 10,
    folder_prefix: str = "",
    folder_suffix: str = "_",
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> ScanResult:
    """
    폴더 내의 사진 및 영상 파일을 스캔하여 날짜별 클러스터를 계산합니다.
    """
    result = ScanResult(base_folder=base_folder)
    if not os.path.isdir(base_folder):
        return result

    # 1. 파일 목록 수집 (하위 폴더 제외)
    candidate_files = []
    for entry in os.listdir(base_folder):
        full_path = os.path.join(base_folder, entry)
        if os.path.isfile(full_path):
            if entry.lower().endswith(SUPPORTED_EXTENSIONS):
                candidate_files.append(entry)

    result.total_files = len(candidate_files)
    if result.total_files == 0:
        return result

    # 2. 파일별 날짜 분석
    date_map: Dict[str, List[FileItem]] = defaultdict(list)

    for idx, filename in enumerate(candidate_files):
        file_path = os.path.join(base_folder, filename)
        date_str, source = get_photo_date(
            file_path,
            prefer_exif=prefer_exif,
            allow_mtime_fallback=allow_mtime_fallback
        )

        item = FileItem(
            filename=filename,
            file_path=file_path,
            date=date_str,
            source=source
        )

        if date_str:
            date_map[date_str].append(item)
            result.classified_files_count += 1
        else:
            result.unclassified_files.append(item)

        if progress_callback:
            progress_callback(idx + 1, result.total_files, filename)

    # 3. 클러스터 목록 생성 (날짜 내림차순 정렬)
    sorted_dates = sorted(date_map.keys(), reverse=True)
    for date_str in sorted_dates:
        files = date_map[date_str]
        will_create = len(files) >= min_count
        folder_name = f"{folder_prefix}{date_str}{folder_suffix}"
        
        result.clusters.append(
            ClusterInfo(
                date=date_str,
                count=len(files),
                will_create_folder=will_create,
                target_folder_name=folder_name,
                files=files
            )
        )

    return result


def organize_photos(
    base_folder: str,
    scan_result: ScanResult,
    mode: str = "move",  # 'move' 또는 'copy'
    min_count: int = 10,
    folder_prefix: str = "",
    folder_suffix: str = "_",
    organize_small_files: bool = False,
    small_files_folder_name: str = "_미분류_기타",
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, int]:
    """
    스캔 결과를 바탕으로 폴더를 생성하고 파일 이동/복사를 실행합니다.
    """
    stats = {
        "moved_files": 0,
        "copied_files": 0,
        "created_folders": 0,
        "skipped_files": 0,
        "errors": 0
    }

    # 작업 대상 파일 목록 구성
    tasks: List[tuple[FileItem, str]] = [] # (item, target_folder_path)

    for cluster in scan_result.clusters:
        if len(cluster.files) >= min_count:
            folder_name = f"{folder_prefix}{cluster.date}{folder_suffix}"
            target_dir = os.path.join(base_folder, folder_name)
            for file_item in cluster.files:
                tasks.append((file_item, target_dir))
        else:
            if organize_small_files:
                target_dir = os.path.join(base_folder, small_files_folder_name)
                for file_item in cluster.files:
                    tasks.append((file_item, target_dir))
            else:
                stats["skipped_files"] += len(cluster.files)

    total_tasks = len(tasks)
    if total_tasks == 0:
        if log_callback:
            log_callback("⚠️ 처리할 파일이 없습니다. (조건을 만족하는 날짜가 없음)")
        return stats

    created_dirs = set()

    for idx, (item, target_dir) in enumerate(tasks):
        # 폴더 생성
        if target_dir not in created_dirs:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                stats["created_folders"] += 1
                if log_callback:
                    log_callback(f"📁 폴더 생성: {os.path.basename(target_dir)}")
            created_dirs.add(target_dir)

        # 고유 대상 파일 경로 계산 (덮어쓰기 방지)
        dest_path = get_unique_destination(target_dir, item.filename)
        dest_filename = os.path.basename(dest_path)

        try:
            if mode == "copy":
                shutil.copy2(item.file_path, dest_path)
                stats["copied_files"] += 1
                action_text = "복사"
            else:
                shutil.move(item.file_path, dest_path)
                stats["moved_files"] += 1
                action_text = "이동"

            if dest_filename != item.filename:
                log_msg = f"[{action_text}] {item.filename} ➔ {os.path.basename(target_dir)}/{dest_filename} (이름 중복 변경)"
            else:
                log_msg = f"[{action_text}] {item.filename} ➔ {os.path.basename(target_dir)}/"

            if log_callback:
                log_callback(log_msg)

        except Exception as e:
            stats["errors"] += 1
            if log_callback:
                log_callback(f"❌ 오류 발생 ({item.filename}): {str(e)}")

        if progress_callback:
            progress_callback(idx + 1, total_tasks, item.filename)

    return stats
