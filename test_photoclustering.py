"""
PhotoClustering 단위 테스트 (Unit Tests)
================================================================================
설명:
    PhotoClustering 프로그램의 핵심 비즈니스 로직(날짜 추출, 폴더 스캔, 파일 정리)이
    의도한 대로 정확하게 작동하는지 검증하는 단위 테스트 스크립트입니다.
    
    * 테스트에 사용되는 파일명은 패턴 검증을 위한 가상 샘플(더미 데이터)이며,
      임시 폴더(tempfile)에서 테스트 완료 후 즉시 자동 삭제됩니다.

주요 테스트 항목:
    1. 파일명 기반 날짜 정규식 파싱 검증 (다양한 카메라/메신저 파일명 패턴)
    2. 이미지 EXIF 메타데이터(DateTimeOriginal) 일시 추출 검증
    3. 대상 폴더 중복 파일명 회피 (_1, _2 넘버링 부여) 검증
    4. N장 이상 날짜 클러스터링 및 파일 자동 이동/정리 로직 검증

실행 방법:
    python test_photoclustering.py
================================================================================
"""

import os
import sys
import shutil
import tempfile
import unittest
from PIL import Image, ExifTags

# 윈도우 cp949 환경에서도 한글/기호가 깨지지 않도록 UTF-8 인코딩 설정
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.date_extractor import (
    extract_date_from_filename,
    extract_date_from_exif,
    get_photo_date
)
from core.organizer import (
    scan_folder,
    organize_photos,
    get_unique_destination
)


class TestDateExtractor(unittest.TestCase):
    def test_filename_dates(self):
        """[1/4] 파일명 기반 날짜 정규식 패턴 파싱 테스트"""
        print("\n" + "=" * 75)
        print(" [1/4] 파일명 날짜 정규식 파싱 검사")
        print("=" * 75)

        cases = [
            ("20240101_123456.jpg", "2024-01-01"),
            ("IMG_20231225_091520.png", "2023-12-25"),
            ("Screenshot_2022-08-15-10-30-00.png", "2022-08-15"),
            ("KakaoTalk_20210304_112233.jpeg", "2021-03-04"),
            ("2020.07.19_vacation.jpg", "2020-07-19"),
            ("2024-05-10.mp4", "2024-05-10"),
            ("random_file_name.jpg", None),
            ("12345.jpg", None),
        ]
        for filename, expected in cases:
            with self.subTest(filename=filename):
                result = extract_date_from_filename(filename)
                status = "[PASS]" if result == expected else "[FAIL]"
                exp_str = str(expected) if expected else "미인식(None)"
                res_str = str(result) if result else "미인식(None)"
                print(f"  * 파일명: {filename:<36} -> 추출: {res_str:<12} (기대: {exp_str}) {status}")
                self.assertEqual(result, expected)

    def test_exif_extraction(self):
        """[2/4] 이미지 EXIF 촬영일시 메타데이터 추출 테스트"""
        print("\n" + "=" * 75)
        print(" [2/4] EXIF 메타데이터 촬영일시 추출 검사")
        print("=" * 75)

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "exif_test.jpg")
            img = Image.new("RGB", (64, 64), color="red")
            exif = img.getexif()
            # 0x9003: DateTimeOriginal (촬영 원본 일시)
            exif[0x9003] = "2023:11:15 14:30:00"
            img.save(img_path, exif=exif)

            # 1. EXIF 직접 추출 검증
            date_str = extract_date_from_exif(img_path)
            status_1 = "[PASS]" if date_str == "2023-11-15" else "[FAIL]"
            print(f"  * EXIF 원본: '2023:11:15 14:30:00' -> 추출: {date_str} {status_1}")
            self.assertEqual(date_str, "2023-11-15")

            # 2. 종합 날짜 판별 엔진 검증
            res_date, source = get_photo_date(img_path, prefer_exif=True)
            status_2 = "[PASS]" if (res_date == "2023-11-15" and source == "exif") else "[FAIL]"
            print(f"  * 종합 판별: 일자 {res_date}, 판별출처 [{source}] {status_2}")
            self.assertEqual(res_date, "2023-11-15")
            self.assertEqual(source, "exif")


