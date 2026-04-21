import math

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def f(x):
    """Целевая функция: f(x) = 8x₁² + x₂² - x₁x₂ + x₁"""
    return 8*x[0]**2 + x[1]**2 - x[0]*x[1] + x[0]

def norm(v):
    """Вычисление нормы вектора"""
    return (sum(vi**2 for vi in v))**0.5

def vec_sub(a, b):
    """Вычитание векторов a - b"""
    return [a[i] - b[i] for i in range(len(a))]

def vec_add(a, b):
    """Сложение векторов a + b"""
    return [a[i] + b[i] for i in range(len(a))]

def vec_mul_scalar(v, t):
    """Умножение вектора на скаляр"""
    return [vi * t for vi in v]

def mat_vec(A, v):
    """Умножение матрицы на вектор"""
    return [sum(A[i][j]*v[j] for j in range(len(v))) for i in range(len(A))]

def mat_add(A, B):
    """Сложение матриц A + B"""
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def mat_mul_scalar(A, t):
    """Умножение матрицы на скаляр"""
    n = len(A)
    return [[A[i][j] * t for j in range(n)] for i in range(n)]

def identity(n):
    """Создание единичной матрицы размера n×n"""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def numerical_gradient(x, h=1e-8):
    """
    Численное вычисление градиента методом центральных разностей
    ∂f/∂xᵢ ≈ (f(x + h·eᵢ) - f(x - h·eᵢ)) / (2h)
    """
    n = len(x)
    grad = [0.0] * n
    
    for i in range(n):
        x_plus = x[:]
        x_minus = x[:]
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
    
    return grad

def hessian_matrix(x):
    """Матрица Гессе для функции f(x) = 8x₁² + x₂² - x₁x₂ + x₁"""
    return [[16.0, -1.0], [-1.0, 2.0]]

