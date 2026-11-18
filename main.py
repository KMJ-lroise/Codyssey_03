import math

EPSILON = 1e-9

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


if __name__ == "__main__":
    main()

    