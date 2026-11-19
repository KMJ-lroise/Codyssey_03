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


def generate_cross(n):
    """3 이상의 홀수 크기로 십자가 패턴을 만듭니다."""
    if type(n) is not int or n < 3 or n % 2 == 0:
        raise ValueError("크기는 3 이상의 홀수 정수여야 합니다.")

    matrix = make_matrix(n)
    center = n // 2
    for index in range(n):
        matrix[center][index] = 1.0
        matrix[index][center] = 1.0
    return matrix


def generate_x(n):
    """3 이상의 홀수 크기로 X 패턴을 만듭니다."""
    if type(n) is not int or n < 3 or n % 2 == 0:
        raise ValueError("크기는 3 이상의 홀수 정수여야 합니다.")

    matrix = make_matrix(n)
    for index in range(n):
        matrix[index][index] = 1.0
        matrix[index][n - 1 - index] = 1.0
    return matrix


def mac(pattern, filt):
    """같은 크기의 정사각형 패턴과 필터를 곱하고 더합니다."""
    total = 0.0
    n = len(pattern)

    for row_index in range(n):
        for column_index in range(n):
            total += pattern[row_index][column_index] * filt[row_index][column_index]

    return total


def flatten_matrix(matrix):
    """2차원 배열을 행 순서대로 이어 붙인 1차원 리스트로 만듭니다."""
    flat = []
    for row in matrix:
        for value in row:
            flat.append(value)
    return flat


def mac_1d(pattern, filt):
    """길이가 같은 1차원 리스트의 MAC 점수를 계산합니다."""
    if len(pattern) != len(filt):
        raise ValueError("패턴과 필터의 길이가 같아야 합니다.")

    total = 0.0
    for index in range(len(pattern)):
        total += pattern[index] * filt[index]
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


def measure_mac_ms(pattern, filt, repeat=REPEAT, mac_func=mac):
    """지정한 MAC 함수를 반복 측정하고 평균 ms를 반환합니다."""
    elapsed = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        mac_func(pattern, filt)
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


def run_case(case_key, case, filters):
    """패턴 하나를 검사하고 점수, 판정, 성공 여부를 반환합니다."""
    result = {
        "case": case_key,
        "score_cross": None,
        "score_x": None,
        "predicted": "-",
        "expected": "-",
        "status": "FAIL",
        "reason": "",
    }

    try:
        n = parse_size_key(case_key, is_pattern=True)
        if not isinstance(case, dict) or not isinstance(filters, dict):
            raise ValueError("패턴과 필터 묶음은 객체여야 합니다.")

        expected = normalize_label(case["expected"])
        if expected is None:
            raise ValueError(f"알 수 없는 expected 라벨: {case['expected']!r}")
        result["expected"] = expected

        pattern = case["input"]
        pair = filters[f"size_{n}"]
        if not isinstance(pair, dict):
            raise ValueError("크기별 필터 묶음은 객체여야 합니다.")

        cross_filter = pair["cross"]
        x_filter = pair["x"]
        validate_matrix(pattern, n)
        validate_matrix(cross_filter, n)
        validate_matrix(x_filter, n)

        score_cross = mac(pattern, cross_filter)
        score_x = mac(pattern, x_filter)
        if not all(math.isfinite(v) for v in (score_cross, score_x)):
            raise OverflowError("MAC 계산 결과가 유한한 숫자가 아닙니다.")

        result["score_cross"] = score_cross
        result["score_x"] = score_x
        predicted = judge(score_cross, score_x, "Cross", "X")
        result["predicted"] = predicted

        if predicted == expected:
            result["status"] = "PASS"
        elif predicted == "UNDECIDED":
            result["reason"] = f"점수 차이가 {EPSILON:g} 미만이므로 판정 불가"
        else:
            result["reason"] = f"기대 정답 {expected}와 실제 판정 {predicted} 불일치"

    except KeyError as error:
        result["reason"] = f"데이터 오류: 필수 키 없음 {error}"
    except (ValueError, TypeError) as error:
        result["reason"] = f"데이터 오류: {error}"
    except OverflowError as error:
        result["reason"] = f"수치 계산 오류: {error}"

    return result


def print_json_performance(data, results):
    """크기별로 계산 가능한 첫 패턴과 Cross 필터의 시간을 측정합니다."""
    samples = {}
    for result in results:
        if result["score_cross"] is None or result["score_x"] is None:
            continue

        case_key = result["case"]
        n = parse_size_key(case_key, is_pattern=True)
        if n not in samples:
            samples[n] = case_key

    print(f"\n=== 성능 분석: {REPEAT}회 평균 ===")
    print("측정 대상: 크기별 첫 계산 가능 패턴과 Cross 필터의 MAC 함수 호출")
    print("크기(N×N) | 평균 시간(ms) | MAC 연산 횟수(N²) | 사용 패턴")

    for n in (5, 13, 25):
        if n not in samples:
            print(f"{n}x{n} | 측정 불가 | {n * n} | 계산 가능한 패턴 없음")
            continue

        case_key = samples[n]
        pattern = data["patterns"][case_key]["input"]
        cross_filter = data["filters"][f"size_{n}"]["cross"]
        average_ms = measure_mac_ms(pattern, cross_filter)
        print(f"{n}x{n} | {average_ms:.6f} | {n * n} | {case_key}")


