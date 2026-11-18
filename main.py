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


def main():
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


if __name__ == "__main__":
    main()