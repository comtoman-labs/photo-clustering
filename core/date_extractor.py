import os
import re
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image, ExifTags

# EXIF DateTime 태그 ID 매핑
EXIF_DATE_TAGS = (
    "DateTimeOriginal",  # 0x9003
    "DateTimeDigitized", # 0x9004
    "DateTime",          # 0x0132
)

# 파일명 내 날짜 정규식 패턴 (2000~2099년 또는 1980~1999년)
# 20240101, 2024-01-01, 2024_01_01, 2024.01.01 등 매칭
FILENAME_DATE_PATTERNS = [
    # YYYY-MM-DD, YYYY_MM_DD, YYYY.MM.DD
    re.compile(r"(?:^|[^0-9])((?:19[89]\d|20\d{2}))[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])(?:[^0-9]|$)"),
    # YYYYMMDD (연속 8자리)
    re.compile(r"(?:^|[^0-9])((?:19[89]\d|20\d{2}))(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?:[^0-9]|$)"),
]


def extract_date_from_exif(file_path: str) -> Optional[str]:
    """이미지 파일의 EXIF 메타데이터에서 촬영 일시(YYYY-MM-DD)를 추출합니다."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif'):
        return None

    try:
        with Image.open(file_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                return None

            # get_ifd(ExifTags.IFD.Exif)도 확인 (Exif SubIFD)
            sub_exif = None
            try:
                sub_exif = exif_data.get_ifd(ExifTags.IFD.Exif)
            except Exception:
                sub_exif = None

            date_str = None
            # 메인 EXIF 및 SubIFD 순회
            for ifd in (sub_exif, exif_data):
                if not ifd:
                    continue
                for tag_id, value in ifd.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag_name in EXIF_DATE_TAGS and isinstance(value, str):
                        date_str = value.strip()
                        if date_str and not date_str.startswith("0000"):
                            break
                if date_str:
                    break

            if date_str:
                # 일반적인 EXIF 포맷: "YYYY:MM:DD HH:MM:SS"
                match = re.match(r"^(\d{4})[:\-](\d{2})[:\-](\d{2})", date_str)
                if match:
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    if 1980 <= year <= 2099 and 1 <= month <= 12 and 1 <= day <= 31:
                        return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception:
        return None

    return None


def extract_date_from_filename(filename: str) -> Optional[str]:
    """파일명에서 날짜 패턴(YYYY-MM-DD)을 추출합니다."""
    stem = os.path.splitext(filename)[0]

    for pattern in FILENAME_DATE_PATTERNS:
        match = pattern.search(stem)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1980 <= year <= 2099 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"

    return None


def extract_date_from_mtime(file_path: str) -> Optional[str]:
    """파일 수정 시간(mtime)에서 날짜(YYYY-MM-DD)를 추출합니다."""
    try:
        mtime = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def get_photo_date(
    file_path: str,
    prefer_exif: bool = True,
    allow_mtime_fallback: bool = False
) -> Tuple[Optional[str], str]:
    """
    사진의 날짜를 추출합니다.
    
    Returns:
        (date_str, source_type): ('2024-05-01', 'exif' | 'filename' | 'mtime' | 'unknown')
    """
    filename = os.path.basename(file_path)

    if prefer_exif:
        # 1순위: EXIF
        exif_date = extract_date_from_exif(file_path)
        if exif_date:
            return exif_date, "exif"

        # 2순위: 파일명
        fn_date = extract_date_from_filename(filename)
        if fn_date:
            return fn_date, "filename"
    else:
        # 파일명 우선
        fn_date = extract_date_from_filename(filename)
        if fn_date:
            return fn_date, "filename"

        exif_date = extract_date_from_exif(file_path)
        if exif_date:
            return exif_date, "exif"

    # 3순위: mtime (선택적 fallback)
    if allow_mtime_fallback:
        mtime_date = extract_date_from_mtime(file_path)
        if mtime_date:
            return mtime_date, "mtime"

    return None, "unknown"
