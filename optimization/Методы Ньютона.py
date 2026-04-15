example = 1

def fmt_vec(v, digits=6):
    return "(" + ", ".join(f"{value:.{digits}f}" for value in v) + ")"


def f0(x):
    """Целевая функция: f(x) = 8x₁² + x₂² - x₁x₂ + x₁"""
    x1, x2 = x[0], x[1]
    return 8 * x1 * x1 + x2 * x2 - x1 * x2 + x1


def f1(x):
    x1, x2 = x[0], x[1]
    return (x1 + 2 * x2 - 5) ** 4 + (x2 - 2) ** 2


def f2(x):
    x1, x2, x3 = x[0], x[1], x[2]
    return (x1 + 2 * x2 - 5) ** 4 + (x2 - 2) ** 2 + (x1 + 2 * x2 + x3 - 7) ** 2


def grad_f0(x):
    x1, x2 = x[0], x[1]
    df_dx1 = 16 * x1 - x2 + 1
    df_dx2 = 2 * x2 - x1
    return [df_dx1, df_dx2]


def grad_f1(x):
    x1, x2 = x[0], x[1]
    a = x1 + 2 * x2 - 5
    df_dx1 = 4 * a ** 3
    df_dx2 = 8 * a ** 3 + 2 * (x2 - 2)
    return [df_dx1, df_dx2]


def grad_f2(x):
    x1, x2, x3 = x[0], x[1], x[2]
    a = x1 + 2 * x2 - 5
    b = x1 + 2 * x2 + x3 - 7
    df_dx1 = 4 * a ** 3 + 2 * b
    df_dx2 = 8 * a ** 3 + 2 * (x2 - 2) + 4 * b
    df_dx3 = 2 * b
    return [df_dx1, df_dx2, df_dx3]


def hessian_f(x):
    """Гессиан для f0"""
    return [[16, -1],
            [-1, 2]]


def hessian_f1(x):
    x1, x2 = x[0], x[1]
    common = 12 * (x1 + 2 * x2 - 5) ** 2
    h11 = common
    h12 = 2 * common
    h21 = 2 * common
    h22 = 4 * common + 2
    return [[h11, h12],
            [h21, h22]]


def hessian_f2(x):
    x1, x2, x3 = x[0], x[1], x[2]
    a = x1 + 2 * x2 - 5
    common = 12 * a * a

    h11 = common + 2
    h12 = 2 * common + 4
    h13 = 2

    h21 = 2 * common + 4
    h22 = 4 * common + 10
    h23 = 4

    h31 = 2
    h32 = 4
    h33 = 2

    return [[h11, h12, h13],
            [h21, h22, h23],
            [h31, h32, h33]]


def f(x):
    if example == 0:
        return f0(x)
    elif example == 1:
        return f1(x)
    else:
        return f2(x)


def grad_f(x):
    if example == 0:
        return grad_f0(x)
    elif example == 1:
        return grad_f1(x)
    else:
        return grad_f2(x)


def hessian(x):
    if example == 0:
        return hessian_f(x)
    elif example == 1:
        return hessian_f1(x)
    else:
        return hessian_f2(x)


def vec_norm(v):
    return sum(value * value for value in v) ** 0.5


def vec_dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def vec_add(a, b):
    return [x + y for x, y in zip(a, b)]


def vec_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def vec_scale(v, k):
    return [x * k for x in v]


def mat_vec_mul(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


def matrix_determinant(M):
    A = [row[:] for row in M]
    n = len(A)
    det_sign = 1.0
    det = 1.0

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(A[r][col]))
        pivot = A[pivot_row][col]

        if abs(pivot) < 1e-12:
            return 0.0

        if pivot_row != col:
            A[col], A[pivot_row] = A[pivot_row], A[col]
            det_sign *= -1.0

        pivot = A[col][col]
        det *= pivot

        for row in range(col + 1, n):
            factor = A[row][col] / pivot
            if factor == 0:
                continue
            for j in range(col, n):
                A[row][j] -= factor * A[col][j]

    return det_sign * det


def matrix_inverse_manual(H):
    """
    Универсальное обращение матрицы методом Гаусса-Жордана.
    Работает для 2x2, 3x3 и вообще для квадратных матриц.
    """
    n = len(H)
    A = [row[:] for row in H]
    I = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(A[r][col]))
        pivot = A[pivot_row][col]

        if abs(pivot) < 1e-12:
            raise ValueError("Матрица вырожденная (определитель близок к нулю)")

        if pivot_row != col:
            A[col], A[pivot_row] = A[pivot_row], A[col]
            I[col], I[pivot_row] = I[pivot_row], I[col]

        pivot = A[col][col]
        for j in range(n):
            A[col][j] /= pivot
            I[col][j] /= pivot

        for row in range(n):
            if row == col:
                continue
            factor = A[row][col]
            if factor == 0:
                continue
            for j in range(n):
                A[row][j] -= factor * A[col][j]
                I[row][j] -= factor * I[col][j]

    return I


