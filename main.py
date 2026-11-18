import re
import json
import math
import time
from pathlib import Path

EPSILON = 1e-9
REPEAT = 10

def make_matrix(n):
    """n행 n열의 숫자 표를 만들고 모든 칸을 0으로 채웁니다."""
    matrix = []

    for row_index in range(n):
        row = []

        for column_index in range(n):
            row.append(0)

        matrix.append(row)

    return matrix


def mac(pattern, filt):
    """같은 크기의 정사각형 패턴과 필터를 곱하고 더합니다."""
    total = 0.0
    n = len(pattern)

    for row_index in range(n):
        for column_index in range(n):
            total += pattern[row_index][column_index] * filt[row_index][column_index]

    return total


def judge(score_a, score_b, label_a="A", label_b="B"):
    """허용오차보다 작은 점수 차이는 동점으로 처리합니다."""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b


def run_basic_checks():
    print("=== 배열 크기 확인 ===")

    for n in [3, 5, 13, 25]:
        matrix = make_matrix(n)
        print(f"{n}x{n}: {len(matrix)}행, {len(matrix[0])}열")

    print()
    print("=== 특정 위치 읽기와 쓰기 ===")

    matrix = make_matrix(3)

    print(f"변경 전 가운데 값: {matrix[1][1]}")

    matrix[1][1] = 1

    print(f"변경 후 가운데 값: {matrix[1][1]}")
    print("전체 배열:")

    for row in matrix:
        print(row)

    print()
    print("=== MAC 연산 확인 ===")

    cross = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]

    x_pattern = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]

    print(f"십자가 입력 / 십자가 필터: {mac(cross, cross)}")
    print(f"십자가 입력 / X 필터: {mac(cross, x_pattern)}")
    print(f"X 입력 / 십자가 필터: {mac(x_pattern, cross)}")
    print(f"X 입력 / X 필터: {mac(x_pattern, x_pattern)}")


def read_matrix(name, n=3):
    print(f"\n{name}: {n}줄을 입력하세요. 각 줄에는 숫자 {n}개가 필요합니다.")
    matrix = []

    for row_index in range(n):
        while True:
            parts = input(f"{row_index + 1}행: ").split()

            if len(parts) != n:
                print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
                continue

            try:
                row = [float(part) for part in parts]
            except ValueError:
                print("입력 형식 오류: 문자 대신 숫자를 입력하세요.")
                continue

            if not all(math.isfinite(value) for value in row):
                print("입력 형식 오류: nan이나 inf 대신 유한한 숫자를 입력하세요.")
                continue

            matrix.append(row)
            break

    return matrix


def print_matrix(name, matrix):
    print(f"\n{name} 저장 확인:")

    for row in matrix:
        print(" ".join(f"{value:g}" for value in row))


def measure_mac_ms(pattern, filt, repeat=REPEAT):
    """필터 하나의 MAC 계산을 반복 측정하고 평균 ms를 반환합니다."""
    elapsed = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        mac(pattern, filt)
        end = time.perf_counter()

        elapsed += end - start

    return elapsed / repeat * 1000


def parse_size_key(key, is_pattern=False):
    """필터 또는 패턴 키의 형식을 검사하고 크기 N을 반환합니다."""
    if is_pattern:
        rule = r"size_([1-9][0-9]*)_[1-9][0-9]*"
    else:
        rule = r"size_([1-9][0-9]*)"

    match = re.fullmatch(rule, key) if isinstance(key, str) else None

    if match is None:
        raise ValueError(f"키 형식 오류: {key}")

    return int(match.group(1))


def validate_matrix(matrix, n):
    """배열이 N×N이며 모든 값이 유한한 숫자인지 검사합니다."""
    if not isinstance(matrix, list) or len(matrix) != n:
        raise ValueError(f"행 수 오류: {n}행이 필요합니다.")

    for row_index, row in enumerate(matrix, start=1):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(
                f"{row_index}행의 열 수 오류: {n}개가 필요합니다."
            )

        for value in row:
            if type(value) not in (int, float):
                raise ValueError(
                    f"{row_index}행의 값 오류: 숫자가 필요합니다."
                )

            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(
                    f"{row_index}행의 값 오류: 유한한 숫자가 필요합니다."
                )


