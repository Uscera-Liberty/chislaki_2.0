import math

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def norm(v):
    return sum(x*x for x in v) ** 0.5

def vec_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(len(a))]

def vec_mul_scalar(v, s):
    return [v[i] * s for i in range(len(v))]

def dot(a, b):
    return sum(a[i]*b[i] for i in range(len(a)))

def mat_vec(A, v):
    return [sum(A[i][j]*v[j] for j in range(len(v))) for i in range(len(A))]

def outer(v1, v2):
    return [[v1[i]*v2[j] for j in range(len(v2))] for i in range(len(v1))]

def mat_add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A))] for i in range(len(A))]

def mat_sub(A, B):
    return [[A[i][j] - B[i][j] for j in range(len(A))] for i in range(len(A))]

def mat_mul_scalar(A, s):
    return [[A[i][j]*s for j in range(len(A))] for i in range(len(A))]

def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


# ===== ФУНКЦИЯ =====

def f(x):
    return 8*x[0]**2 + x[1]**2 - x[0]*x[1] + x[0]


def numerical_gradient(x, h=1e-8):
    n = len(x)
    grad = [0.0]*n

    for i in range(n):
        x_plus = x[:]
        x_minus = x[:]
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2*h)

    return grad


def svenn_method(x, d, t0=0.0, delta=0.01):
    """
    Метод Свенна для поиска начального интервала локализации минимума
    Возвращает интервал [a, b], содержащий минимум функции φ(t) = f(x + t*d)
    """
    def phi(t):
        return f(vec_add(x, vec_mul_scalar(d, t)))
    
    t = t0
    h = delta
    
    # Определяем направление поиска
    f_t = phi(t)
    f_t_plus_h = phi(t + h)
    
    if f_t_plus_h > f_t:
        h = -h
        t_prev = t + h
        t = t0
    else:
        t_prev = t
        t = t + h
    
    # Удваиваем шаг до выхода за минимум
    k = 0
    while True:
        t_new = t + 2**k * h
        f_new = phi(t_new)
        f_curr = phi(t)
        
        if f_new > f_curr:
            break
        
        t_prev = t
        t = t_new
        k += 1
        
        if k > 100:  # Защита от бесконечного цикла
            break
    
    # Возвращаем упорядоченный интервал
    if t_prev < t:
        return t_prev, t
    else:
        return t, t_prev


