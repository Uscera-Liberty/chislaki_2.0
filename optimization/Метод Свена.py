import math


def f(x):
    return 2 * math.pow(x, 2) - 2 * x + 5 / 2


def swann_method(x0, t):
    print("\n" + "@" * 40)
    print("АЛГОРИТМ СВЕННА")
    print(f"\nНачальная точка: x0 = {x0}")
    print(f"Начальный шаг: t = {t}")

    f0, f1 = f(x0), f(x0 + t)
    calls = 2

    print(f"\nf(x0) = {f0:.6f}")
    print(f"f(x0 + t) = {f1:.6f}")

    delta = t if f1 < f0 else -t
    print(f"\nНаправление поиска: {'вправо' if delta > 0 else 'влево'} (delta = {delta})")

    a0 = x0
    x0, f0 = x0 + delta, f(x0 + delta)
    calls += 1

    k = 0
    while True:
        delta *= 2
        x1 = x0 + delta
        f1 = f(x1)
        calls += 1

        print(f"\nИтерация {k}:")
        print(f"  a0 = {a0:.6f}")
        print(f"  x0 = {x0:.6f},  f0 = {f0:.6f}")
        print(f"  x1 = {x1:.6f},  f1 = {f1:.6f},  delta = {delta:.6f}")

        if f1 >= f0:
            print(f"  f1 >= f0 => стоп")
            break

        print(f"  f1 < f0 => продолжаем")
        a0 = x0
        x0, f0 = x1, f1
        k += 1

    a0, b0 = (a0, x1) if delta > 0 else (x1, a0)

    print("\n" + "=" * 40)
    print("НАЙДЕН ИНТЕРВАЛ НЕОПРЕДЕЛЁННОСТИ")
    print(f"  [a0, b0] = [{a0:.6f}, {b0:.6f}]")
    print(f"  Итераций: {k + 1}")
    print(f"  Вычислений функции: {calls}")
    print("=" * 40)
    return a0, b0


def main():
    swann_method(1, 1)
    swann_method(100, 1)


if __name__ == "__main__":
    main()