def check_hessian_positive(H):
    """
    Критерий Сильвестра для матрицы любого размера:
    все ведущие главные миноры должны быть положительными.
    """
    n = len(H)
    minors = []

    for k in range(1, n + 1):
        submatrix = [row[:k] for row in H[:k]]
        minors.append(matrix_determinant(submatrix))

    print("  Миноры: " + ", ".join(
        f"Δ{i + 1} = {minor:.6f}" for i, minor in enumerate(minors)
    ))

    return all(minor > 0 for minor in minors)


def newton_method(x, eps1=0.1, eps2=0.15, M=10):
    k = 0
    small_step_flag = False

    print(f"\n{'='*60}")
    print(f"МЕТОД НЬЮТОНА")
    print(f"{'='*60}")
    print(f"Начальная точка: x⁰ = {fmt_vec(x, 3)}")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}\n")

    while k < M:
        grad = grad_f(x)
        grad_norm = vec_norm(grad)

        print(f"Итерация {k}:")
        print(f"  x^{k} = {fmt_vec(x, 6)}")
        print(f"  f(x^{k}) = {f(x):.6f}")
        print(f"  ∇f(x^{k}) = {fmt_vec(grad, 6)}")
        print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

        if grad_norm < eps1:
            print(f"  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен.")
            return x

        H = hessian(x)
        print(f"  H(x^{k}) = {H}")

        try:
            H_inv = matrix_inverse_manual(H)
            print(f"  H⁻¹(x^{k}) = {H_inv}")
        except ValueError as e:
            print(f"  ✗ Ошибка: {e}")
            break

        is_positive = check_hessian_positive(H)

        if is_positive:
            print(f"  ✓ H > 0 (положительно определена)")
            d = vec_scale(mat_vec_mul(H_inv, grad), -1.0)
            t_k = 1.0
            print(f"  d^{k} = -H⁻¹∇f = {fmt_vec(d, 6)}")
            print(f"  t_{k} = 1")
        else:
            print(f"  ✗ H не является положительно определенной")
            d = vec_scale(grad, -1.0)
            t_k = 1.0
            print(f"  d^{k} = -∇f = {fmt_vec(d, 6)}")
            print(f"  Переход к поиску шага")

        x_new = vec_add(x, vec_scale(d, t_k))
        f_old = f(x)
        f_new = f(x_new)

        division_count = 0
        while f_new >= f_old and division_count < 20:
            t_k /= 2.0
            x_new = vec_add(x, vec_scale(d, t_k))
            f_new = f(x_new)
            division_count += 1
            print(f"  Деление шага: t_{k} = {t_k:.6f}, f(x^{{k+1}}) = {f_new:.6f}")

        print(f"  x^{k+1} = {fmt_vec(x_new, 6)}")

        x_diff = vec_norm(vec_sub(x_new, x))
        f_diff = abs(f_new - f_old)

        print(f"  ‖x^{k+1} - x^{k}‖ = {x_diff:.6f}")
        print(f"  |f(x^{k+1}) - f(x^{k})| = {f_diff:.6f}")

        if x_diff < eps2 and f_diff < eps2:
            if small_step_flag:
                print(f"  ✓ Условия выполнены два раза подряд. Расчет окончен.")
                return x_new
            small_step_flag = True
        else:
            small_step_flag = False

        x = x_new
        k += 1
        print()

    print(f"\nДостигнуто максимальное число итераций M = {M}")
    return x