def golden_section_search(x, d, tol=1e-5):
    """
    Поиск оптимального шага методом золотого сечения
    Сначала находим начальный интервал методом Свенна
    """
    # Находим начальный интервал методом Свенна
    a, b = svenn_method(x, d)
    
    phi_const = (math.sqrt(5) - 1)/2

    def phi(t):
        return f(vec_add(x, vec_mul_scalar(d, t)))

    x1 = b - phi_const*(b-a)
    x2 = a + phi_const*(b-a)
    f1 = phi(x1)
    f2 = phi(x2)

    while abs(b-a) > tol:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - phi_const*(b-a)
            f1 = phi(x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + phi_const*(b-a)
            f2 = phi(x2)

    return (a+b)/2


# ===== ФЛЕТЧЕР-РИВС =====

def fletcher_reeves_method(x0, eps1=0.1, eps2=0.15, M=10):
    n = len(x0)
    x = x0[:]
    k = 0
    converged_twice = False

    print("\n" + "="*70)
    print("МЕТОД ФЛЕТЧЕРА-РИВСА")
    print("="*70)
    print(f"Начальная точка: x⁰ = ({x[0]:.3f}, {x[1]:.3f})")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}")
    print(f"Размерность задачи: n = {n}\n")

    grad = numerical_gradient(x)
    grad_norm = norm(grad)

    print(f"Итерация {k}:")
    print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
    print(f"  f(x^{k}) = {f(x):.6f}")
    print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
    print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

    if grad_norm < eps1:
        print("  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен.")
        return x

    d = vec_mul_scalar(grad, -1)
    print(f"  d^{k} = -∇f(x^{k}) = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")

    grad_prev = grad[:]

    while k < M:
        t_k = golden_section_search(x, d)
        print(f"  t_{k}* = {t_k:.6f}")

        x_old = x[:]
        f_old = f(x)

        x = vec_add(x, vec_mul_scalar(d, t_k))
        f_new = f(x)

        k += 1

        print(f"\nИтерация {k}:")
        print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
        print(f"  f(x^{k}) = {f_new:.6f}")

        x_diff = norm(vec_sub(x, x_old))
        f_diff = abs(f_new - f_old)

        print(f"  ‖x^{k} - x^{k-1}‖ = {x_diff:.6f}")
        print(f"  |f(x^{k}) - f(x^{k-1})| = {f_diff:.6f}")

        if x_diff < eps2 and f_diff < eps2:
            if converged_twice:
                print("  ✓ Условия выполнены в двух последовательных итерациях. Расчет окончен.")
                return x
            else:
                converged_twice = True
        else:
            converged_twice = False

        if k >= M:
            print(f"\n  Достигнуто предельное число итераций M = {M}")
            break

        grad = numerical_gradient(x)
        grad_norm = norm(grad)

        print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
        print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

        if grad_norm < eps1:
            print(f"  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен")
            return x

        grad_norm_prev = norm(grad_prev)

        if k % n == 0:
            beta = 0.0
            print(f"  k = {k} ∈ J, β = 0")
        else:
            beta = (grad_norm**2)/(grad_norm_prev**2) if grad_norm_prev > 1e-10 else 0.0
            print(f"  β = {beta:.6f}")

        d = vec_add(vec_mul_scalar(grad, -1), vec_mul_scalar(d, beta))
        print(f"  d^{k} = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")

        grad_prev = grad[:]
        print()

    return x


# ===== DFP =====

def davidon_fletcher_powell_method(x0, eps1=0.1, eps2=0.15, M=10):
    n = len(x0)
    x = x0[:]
    k = 0
    converged_twice = False

    print("\n" + "="*70)
    print("МЕТОД ДЭВИДОНА-ФЛЕТЧЕРА-ПАУЭЛЛА")
    print("="*70)
    print(f"Начальная точка: x⁰ = ({x[0]:.3f}, {x[1]:.3f})")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}")
    print(f"Размерность задачи: n = {n}\n")

    A = identity(n)

    print(f"Итерация {k}:")
    print(f"  A^{k} = E (единичная матрица)")
    for row in A:
        print(f"    {row}")

    grad = numerical_gradient(x)
    grad_norm = norm(grad)

    print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
    print(f"  f(x^{k}) = {f(x):.6f}")
    print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
    print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

    if grad_norm < eps1:
        print("  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен.")
        return x

    while k < M:
        d = vec_mul_scalar(mat_vec(A, grad), -1)
        print(f"  d^{k} = -A^{k}·∇f(x^{k}) = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")

        t_k = golden_section_search(x, d)
        print(f"  t_{k}* = {t_k:.6f}")

        x_old = x[:]
        f_old = f(x)
        grad_old = grad[:]

        x = vec_add(x, vec_mul_scalar(d, t_k))
        f_new = f(x)

        k += 1

        print(f"\nИтерация {k}:")
        print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
        print(f"  f(x^{k}) = {f_new:.6f}")

        x_diff = norm(vec_sub(x, x_old))
        f_diff = abs(f_new - f_old)

        print(f"  ‖x^{k} - x^{k-1}‖ = {x_diff:.6f}")
        print(f"  |f(x^{k}) - f(x^{k-1})| = {f_diff:.6f}")

        if x_diff < eps2 and f_diff < eps2:
            if converged_twice:
                print("  ✓ Условия выполнены в двух последовательных итерациях. Расчет окончен.")
                return x
            else:
                converged_twice = True
        else:
            converged_twice = False

        if k >= M:
            print(f"\n  Достигнуто предельное число итераций M = {M}")
            break

        grad = numerical_gradient(x)
        grad_norm = norm(grad)

        print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
        print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

        if grad_norm < eps1:
            print(f"  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен")
            return x

        delta_g = vec_sub(grad, grad_old)
        delta_x = vec_sub(x, x_old)

        print(f"  Δg^{k-1} = ∇f(x^{k}) - ∇f(x^{k-1}) = [{delta_g[0]:.6f}, {delta_g[1]:.6f}]ᵀ")
        print(f"  Δx^{k-1} = x^{k} - x^{k-1} = [{delta_x[0]:.6f}, {delta_x[1]:.6f}]ᵀ")

        # Вычисление A^k_c
        denom1 = dot(delta_x, delta_g)
        if abs(denom1) < 1e-10:
            print(f"  ⚠ (Δx)ᵀ·Δg ≈ 0, пропускаем обновление матрицы")
            print()
            continue

        term1 = mat_mul_scalar(outer(delta_x, delta_x), 1.0/denom1)

        A_delta_g = mat_vec(A, delta_g)
        denom2 = dot(delta_g, A_delta_g)
        
        if abs(denom2) < 1e-10:
            print(f"  ⚠ (Δg)ᵀ·A·Δg ≈ 0, пропускаем обновление матрицы")
            print()
            continue

        term2 = mat_mul_scalar(outer(A_delta_g, A_delta_g), 1.0/denom2)

        A_c = mat_sub(term1, term2)

        print(f"  A^{k-1}_c вычислена:")
        print(f"    (Δx)ᵀ·Δg = {denom1:.6f}")
        print(f"    (Δg)ᵀ·A·Δg = {denom2:.6f}")

        A = mat_add(A, A_c)

        print(f"  A^{k} = A^{k-1} + A^{k-1}_c =")
        for row in A:
            print(f"    [{row[0]:9.6f}, {row[1]:9.6f}]")
        print()

    return x