class TestOrganizer(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_unique_destination(self):
        """[3/4] 대상 폴더 중복 파일명 자동 넘버링(_1, _2) 검사"""
        print("\n" + "=" * 75)
        print(" [3/4] 파일명 중복 회피(_1, _2 넘버링) 검사")
        print("=" * 75)

        f1 = os.path.join(self.tmpdir, "test.jpg")
        with open(f1, "w") as f:
            f.write("a")
        print(f"  * 원본 파일 존재: {os.path.basename(f1)}")

        dest1 = get_unique_destination(self.tmpdir, "test.jpg")
        with open(dest1, "w") as f:
            f.write("b")
        status_1 = "[PASS]" if os.path.basename(dest1) == "test_1.jpg" else "[FAIL]"
        print(f"  * 중복 1회 발생 시: test.jpg -> {os.path.basename(dest1)} {status_1}")
        self.assertEqual(dest1, os.path.join(self.tmpdir, "test_1.jpg"))

        dest2 = get_unique_destination(self.tmpdir, "test.jpg")
        status_2 = "[PASS]" if os.path.basename(dest2) == "test_2.jpg" else "[FAIL]"
        print(f"  * 중복 2회 발생 시: test.jpg -> {os.path.basename(dest2)} {status_2}")
        self.assertEqual(dest2, os.path.join(self.tmpdir, "test_2.jpg"))

    def test_scan_and_organize(self):
        """[4/4] 10장 이상 날짜 클러스터링 및 파일 자동 이동/정리 검사"""
        print("\n" + "=" * 75)
        print(" [4/4] N장 이상 클러스터링 및 자동 폴더 이동 검사")
        print("=" * 75)

        # 1. 2024-01-01 날짜의 파일 12개 생성 (10장 이상 -> 폴더 생성 대상)
        for i in range(12):
            fname = f"20240101_{i:02d}.jpg"
            fpath = os.path.join(self.tmpdir, fname)
            with open(fpath, "w") as f:
                f.write("sample")

        # 2. 2024-02-01 날짜의 파일 5개 생성 (10장 미만 -> 폴더 생성 제외)
        for i in range(5):
            fname = f"20240201_{i:02d}.jpg"
            fpath = os.path.join(self.tmpdir, fname)
            with open(fpath, "w") as f:
                f.write("sample")

        # 3. 날짜 없는 알 수 없는 파일 2개 생성
        for i in range(2):
            fname = f"unknown_{i:02d}.jpg"
            fpath = os.path.join(self.tmpdir, fname)
            with open(fpath, "w") as f:
                f.write("sample")

        print(f"  * 생성된 가상 파일: 총 19개 (2024-01-01: 12개, 2024-02-01: 5개, 날짜미상: 2개)")

        # 4. 스캔 실행 (최소 10장 기준)
        scan_res = scan_folder(self.tmpdir, min_count=10)
        print(f"  * 스캔 결과: 전체 {scan_res.total_files}개 탐지 (분류 완료 {scan_res.classified_files_count}개, 미분류 {len(scan_res.unclassified_files)}개) [PASS]")
        self.assertEqual(scan_res.total_files, 19)
        self.assertEqual(scan_res.classified_files_count, 17)
        self.assertEqual(len(scan_res.unclassified_files), 2)

        # 클러스터 판정 확인
        c_20240101 = next(c for c in scan_res.clusters if c.date == "2024-01-01")
        print(f"  * [2024-01-01] {c_20240101.count}장 감지 -> 10장 이상이므로 폴더 생성 판정: {c_20240101.will_create_folder} ('{c_20240101.target_folder_name}') [PASS]")
        self.assertEqual(c_20240101.count, 12)
        self.assertTrue(c_20240101.will_create_folder)
        self.assertEqual(c_20240101.target_folder_name, "2024-01-01_")

        c_20240201 = next(c for c in scan_res.clusters if c.date == "2024-02-01")
        print(f"  * [2024-02-01] {c_20240201.count}장 감지 -> 10장 미만이므로 폴더 생성 건너뛰기 판정: {not c_20240201.will_create_folder} [PASS]")
        self.assertEqual(c_20240201.count, 5)
        self.assertFalse(c_20240201.will_create_folder)

        # 5. 파일 이동 실행 (Move 모드)
        stats = organize_photos(self.tmpdir, scan_res, mode="move", min_count=10)
        print(f"  * 이동 실행 통계: 폴더 {stats['created_folders']}개 생성, 파일 {stats['moved_files']}개 이동, {stats['skipped_files']}개 원본 보존 [PASS]")
        self.assertEqual(stats["created_folders"], 1)
        self.assertEqual(stats["moved_files"], 12)
        self.assertEqual(stats["skipped_files"], 5)

        # 실제 폴더 및 파일 존재 검증
        target_dir = os.path.join(self.tmpdir, "2024-01-01_")
        self.assertTrue(os.path.isdir(target_dir))
        self.assertEqual(len(os.listdir(target_dir)), 12)
        print(f"  * 실제 디스크 검증: '2024-01-01_' 폴더 안에 정확히 12장 이동 확인 완료 [PASS]")


if __name__ == "__main__":
    unittest.main(verbosity=2)