def run_json_analysis(data=None):
    """각 케이스의 결과와 전체 통과·실패 수를 출력합니다."""
    try:
        if data is None:
            data = load_data()
        if not isinstance(data, dict):
            raise ValueError("JSON 최상위는 객체여야 합니다.")

        filters = data["filters"]
        patterns = data["patterns"]
        if not isinstance(filters, dict) or not isinstance(patterns, dict):
            raise ValueError("filters와 patterns는 객체여야 합니다.")
    except (OSError, ValueError, KeyError) as error:
        print(f"JSON 분석 시작 실패: {error}")
        return []

    results = []
    print("=== JSON 판정 결과 ===")
    print("케이스 | Cross 점수 | X 점수 | 판정 | expected | 결과")

    for case_key, case in patterns.items():
        result = run_case(case_key, case, filters)
        results.append(result)
        cross_text = "-" if result["score_cross"] is None else f"{result['score_cross']:.6f}"
        x_text = "-" if result["score_x"] is None else f"{result['score_x']:.6f}"
        print(
            f"{case_key} | {cross_text} | {x_text} | "
            f"{result['predicted']} | {result['expected']} | {result['status']}"
        )

    print_json_performance(data, results)

    print("\n=== 결과 요약 ===")
    passed = sum(result["status"] == "PASS" for result in results)
    print(f"\n전체: {len(results)} | PASS: {passed} | FAIL: {len(results) - passed}")
    for result in results:
        if result["status"] == "FAIL":
            print(f"- {result['case']}: {result['reason']}")

    return results


def run_generated_checks():
    """자동 생성 패턴의 모양, 점수, 계산 시간을 확인합니다."""
    print_matrix("자동 생성 3×3 십자가", generate_cross(3))
    print_matrix("자동 생성 3×3 X", generate_x(3))

    print(f"\n=== 자동 생성 패턴 검증 및 성능: {REPEAT}회 평균 ===")
    print("측정 대상: 자동 생성 X 패턴과 X 필터의 MAC 함수 호출")
    print("크기 | Cross/Cross | Cross/X | X/Cross | X/X | 평균 시간(ms) | N²")
    for n in (3, 5, 13, 25):
        cross = generate_cross(n)
        x_pattern = generate_x(n)
        cc = mac(cross, cross)
        cx = mac(cross, x_pattern)
        xc = mac(x_pattern, cross)
        xx = mac(x_pattern, x_pattern)
        average_ms = measure_mac_ms(x_pattern, x_pattern)
        print(
            f"{n}x{n} | {cc:g} | {cx:g} | {xc:g} | {xx:g} | "
            f"{average_ms:.6f} | {n * n}"
        )

def run_layout_comparison():
    """동일한 X 패턴·필터로 2차원과 1차원 MAC을 비교합니다."""
    print(f"=== 2차원·1차원 MAC 비교: 각 {REPEAT}회 평균 ===")
    print("측정 대상: 자동 생성 X 패턴과 X 필터, 배열 생성·변환 시간 제외")
    print("크기 | 2D 점수 | 1D 점수 | 점수 차이 | 비교 | 2D(ms) | 1D(ms) | 2D/1D")

    for n in (3, 5, 13, 25):
        pattern = generate_x(n)
        filt = generate_x(n)
        flat_pattern = flatten_matrix(pattern)
        flat_filter = flatten_matrix(filt)

        score_2d = mac(pattern, filt)
        score_1d = mac_1d(flat_pattern, flat_filter)
        difference = abs(score_2d - score_1d)
        status = "PASS" if difference < EPSILON else "FAIL"

        time_2d = measure_mac_ms(pattern, filt, mac_func=mac)
        time_1d = measure_mac_ms(flat_pattern, flat_filter, mac_func=mac_1d)
        ratio = f"{time_2d / time_1d:.2f}" if time_1d > 0 else "-"

        print(
            f"{n}x{n} | {score_2d:g} | {score_1d:g} | {difference:.3g} | "
            f"{status} | {time_2d:.6f} | {time_1d:.6f} | {ratio}"
        )

def run_input_mode():
    print("=== Mini NPU Simulator: 사용자 입력 모드 ===")

    print("1. 필터 A와 B 직접 입력")
    print("2. 기본 필터 자동 생성 (A: 십자가, B: X)")
    while True:
        choice = input("필터 준비 방법을 선택하세요 (1 또는 2): ").strip()
        if choice == "1":
            filter_a = read_matrix("필터 A")
            filter_b = read_matrix("필터 B")
            break
        if choice == "2":
            filter_a = generate_cross(3)
            filter_b = generate_x(3)
            break
        print("입력 오류: 1 또는 2를 입력하세요.")

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
    print("\n=== 결과 요약 ===")
    label = "판정 불가" if result == "UNDECIDED" else result
    print(f"A 점수: {score_a:g} | B 점수: {score_b:g} | 최종 판정: {label}")
    print("사용자 입력 모드는 기대 정답이 없어 PASS/FAIL을 집계하지 않습니다.")


def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 모드 (3×3)")
    print("2. data.json 분석 모드 (5×5, 13×13, 25×25)")

    while True:
        choice = input("모드를 선택하세요 (1 또는 2): ").strip()
        if choice == "1":
            run_input_mode()
            break
        if choice == "2":
            run_json_analysis()
            break
        print("입력 오류: 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()

    