# ===== MAIN =====

def main():
    x0 = [2.0, 2.0]

    print("\n" + "="*70)
    print("РЕШЕНИЕ ЗАДАЧИ 10: f(x) = 8x₁² + x₂² - x₁x₂ + x₁, x₀ = (2, 2)")
    print("="*70)

    x_fr = fletcher_reeves_method(x0)
    
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТ МЕТОДА ФЛЕТЧЕРА-РИВСА:")
    print("="*70)
    print(f"Найденная точка: x* = [{x_fr[0]:.6f}, {x_fr[1]:.6f}]ᵀ")
    print(f"Значение функции: f(x*) = {f(x_fr):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {norm(numerical_gradient(x_fr)):.6f}")

    x_dfp = davidon_fletcher_powell_method(x0)
    
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТ МЕТОДА ДЭВИДОНА-ФЛЕТЧЕРА-ПАУЭЛЛА:")
    print("="*70)
    print(f"Найденная точка: x* = [{x_dfp[0]:.6f}, {x_dfp[1]:.6f}]ᵀ")
    print(f"Значение функции: f(x*) = {f(x_dfp):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {norm(numerical_gradient(x_dfp)):.6f}")

    # Точное решение
    x1_exact = -2/31
    x2_exact = -1/31
    
    print(f"\n{'='*70}")
    print("ТОЧНОЕ РЕШЕНИЕ (аналитическое):")
    print(f"x* = [{x1_exact:.6f}, {x2_exact:.6f}]ᵀ")
    print(f"f(x*) = {f([x1_exact, x2_exact]):.6f}")
    
    diff_fr = norm(vec_sub(x_fr, [x1_exact, x2_exact]))
    diff_dfp = norm(vec_sub(x_dfp, [x1_exact, x2_exact]))
    
    print(f"\nПогрешность метода Флетчера-Ривса: ‖x_FR - x_exact‖ = {diff_fr:.6f}")
    print(f"Погрешность метода Дэвидона-Флетчера-Пауэлла: ‖x_DFP - x_exact‖ = {diff_dfp:.6f}")


if __name__ == "__main__":
    main()