import math

# ============================================================
# ЗАДАЧА 4г: Метод прогонки (алгоритм Томаса)
# y'' + p(x)*y' + q(x)*y = f(x),  x in [a, b]
# ГУ: y'(a) = alpha  (Неймана)
#     y(b)  = beta   (Дирихле)
#
# Аппроксимация левого ГУ O(h^2) через фиктивный узел x_{-1}:
#   центральная разность: y'(a) ~ (y_1 - y_{-1}) / (2h) = alpha
#   => y_{-1} = y_1 - 2h*alpha
#   Подставляем в уравнение в точке i=0:
#   (y_{-1} - 2*y_0 + y_1)/h^2 + p_0*(y_1-y_{-1})/(2h) + q_0*y_0 = f_0
#   => B[0]*y_0 + C[0]*y_1 = D[0]  — двухточечная строка, прогонка работает!
#
# Трёхдиагональная система:
#   A[i]*y[i-1] + B[i]*y[i] + C[i]*y[i+1] = D[i]
#
# Прямой ход: alpha_p[i], beta_p[i] такие что y[i] = alpha_p[i]*y[i+1] + beta_p[i]
# Обратный ход: восстанавливаем y[n], y[n-1], ..., y[0]
# ============================================================

def solve(n, a_bc, b_bc, alpha, beta, p, q, f):
    h = (b_bc - a_bc) / n
    x = [a_bc + i * h for i in range(n + 1)]

    A = [0.0] * (n + 1)
    B = [0.0] * (n + 1)
    C = [0.0] * (n + 1)
    D = [0.0] * (n + 1)

    # --- Строка 0: левое ГУ Неймана через фиктивный узел ---
    # y_{-1} = y_1 - 2h*alpha, подставляем в уравнение при i=0:
    # (y_{-1}-2y_0+y_1)/h^2 + p_0*(y_1-y_{-1})/(2h) + q_0*y_0 = f_0
    # = (y_1-2h*alpha-2y_0+y_1)/h^2 + p_0*(y_1-(y_1-2h*alpha))/(2h) + q_0*y_0
    # = (2y_1-2y_0)/h^2 - 2*alpha/h + p_0*alpha + q_0*y_0 = f_0
    # => (-2/h^2+q_0)*y_0 + (2/h^2)*y_1 = f_0 + 2*alpha/h - p_0*alpha
    p0 = p(x[0])
    B[0] = -2/h**2 + q(x[0])
    C[0] =  2/h**2
    D[0] =  f(x[0]) + 2*alpha/h - p0*alpha

    # --- Строки 1..n-1: внутренние узлы, схема O(h^2) ---
    # y''_i ~ (y_{i-1}-2y_i+y_{i+1})/h^2
    # y'_i  ~ (y_{i+1}-y_{i-1})/(2h)
    for i in range(1, n):
        pi_ = p(x[i])
        A[i] =  1/h**2 - pi_/(2*h)
        B[i] = -2/h**2 + q(x[i])
        C[i] =  1/h**2 + pi_/(2*h)
        D[i] =  f(x[i])

    # --- Строка n: правое ГУ Дирихле y(b) = beta ---
    B[n] = 1.0
    D[n] = beta

    # -------------------------------------------------------
    # Прямой ход прогонки
    # y[i] = alpha_p[i]*y[i+1] + beta_p[i]
    # -------------------------------------------------------
    alpha_p = [0.0] * (n + 1)
    beta_p  = [0.0] * (n + 1)

    # Строка 0: B[0]*y[0] + C[0]*y[1] = D[0]  (A[0]=0)
    alpha_p[0] = -C[0] / B[0]
    beta_p[0]  =  D[0] / B[0]

    # Строки 1..n-1
    for i in range(1, n):
        # Подставляем y[i-1] = alpha_p[i-1]*y[i] + beta_p[i-1]:
        # A[i]*(alpha_p[i-1]*y[i]+beta_p[i-1]) + B[i]*y[i] + C[i]*y[i+1] = D[i]
        # (B[i] + A[i]*alpha_p[i-1])*y[i] + C[i]*y[i+1] = D[i] - A[i]*beta_p[i-1]
        denom      = B[i] + A[i] * alpha_p[i-1]
        alpha_p[i] = -C[i] / denom
        beta_p[i]  = (D[i] - A[i] * beta_p[i-1]) / denom

    # -------------------------------------------------------
    # Обратный ход прогонки
    # -------------------------------------------------------
    y = [0.0] * (n + 1)

    # Строка n: B[n]*y[n] = D[n]  (нет y[n+1], A[n] уже учтён через beta_p)
    y[n] = (D[n] - A[n] * beta_p[n-1]) / (B[n] + A[n] * alpha_p[n-1])

    for i in range(n - 1, -1, -1):
        y[i] = alpha_p[i] * y[i+1] + beta_p[i]

    return x, y


def run_example(name, a_bc, b_bc, alpha, beta, p, q, f, exact):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)
    ns = [10, 20, 40, 80]
    errs = []
    for n in ns:
        x, y = solve(n, a_bc, b_bc, alpha, beta, p, q, f)
        max_err = 0.0
        for i in range(len(x)):
            err = abs(y[i] - exact(x[i]))
            if err > max_err:
                max_err = err
        errs.append(max_err)
        print(f"n={n:3d},  h={(b_bc-a_bc)/n:.5f},  max|err| = {max_err:.2e}")
    print()
    for i in range(1, len(ns)):
        pr = math.log2(errs[i-1] / errs[i])
        print(f"Порядок ({ns[i-1]}->{ns[i]}): {pr:.2f}")


def run():
    run_example(
        "Пример 1: y'' - y = -sin(x),  y'(0)=0.5,  y(pi)=0",
        0, math.pi,
        0.5, 0.0,
        lambda x: 0.0,
        lambda x: -1.0,
        lambda x: -math.sin(x),
        lambda x: math.sin(x) / 2
    )
    run_example(
        "Пример 2: y'' - y = 0,  y'(0)=1,  y(1)=e",
        0, 1,
        1.0, math.e,
        lambda x: 0.0,
        lambda x: -1.0,
        lambda x: 0.0,
        lambda x: math.exp(x)
    )
    run_example(
        "Пример 3: y'' + y = 0,  y'(0)=1,  y(pi)=0",
        0, math.pi,
        1.0, 0.0,
        lambda x: 0.0,
        lambda x:  1.0,
        lambda x: 0.0,
        lambda x: math.sin(x)
    )

run()