def normalize_label(raw):
    """정답 라벨을 Cross 또는 X로 통일합니다."""
    if not isinstance(raw, str):
        return None

    labels = {
        "cross": "Cross",
        "+": "Cross",
        "x": "X",
    }

    return labels.get(raw.strip().lower())


def load_data():
    """main.py와 같은 폴더에 있는 data.json을 읽습니다."""
    data_path = Path(__file__).resolve().parent / "data.json"

    with data_path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def preview_data():
    """JSON의 키, 필터 크기, 패턴의 기대 정답을 확인합니다."""
    data = load_data()

    print("=== JSON 구조 확인 ===")
    print("최상위 키:", ", ".join(data.keys()))

    print("\n필터 목록:")
    for filter_key, filters in data["filters"].items():
        for label, matrix in filters.items():
            rows = len(matrix)
            row_lengths = [len(row) for row in matrix]
            print(
                f"{filter_key} / {label}: "
                f"행 수={rows}, 각 행의 열 수={row_lengths}"
            )

    print("\n패턴 목록:")
    for case_key, case in data["patterns"].items():
        matrix = case["input"]
        rows = len(matrix)
        row_lengths = [len(row) for row in matrix]
        expected = case["expected"]

        print(
            f"{case_key}: 행 수={rows}, "
            f"각 행의 열 수={row_lengths}, expected={expected}"
        )

    print(f"\n전체 패턴 수: {len(data['patterns'])}")


def check_data_structure():
    """실제 JSON의 키, 배열 크기, 정답 라벨을 검사합니다."""
    data = load_data()

    print("=== 필터 검증 ===")
    for filter_key, filters in data["filters"].items():
        n = parse_size_key(filter_key)

        for label in ("cross", "x"):
            validate_matrix(filters[label], n)

        print(f"{filter_key}: {n}x{n}, cross/x 배열 정상")

    print("\n=== 패턴 검증 ===")
    for case_key, case in data["patterns"].items():
        n = parse_size_key(case_key, is_pattern=True)
        filter_key = f"size_{n}"

        if filter_key not in data["filters"]:
            raise ValueError(f"{case_key}: 대응하는 필터가 없습니다.")

        validate_matrix(case["input"], n)
        expected = normalize_label(case["expected"])

        if expected is None:
            raise ValueError(f"{case_key}: 알 수 없는 expected 라벨입니다.")

        print(
            f"{case_key}: {n}x{n}, "
            f"필터={filter_key}, expected={expected}, 데이터 정상"
        )

    print(f"\n검증 완료: 패턴 {len(data['patterns'])}개")


def main():
    print("=== Mini NPU Simulator: 사용자 입력 기능 확인 ===")

    filter_a = read_matrix("필터 A")
    filter_b = read_matrix("필터 B")

    print_matrix("필터 A", filter_a)
    print_matrix("필터 B", filter_b)

    pattern = read_matrix("패턴")
    print_matrix("패턴", pattern)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    print("\n=== MAC 결과 ===")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    
    result = judge(score_a, score_b)

    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (점수 차이 < {EPSILON:g})")
    else:
        print(f"판정: {result}")

    average_ms = measure_mac_ms(pattern, filter_a)
    n = len(pattern)

    print(f"\n=== 성능 분석: {REPEAT}회 평균 ===")
    print("측정 대상: 입력 패턴과 필터 A의 MAC 함수 호출")
    print("크기(N×N) | 평균 시간(ms) | MAC 연산 횟수(N²)")
    print(f"{n}x{n} | {average_ms:.6f} | {n * n}")


if __name__ == "__main__":
    main()

    