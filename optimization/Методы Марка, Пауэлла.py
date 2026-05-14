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


def powell_method2(x0, eps1=0.0001, eps2=0.00015, M=100):
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
        
        x_start = x[:] 
        
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

def powell_method(x0, eps1=0.0001, eps2=0.00015, M=50):
    """
    Улучшенный метод Пауэлла с проверкой линейной независимости направлений
    """
    n = len(x0)
    x = x0[:]
    k = 0
    converged_twice = False
    
    print("\n" + "="*70)
    print("МЕТОД ПАУЭЛЛА (УЛУЧШЕННАЯ ВЕРСИЯ)")
    print("="*70)
    print(f"Начальная точка: x⁰ = ({x[0]:.3f}, {x[1]:.3f})")
    print(f"ε₁ = {eps1}, ε₂ = {eps2}, M = {M}")
    
    # Начальные направления - единичные орты
    directions = [[1.0, 0.0], [0.0, 1.0]]
    
    # Запоминаем, какое уменьшение дало каждое направление
    delta_f = [0.0, 0.0]
    
    while k < M:
        print(f"\nЦИКЛ {k}:")
        print(f"  x_начало = [{x[0]:.6f}, {x[1]:.6f}]ᵀ, f = {f(x):.6f}")
        
        x_start = x[:]
        f_start = f(x)
        
        # Минимизация вдоль текущих направлений и запись уменьшений
        max_delta = -1.0
        max_idx = 0
        
        for i in range(n):
            d = directions[i]
            f_before = f(x)
            
            t_opt = golden_section_search(x, d)
            x = vec_add(x, vec_mul_scalar(d, t_opt))
            
            f_after = f(x)
            current_delta = abs(f_before - f_after)
            delta_f[i] = current_delta
            
            if current_delta > max_delta:
                max_delta = current_delta
                max_idx = i
            
            print(f"  Шаг {i+1}: t* = {t_opt:.6f}, Δf = {current_delta:.6f}")
        
        # Проверка сходимости
        grad = numerical_gradient(x)
        grad_norm = norm(grad)
        
        if grad_norm < eps1:
            print(f"  ✓ ‖∇f‖ < ε₁. Минимум найден!")
            return x
        
        x_diff = norm(vec_sub(x, x_start))
        f_diff = abs(f(x) - f_start)
        
        if x_diff < eps2 and f_diff < eps2:
            if converged_twice:
                print(f"  ✓ Сходимость по x и f достигнута дважды")
                return x
            converged_twice = True
        else:
            converged_twice = False
        
        # Формируем новое направление
        v = vec_sub(x, x_start)
        v_norm = norm(v)
        
        print(f"  Новое направление v: ‖v‖ = {v_norm:.6f}")
        
        # Проверка линейной независимости
        if v_norm > 1e-8:
            # Дополнительная минимизация вдоль v
            t_opt = golden_section_search(x, v)
            x = vec_add(x, vec_mul_scalar(v, t_opt))
            print(f"  Минимизация вдоль v: t* = {t_opt:.6f}")
            
            v_norm = norm(v)
            if v_norm > 1e-8:
                v_normalized = [v[0]/v_norm, v[1]/v_norm]
                
                # Проверяем, не коллинеарно ли v существующим направлениям
                is_independent = True
                for d in directions:
                    d_norm = norm(d)
                    if d_norm > 1e-8:
                        d_normalized = [d[0]/d_norm, d[1]/d_norm]
                        dot_product = abs(v_normalized[0]*d_normalized[0] + v_normalized[1]*d_normalized[1])
                        if dot_product > 0.999:  # Почти параллельны
                            is_independent = False
                            break
                
                if is_independent:
                    # Заменяем направление, давшее НАИМЕНЬШЕЕ уменьшение
                    min_idx = 0 if delta_f[0] < delta_f[1] else 1
                    directions[min_idx] = v
                    print(f"  ✓ Направление {min_idx} заменено (независимое)")
                else:
                    print(f"  ⚠ Направление v линейно зависимо, пропускаем замену")
            else:
                print(f"  ⚠ Направление v слишком мало, пропускаем")
        else:
            print(f"  ⚠ v ≈ 0, пропускаем обновление направлений")
        
        
        k += 1
    
    print(f"\nДостигнуто максимальное число итераций M = {M}")
    return x

def main():
    """Основная функция для тестирования методов"""
    
    # Начальная точка из задания
    x0 = [-100, -100]
    
    # Параметры
    eps1 = 0.0001
    eps2 = 0.00015
    M = 50
    
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
    
    
    
    # Точное решение
    x1_exact = -2/31
    x2_exact = -1/31
    
    print(f"\nТочное решение (аналитическое):")
    print(f"x* = [{x1_exact:.6f}, {x2_exact:.6f}]ᵀ")
    print(f"f(x*) = {f([x1_exact, x2_exact]):.6f}")
    
    diff_powell = norm(vec_sub(x_powell, [x1_exact, x2_exact]))
    
    print(f"\nПогрешность метода Пауэлла: ‖x_Powell - x_exact‖ = {diff_powell:.6f}")


if __name__ == "__main__":
    main()