def newton_raphson_method(x, eps1=0.1, eps2=0.15, M=10):
    k = 0
    small_step_flag = False

    print(f"\n{'='*60}")
    print(f"МЕТОД НЬЮТОНА-РАФСОНА")
    print(f"{'='*60}")
    print(f"Начальная точка: x⁰ = {fmt_vec(x, 3)}")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}\n")

    while k < M:
        grad = grad_f(x)
        grad_norm = vec_norm(grad)

        print(f"Итерация {k}:")
        print(f"  x^{k} = {fmt_vec(x, 6)}")
        print(f"  f(x^{k}) = {f(x):.6f}")
        print(f"  ∇f(x^{k}) = {fmt_vec(grad, 6)}")
        print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

        if grad_norm < eps1:
            print(f"  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен.")
            return x

        H = hessian(x)
        print(f"  H(x^{k}) = {H}")

        try:
            H_inv = matrix_inverse_manual(H)
            print(f"  H⁻¹(x^{k}) = {H_inv}")
        except ValueError as e:
            print(f"  ✗ Ошибка: {e}")
            break

        is_positive = check_hessian_positive(H)

        if is_positive:
            print(f"  ✓ H > 0 (положительно определена)")
            d = vec_scale(mat_vec_mul(H_inv, grad), -1.0)
            print(f"  d^{k} = -H⁻¹∇f = {fmt_vec(d, 6)}")
        else:
            print(f"  ✗ H не является положительно определенной")
            d = vec_scale(grad, -1.0)
            print(f"  d^{k} = -∇f = {fmt_vec(d, 6)}")

        print(f"  Поиск оптимального шага t* (адаптивный: Свенн + золотое сечение)...")

        def phi(t):
            return f(vec_add(x, vec_scale(d, t)))

        t0 = 0.0
        h = 0.1
        max_step = 100.0

        if phi(t0 + h) < phi(t0):
            t_prev = t0
            t_curr = t0 + h
            step = h
            while True:
                t_next = min(t_curr + step, max_step)
                if phi(t_next) < phi(t_curr):
                    t_prev = t_curr
                    t_curr = t_next
                    step *= 2
                else:
                    break
            a, b = t_prev, t_next
        else:
            a, b = t0, t0 + h

        if abs(b - a) < 1e-8:
            b = a + 1.0

        eps = 1e-4
        gr = (5 ** 0.5 - 1) / 2

        x1 = b - gr * (b - a)
        x2 = a + gr * (b - a)

        f1_val = phi(x1)
        f2_val = phi(x2)

        while abs(b - a) > eps:
            if f1_val < f2_val:
                b = x2
                x2 = x1
                f2_val = f1_val
                x1 = b - gr * (b - a)
                f1_val = phi(x1)
            else:
                a = x1
                x1 = x2
                f1_val = f2_val
                x2 = a + gr * (b - a)
                f2_val = phi(x2)

        t_k = (a + b) / 2.0

        print(f"  t_{k}* = {t_k:.6f} (интервал поиска = [{a:.4f}, {b:.4f}])")

        x_new = vec_add(x, vec_scale(d, t_k))
        f_old = f(x)
        f_new = f(x_new)

        print(f"  x^{k+1} = {fmt_vec(x_new, 6)}")
        print(f"  f(x^{k+1}) = {f_new:.6f}")

        x_diff = vec_norm(vec_sub(x_new, x))
        f_diff = abs(f_new - f_old)

        print(f"  ‖x^{k+1} - x^{k}‖ = {x_diff:.6f}")
        print(f"  |f(x^{k+1}) - f(x^{k})| = {f_diff:.6f}")

        if x_diff < eps2 and f_diff < eps2:
            if small_step_flag:
                print(f"  ✓ Условия выполнены два раза подряд. Расчет окончен.")
                return x_new
            small_step_flag = True
        else:
            small_step_flag = False

        x = x_new
        k += 1
        print()

    print(f"\nДостигнуто максимальное число итераций M = {M}")
    return x

def main():
    x0 = [2.0, 2.0, 2.0] if example == 2 else [2.0, 2.0]
    eps1 = 0.1
    eps2 = 0.15
    M = 10

    task_title = {
        0: "f(x) = 8x₁² + x₂² - x₁x₂ + x₁",
        1: "f(x) = (x₁ + 2x₂ - 5)⁴ + (x₂ - 2)²",
        2: "f(x) = (x₁ + 2x₂ - 5)⁴ + (x₂ - 2)² + (x₁ + 2x₂ + x₃ - 7)²",
    }.get(example, "f(x)")

    print("\n" + "=" * 60)
    print(f"РЕШЕНИЕ ЗАДАЧИ 10: {task_title}, x₀ = {fmt_vec(x0, 3)}")
    print("=" * 60)

    x_newton = newton_method(x0, eps1, eps2, M)

    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТ МЕТОДА НЬЮТОНА:")
    print(f"{'='*60}")
    print(f"Найденная точка: x* = {fmt_vec(x_newton, 6)}")
    print(f"Значение функции: f(x*) = {f(x_newton):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {vec_norm(grad_f(x_newton)):.6f}")

    x_nr = newton_raphson_method(x0, eps1, eps2, M)

    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТ МЕТОДА НЬЮТОНА-РАФСОНА:")
    print(f"{'='*60}")
    print(f"Найденная точка: x* = {fmt_vec(x_nr, 6)}")
    print(f"Значение функции: f(x*) = {f(x_nr):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {vec_norm(grad_f(x_nr)):.6f}")

    print(f"\n{'='*60}")
    print(f"АНАЛИЗ ТОЧКИ МИНИМУМА:")
    print(f"{'='*60}")
    H = hessian(x_newton)
    print(f"Матрица Гессе в найденной точке:")
    print(H)
    if check_hessian_positive(H):
        print("✓ Точка является локальным минимумом (H > 0)")
    else:
        print("✗ Необходима дополнительная проверка")


if __name__ == "__main__":
    main()