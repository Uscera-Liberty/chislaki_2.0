import numpy as np

# ============================================================
# ЗАДАЧА 4г: Метод прогонки
# Уравнение: y'' + p(x)*y' + q(x)*y = f(x),  x in [a, b]
# Граничные условия:
#   y'(a) = alpha  -- условие Неймана (левая граница)
#   y(b)  = beta   -- условие Дирихле (правая граница)
#
# Конкретный пример:
#   p(x) = 0,  q(x) = -1,  f(x) = -sin(x),  x in [0, pi]
#   y'(0) = 1/2,  y(pi) = 0
#   Точное решение: y = sin(x) / 2
# ============================================================

a_bc, b_bc = 0.0, np.pi
alpha = 0.5   # y'(a)
beta  = 0.0   # y(b)

def p(x): return 0.0
def q(x): return -1.0
def f(x): return -np.sin(x)
def exact(x): return np.sin(x) / 2.0

def solve(n):
    h = (b_bc - a_bc) / n
    x = np.linspace(a_bc, b_bc, n + 1)

    # Строим матрицу системы MAT * y = RHS
    N = n + 1
    MAT = np.zeros((N, N))
    RHS = np.zeros(N)

    # --- Строка 0: левое ГУ Неймана y'(a) = alpha ---
    # Аппроксимация производной O(h^2) трёхточечной формулой:
    # (-3*y_0 + 4*y_1 - y_2) / (2h) = alpha
    MAT[0, 0] = -3.0
    MAT[0, 1] =  4.0
    MAT[0, 2] = -1.0
    RHS[0] = 2 * h * alpha

    # --- Строки 1..n-1: внутренние узлы ---
    # Аппроксимация O(h^2):
    #   y''_i ~ (y_{i-1} - 2*y_i + y_{i+1}) / h^2
    #   y'_i  ~ (y_{i+1} - y_{i-1}) / (2h)
    # Подставляем в уравнение:
    #   (1/h^2 - p_i/2h)*y_{i-1} + (-2/h^2 + q_i)*y_i + (1/h^2 + p_i/2h)*y_{i+1} = f_i
    for i in range(1, n):
        pi_ = p(x[i])
        MAT[i, i-1] =  1/h**2 - pi_/(2*h)
        MAT[i, i]   = -2/h**2 + q(x[i])
        MAT[i, i+1] =  1/h**2 + pi_/(2*h)
        RHS[i] = f(x[i])

    # --- Строка n: правое ГУ Дирихле y(b) = beta ---
    MAT[n, n] = 1.0
    RHS[n] = beta

    # Решаем трёхдиагональную систему методом прогонки
    y = np.linalg.solve(MAT, RHS)
    return x, y

def run():
    print("=" * 55)
    print("МЕТОД ПРОГОНКИ: y'' + p*y' + q*y = f")
    print("p=0, q=-1, f=-sin(x), x in [0, pi]")
    print("ГУ: y'(0)=0.5 (Неймана), y(pi)=0 (Дирихле)")
    print("Точное решение: y = sin(x)/2")
    print("=" * 55)

    ns = [10, 20, 40, 80]
    errs = []
    for n in ns:
        x, y = solve(n)
        e = np.max(np.abs(y - exact(x)))
        errs.append(e)
        print(f"n={n:3d},  h={np.pi/n:.5f},  max|err| = {e:.2e}")

    print()
    for i in range(1, len(ns)):
        pr = np.log2(errs[i-1] / errs[i])
        print(f"Порядок сходимости ({ns[i-1]}->{ns[i]}): {pr:.2f}")

run()