import math

def dichotomy_method(a0, b0, l, eps):
    print("\n" + "@" * 40)
    print("МЕТОД ДИХОТОМИИ")
    print(f"\nНачальный интервал: [{a0}, {b0}]")
    print(f"Точность l = {l}, delta = {eps}")

    a = a0
    b = b0
    k = 0
    iterations = 0
    function_calls = 0

    while True:
        y = (a + b) / 2 - eps / 2
        z = (a + b) / 2 + eps / 2

        fy = f(y)
        fz = f(z)
        function_calls += 2

        print(f"\nИтерация {k}:")
        print(f"  Интервал [{a:.6f}, {b:.6f}], длина = {b - a:.6f}")
        print(f"    y = ({a:.6f} + {b:.6f})/2 - {eps}/2 = {y:.6f}")
        print(f"    z = ({a:.6f} + {b:.6f})/2 + {eps}/2 = {z:.6f}")
        print(f"    f(y) = {fy:.6f}")
        print(f"    f(z) = {fz:.6f}")

        if fy <= fz:
            b_new = z
            a_new = a
            print(f"    f(y) ≤ f(z) ==> выбираем левый подинтервал")
        else:
            a_new = y
            b_new = b
            print(f"    f(y) > f(z) ==> выбираем правый подинтервал")

        interval_length = abs(b_new - a_new)
        iterations += 1

        if interval_length <= l:
            print(f"\nУсловие остановки достигнуто:")
            print(f"  |L| = {interval_length:.6f} ≤ {l}")
            x_star = (a_new + b_new) / 2
            print(f"\nРЕЗУЛЬТАТ МЕТОДА ДИХОТОМИИ")
            print(f"  x* ∈ [{a_new:.6f}, {b_new:.6f}]")
            print(f"  x* ≈ {x_star:.6f}")
            print(f"  f(x*) = {f(x_star):.6f}")
            print(f"  Итераций: {iterations}")
            print(f"  Вычислений функции: {function_calls}")
            print("=" * 40)
            return
        else:
            print(f"  |L| = {interval_length:.6f} > {l}, продолжаем...")

        a = a_new
        b = b_new
        k += 1
def golden_section_method(a0, b0, l):
    print("\n" + "@" * 40)
    print("МЕТОД ЗОЛОТОГО СЕЧЕНИЯ")
    print(f"\nНачальный интервал: [{a0}, {b0}]")
    print(f"Точность l = {l}")

    coeff = (3 - math.sqrt(5)) / 2
    a = a0
    b = b0
    k = 0
    iterations = 0
    function_calls = 0

    y = a + coeff * (b - a)
    z = a + b - y
    fy, fz = f(y), f(z)
    function_calls += 2

    print(f"\nИнициализация:")
    print(f"  y_0 = {y:.6f}")
    print(f"  z_0 = {z:.6f}")
    print(f"  f(y_0) = {fy:.6f}")
    print(f"  f(z_0) = {fz:.6f}")

    while True:
        if fy <= fz:
            a_new = a
            b_new = z
            z_new = y
            y_new = a_new + coeff * (b_new - a_new)
            fz_new = fy
            fy_new = f(y_new)
            function_calls += 1
        else:
            a_new = y
            b_new = b
            y_new = z
            z_new = a_new + b_new - y_new
            fy_new = fz
            fz_new = f(z_new)
            function_calls += 1

        interval_length = abs(b_new - a_new)
        iterations += 1

        print(f"\nИтерация {k}:")
        print(f"  Новый интервал [{a_new:.6f}, {b_new:.6f}]")
        print(f"  Длина = {interval_length:.6f}")

        if interval_length <= l:
            x_star = (a_new + b_new) / 2
            print(f"\nРЕЗУЛЬТАТ МЕТОДА ЗОЛОТОГО СЕЧЕНИЯ")
            print(f"  x* ∈ [{a_new:.6f}, {b_new:.6f}]")
            print(f"  x* ≈ {x_star:.6f}")
            print(f"  f(x*) = {f(x_star):.6f}")
            print(f"  Итераций: {iterations}")
            print(f"  Вычислений функции: {function_calls}")
            print("=" * 40)
            return
        else:
            print(f"  |L| = {interval_length:.6f} > {l}, продолжаем...")

        a, b = a_new, b_new
        y, z = y_new, z_new
        fy, fz = fy_new, fz_new
        k += 1

def fibonacci_method(a0, b0, l, eps=1e-6):
    print("\n" + "@" * 40)
    print("МЕТОД ФИБОНАЧЧИ")
    print(f"\nНачальный интервал: [{a0}, {b0}]")
    print(f"Точность l = {l}")

    # Генерация чисел Фибоначчи
    F = [0, 1]
    while F[-1] < (b0 - a0) / l:
        F.append(F[-1] + F[-2])

    N = len(F) - 1
    print(f"Найдено N = {N}, F_N = {F[N]}")

    a = a0
    b = b0
    k = 0
    function_calls = 0

    y = a + F[N-2] / F[N] * (b - a)
    z = a + F[N-1] / F[N] * (b - a)

    fy = f(y)
    fz = f(z)
    function_calls += 2

    while k < N - 2:
        print(f"\nИтерация {k}")
        print(f"  Интервал [{a:.6f}, {b:.6f}]")

        if fy <= fz:
            b = z
            z = y
            fz = fy
            y = a + F[N-k-3] / F[N-k-1] * (b - a)
            fy = f(y)
            function_calls += 1
        else:
            a = y
            y = z
            fy = fz
            z = a + F[N-k-2] / F[N-k-1] * (b - a)
            fz = f(z)
            function_calls += 1

        k += 1

    x_star = (a + b) / 2
    print(f"\nРЕЗУЛЬТАТ МЕТОДА ФИБОНАЧЧИ")
    print(f"  x* ∈ [{a:.6f}, {b:.6f}]")
    print(f"  x* ≈ {x_star:.6f}")
    print(f"  f(x*) = {f(x_star):.6f}")
    print(f"  Итераций: {k}")
    print(f"  Вычислений функции: {function_calls}")
    print("=" * 40)

def f(x):
    return 2*math.pow(x, 2) - 2*x + 5/2

def main():
    #dichotomy_method(-1, 9, 1, 0.2)
    #golden_section_method(-1, 9, 1)
    fibonacci_method(-1, 9, 1)

if __name__=="__main__":
    main()