def matrix_inverse_2x2(H):
    """
    Вычисление обратной матрицы 2×2
    A⁻¹ = (1/det) * [[d, -b], [-c, a]]
    """
    det = H[0][0] * H[1][1] - H[0][1] * H[1][0]
    
    if abs(det) < 1e-10:
        raise ValueError("Матрица вырожденная")
    
    return [[H[1][1] / det, -H[0][1] / det],
            [-H[1][0] / det, H[0][0] / det]]

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
    
    x1 = b - phi_const * (b - a)
    x2 = a + phi_const * (b - a)
    f1 = phi(x1)
    f2 = phi(x2)
    
    while abs(b - a) > tol:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - phi_const * (b - a)
            f1 = phi(x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + phi_const * (b - a)
            f2 = phi(x2)
    
    return (a + b) / 2


def powell_method(x0, eps1=0.1, eps2=0.15, M=10):
    """
    Метод Пауэлла (метод сопряженных направлений)
    """
    n = len(x0)
    x = x0[:]
    k = 0
    converged_twice = False
    
    print("\n" + "="*70)
    print("МЕТОД ПАУЭЛЛА (МЕТОД СОПРЯЖЕННЫХ НАПРАВЛЕНИЙ)")
    print("="*70)
    print(f"Начальная точка: x⁰ = ({x[0]:.3f}, {x[1]:.3f})")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}")
    print(f"Размерность задачи: n = {n}\n")
    
    # Инициализация: используем базисные векторы как начальные направления
    directions = [[1.0, 0.0], [0.0, 1.0]]  # e₁, e₂
    
    print(f"Начальные направления:")
    for i, d in enumerate(directions):
        print(f"  d^{i} = [{d[0]:.1f}, {d[1]:.1f}]ᵀ")
    print()
    
    while k < M:
        print(f"ЦИКЛ {k}:")
        print(f"  x_начало = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
        print(f"  f(x_начало) = {f(x):.6f}")
        
        x_start = x[:]  # Сохраняем начальную точку цикла
        
        # Выполняем n одномерных минимизаций вдоль текущих направлений
        for i in range(n):
            d = directions[i]
            
            print(f"\n  Шаг {i+1}: Минимизация вдоль d^{i} = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")
            
            # Находим оптимальный шаг вдоль направления d
            t_opt = golden_section_search(x, d)
            
            # Обновляем точку
            x = vec_add(x, vec_mul_scalar(d, t_opt))
            
            print(f"    t_{i}* = {t_opt:.6f}")
            print(f"    x_{i+1} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
            print(f"    f(x_{i+1}) = {f(x):.6f}")
        
        # Формируем новое направление: v = x_конец - x_начало
        v = vec_sub(x, x_start)
        v_norm = norm(v)
        
        print(f"\n  Новое направление v = x_конец - x_начало:")
        print(f"  v = [{v[0]:.6f}, {v[1]:.6f}]ᵀ")
        print(f"  ‖v‖ = {v_norm:.6f}")
        
        # Проверка условия окончания
        grad = numerical_gradient(x)
        grad_norm = norm(grad)
        
        print(f"\n  ∇f(x) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
        print(f"  ‖∇f(x)‖ = {grad_norm:.6f}")
        
        if grad_norm < eps1:
            print(f"\n  ✓ ‖∇f(x)‖ < ε₁. Расчет окончен.")
            print(f"  Найдена точка x* = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
            return x
        
        x_diff = norm(vec_sub(x, x_start))
        f_diff = abs(f(x) - f(x_start))
        
        print(f"  ‖x_конец - x_начало‖ = {x_diff:.6f}")
        print(f"  |f(x_конец) - f(x_начало)| = {f_diff:.6f}")
        
        if x_diff < eps2 and f_diff < eps2:
            if converged_twice:
                print(f"\n  ✓ Условия выполнены в двух последовательных циклах")
                print(f"  Расчет окончен. Найдена точка x* = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
                return x
            else:
                converged_twice = True
        else:
            converged_twice = False
        
        # Если направление v не нулевое, выполняем минимизацию вдоль v
        if v_norm > 1e-10:
            print(f"\n  Минимизация вдоль нового направления v:")
            
            t_opt = golden_section_search(x, v)
            x = vec_add(x, vec_mul_scalar(v, t_opt))
            
            print(f"    t* = {t_opt:.6f}")
            print(f"    x_новое = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
            print(f"    f(x_новое) = {f(x):.6f}")
            
            # Обновляем набор направлений: заменяем первое направление на v
            directions = [v] + directions[:-1]
            
            print(f"\n  Обновленные направления:")
            for i, d in enumerate(directions):
                print(f"    d^{i} = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")
        
        k += 1
        print()
    
    print(f"\nДостигнуто максимальное число итераций M = {M}")
    return x


def marquardt_method(x0, eps1=0.1, M=10, mu0=1.0):
    """
    Метод Марквардта согласно алгоритму из презентации (стр. 25)
    """
    n = len(x0)
    x = x0[:]
    k = 0
    mu = mu0
    
    print("\n" + "="*70)
    print("МЕТОД МАРКВАРДТА")
    print("="*70)
    print(f"Начальная точка: x⁰ = ({x[0]:.3f}, {x[1]:.3f})")
    print(f"ε₁ = {eps1}, M = {M}")
    print(f"μ⁰ = {mu0}")
    print(f"Размерность задачи: n = {n}\n")
    
    # Шаг 2: Положить k = 0, μ^k = μ⁰
    print(f"Итерация {k}:")
    print(f"  μ^{k} = {mu:.3f}")
    
    while k < M:
        # Шаг 3: Вычислить ∇f(x^k)
        grad = numerical_gradient(x)
        grad_norm = norm(grad)
        
        print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
        print(f"  f(x^{k}) = {f(x):.6f}")
        print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
        print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")
        
        # Шаг 4: Проверка критерия окончания
        if grad_norm < eps1:
            print(f"\n  ✓ ‖∇f(x^{k})‖ < ε₁. Расчет окончен.")
            print(f"  Найдена точка x* = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
            return x
        
        # Шаг 5: Проверка k ≥ M
        if k >= M:
            print(f"\n  Достигнуто предельное число итераций M = {M}")
            break
        
        # Шаг 6: Вычислить H(x^k)
        H = hessian_matrix(x)
        print(f"  H(x^{k}) = [[{H[0][0]:.1f}, {H[0][1]:.1f}], [{H[1][0]:.1f}, {H[1][1]:.1f}]]")
        
        while True:  # Внутренний цикл для подбора μ
            # Шаг 7: Вычислить H(x^k) + μ^k·E
            E = identity(n)
            H_mu = mat_add(H, mat_mul_scalar(E, mu))
            
            print(f"\n  μ^{k} = {mu:.6f}")
            print(f"  H(x^{k}) + μ^{k}·E = [[{H_mu[0][0]:.6f}, {H_mu[0][1]:.6f}], "
                  f"[{H_mu[1][0]:.6f}, {H_mu[1][1]:.6f}]]")
            
            # Шаг 8: Найти обратную матрицу [H(x^k) + μ^k·E]⁻¹
            try:
                H_mu_inv = matrix_inverse_2x2(H_mu)
                print(f"  [H(x^{k}) + μ^{k}·E]⁻¹ = [[{H_mu_inv[0][0]:.6f}, {H_mu_inv[0][1]:.6f}], "
                      f"[{H_mu_inv[1][0]:.6f}, {H_mu_inv[1][1]:.6f}]]")
            except ValueError as e:
                print(f"  ✗ Ошибка: {e}")
                mu = mu * 2
                print(f"  Увеличиваем μ: μ^{k} = {mu:.6f}")
                continue
            
            # Шаг 9: Вычислить d^k = -[H(x^k) + μ^k·E]⁻¹·∇f(x^k)
            d = vec_mul_scalar(mat_vec(H_mu_inv, grad), -1.0)
            print(f"  d^{k} = -[H + μE]⁻¹·∇f = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")
            
            # Шаг 10: Вычислить x^(k+1) = x^k + d^k
            x_new = vec_add(x, d)
            f_old = f(x)
            f_new = f(x_new)
            
            print(f"  x^{k+1} = x^{k} + d^{k} = [{x_new[0]:.6f}, {x_new[1]:.6f}]ᵀ")
            print(f"  f(x^{k+1}) = {f_new:.6f}")
            
            # Шаг 11: Проверить выполнение условия f(x^(k+1)) < f(x^k)
            print(f"\n  Проверка: f(x^{k+1}) < f(x^{k})?")
            print(f"  {f_new:.6f} < {f_old:.6f}? ", end="")
            
            if f_new < f_old:
                # a) если неравенство выполняется, то перейти к шагу 12
                print("ДА")
                x = x_new
                k += 1
                
                # Шаг 12: Положить k = k+1, μ^(k+1) = μ^k / 2
                mu = mu / 2
                
                print(f"\n  ✓ Условие выполнено. Переходим к следующей итерации.")
                print(f"  Новое значение: μ^{k} = μ^{k-1} / 2 = {mu:.6f}")
                
                print(f"\nИтерация {k}:")
                break  # Выход из внутреннего цикла
            else:
                # б) если нет, то перейти к шагу 13
                print("НЕТ")
                
                # Шаг 13: Положить μ^k = 2μ^k и перейти к шагу 7
                mu = mu * 2
                print(f"  ✗ Условие не выполнено. Увеличиваем μ^{k} = {mu:.6f}")
                print(f"  Повторяем с шага 7...")
        
        print()
    
    print(f"\nДостигнуто максимальное число итераций M = {M}")
    return x


def main():
    """Основная функция для тестирования методов"""
    
    # Начальная точка из задания
    x0 = [2.0, 2.0]
    
    # Параметры
    eps1 = 0.1
    eps2 = 0.15
    M = 10
    
    print("\n" + "="*70)
    print("РЕШЕНИЕ ЗАДАЧИ 10: f(x) = 8x₁² + x₂² - x₁x₂ + x₁, x₀ = (2, 2)")
    print("="*70)
    
    # Метод Пауэлла
    x_powell = powell_method(x0, eps1, eps2, M)
    
    print(f"\n{'='*70}")
    print(f"РЕЗУЛЬТАТ МЕТОДА ПАУЭЛЛА:")
    print(f"{'='*70}")
    print(f"Найденная точка: x* = [{x_powell[0]:.6f}, {x_powell[1]:.6f}]ᵀ")
    print(f"Значение функции: f(x*) = {f(x_powell):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {norm(numerical_gradient(x_powell)):.6f}")
    
    # Метод Марквардта
    x_marq = marquardt_method(x0, eps1, M)
    
    print(f"\n{'='*70}")
    print(f"РЕЗУЛЬТАТ МЕТОДА МАРКВАРДТА:")
    print(f"{'='*70}")
    print(f"Найденная точка: x* = [{x_marq[0]:.6f}, {x_marq[1]:.6f}]ᵀ")
    print(f"Значение функции: f(x*) = {f(x_marq):.6f}")
    print(f"Норма градиента: ‖∇f(x*)‖ = {norm(numerical_gradient(x_marq)):.6f}")
    
    # Анализ решения
    print(f"\n{'='*70}")
    print(f"АНАЛИЗ РЕШЕНИЯ:")
    print(f"{'='*70}")
    
    H = hessian_matrix(x_marq)
    print(f"Матрица Гессе H =")
    print(f"  [[{H[0][0]:6.2f}, {H[0][1]:6.2f}]")
    print(f"   [{H[1][0]:6.2f}, {H[1][1]:6.2f}]]")
    
    det1 = H[0][0]
    det2 = H[0][0] * H[1][1] - H[0][1] * H[1][0]
    print(f"\nГлавные миноры: Δ₁ = {det1:.2f}, Δ₂ = {det2:.2f}")
    
    if det1 > 0 and det2 > 0:
        print("✓ H > 0 (положительно определена)")
        print("✓ Точка является локальным (и глобальным) минимумом")
    
    # Точное решение
    x1_exact = -2/31
    x2_exact = -1/31
    
    print(f"\nТочное решение (аналитическое):")
    print(f"x* = [{x1_exact:.6f}, {x2_exact:.6f}]ᵀ")
    print(f"f(x*) = {f([x1_exact, x2_exact]):.6f}")
    
    diff_powell = norm(vec_sub(x_powell, [x1_exact, x2_exact]))
    diff_marq = norm(vec_sub(x_marq, [x1_exact, x2_exact]))
    
    print(f"\nПогрешность метода Пауэлла: ‖x_Powell - x_exact‖ = {diff_powell:.6f}")
    print(f"Погрешность метода Марквардта: ‖x_Marq - x_exact‖ = {diff_marq:.6f}")


if __name__ == "__main__":
    main()