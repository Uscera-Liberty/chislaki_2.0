import math

# ============================================================
# МЕТОД ПРОГОНКИ
# y'' + p(x)*y' + q(x)*y = f(x)
#
# Граничные условия
# y'(a) = alpha
# y(b)  = beta
# ============================================================


def gaussian_solve(A, b):
    n = len(b)

    for k in range(n):

        pivot = A[k][k]

        for j in range(k, n):
            A[k][j] = A[k][j] / pivot

        b[k] = b[k] / pivot

        for i in range(k + 1, n):

            factor = A[i][k]

            for j in range(k, n):
                A[i][j] -= factor * A[k][j]

            b[i] -= factor * b[k]

    x = [0] * n

    for i in range(n - 1, -1, -1):

        x[i] = b[i]

        for j in range(i + 1, n):
            x[i] -= A[i][j] * x[j]

    return x


def solve(n, a_bc, b_bc, alpha, beta, p, q, f):

    h = (b_bc - a_bc) / n

    x = []
    for i in range(n + 1):
        x.append(a_bc + i * h)

    N = n + 1

    MAT = []
    for i in range(N):
        row = [0.0] * N
        MAT.append(row)

    RHS = [0.0] * N

    # --- левое граничное условие ---
    MAT[0][0] = -3.0
    MAT[0][1] = 4.0
    MAT[0][2] = -1.0
    RHS[0] = 2 * h * alpha

    # --- внутренние узлы ---
    for i in range(1, n):

        pi_ = p(x[i])

        MAT[i][i - 1] = 1 / h**2 - pi_ / (2 * h)
        MAT[i][i] = -2 / h**2 + q(x[i])
        MAT[i][i + 1] = 1 / h**2 + pi_ / (2 * h)

        RHS[i] = f(x[i])

    # --- правое граничное условие ---
    MAT[n][n] = 1
    RHS[n] = beta

    y = gaussian_solve(MAT, RHS)

    return x, y


def run_example(name, a_bc, b_bc, alpha, beta, p, q, f, exact):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    ns = [10, 20, 40, 80]

    errs = []

    for n in ns:

        x, y = solve(n, a_bc, b_bc, alpha, beta, p, q, f)

        max_err = 0

        for i in range(len(x)):
            err = abs(y[i] - exact(x[i]))
            if err > max_err:
                max_err = err

        errs.append(max_err)

        print(f"n={n:3d}, h={(b_bc-a_bc)/n:.5f}, max|err|={max_err:.2e}")

    print()

    for i in range(1, len(ns)):

        pr = math.log2(errs[i - 1] / errs[i])
        print(f"Порядок ({ns[i-1]}->{ns[i]}): {pr:.2f}")


def run():

    # ===============================
    # ПРИМЕР 1
    # y'' - y = -sin(x)
    # y'(0)=0.5
    # y(pi)=0
    # ===============================

    run_example(
        "Пример 1: y'' - y = -sin(x),  y'(0)=0.5, y(pi)=0",
        0, math.pi,
        0.5, 0,
        lambda x: 0,
        lambda x: -1,
        lambda x: -math.sin(x),
        lambda x: math.sin(x) / 2
    )

    # ===============================
    # ПРИМЕР 2
    # y'' - y = 0
    # y'(0)=1
    # y(1)=e
    # ===============================

    run_example(
        "Пример 2: y'' - y = 0,  y'(0)=1, y(1)=e",
        0, 1,
        1, math.e,
        lambda x: 0,
        lambda x: -1,
        lambda x: 0,
        lambda x: math.exp(x)
    )

    # ===============================
    # ПРИМЕР 3
    # y'' + y = 0
    # y'(0)=1
    # y(pi)=0
    # ===============================

    run_example(
        "Пример 3: y'' + y = 0,  y'(0)=1, y(pi)=0",
        0, math.pi,
        1, 0,
        lambda x: 0,
        lambda x: 1,
        lambda x: 0,
        lambda x: math.sin(x)
    )


run()