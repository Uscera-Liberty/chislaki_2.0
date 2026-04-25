# Многомерный метод: метод Ньютона (шаг t=1 + backtracking Армихо)
# Одномерная оптимизация: метод Свенна + метод золотого сечения
# ВАЖНО: одномерный поиск НЕ используется внутри Ньютона —
# при больших r он возвращает t≈0 и x перестаёт меняться (зависание).

import math

# ─────────────────────── ОДНОМЕРНАЯ ОПТИМИЗАЦИЯ ───────────────────────

def swann(f, x0, h=1.0):
    a, fa = x0, f(x0)
    b, fb = x0 + h, f(x0 + h)
    if fb > fa:
        h = -h
        a, b = b, x0
        fa, fb = fb, fa
    while True:
        c = b + h
        fc = f(c)
        if fc >= fb:
            return (min(a, c), max(a, c))
        a, fa = b, fb
        b, fb = c, fc
        h *= 2.0

def golden_section(f, a, b, tol=1e-10):
    phi = (math.sqrt(5) - 1) / 2
    x1 = b - phi * (b - a)
    x2 = a + phi * (b - a)
    f1, f2 = f(x1), f(x2)
    while (b - a) > tol:
        if f1 < f2:
            b, x2, f2 = x2, x1, f1
            x1 = b - phi * (b - a)
            f1 = f(x1)
        else:
            a, x1, f1 = x1, x2, f2
            x2 = a + phi * (b - a)
            f2 = f(x2)
    return (a + b) / 2.0

# ─────────────────────── ЧИСЛЕННЫЕ ПРОИЗВОДНЫЕ ───────────────────────

def grad(f, x, eps=1e-7):
    fx = f(x)
    g = []
    for i in range(len(x)):
        xp = x[:]
        xp[i] += eps
        g.append((f(xp) - fx) / eps)
    return g

def hess(f, x, eps=1e-5):
    n = len(x)
    H = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            xpp = x[:]; xpp[i] += eps; xpp[j] += eps
            xpm = x[:]; xpm[i] += eps; xpm[j] -= eps
            xmp = x[:]; xmp[i] -= eps; xmp[j] += eps
            xmm = x[:]; xmm[i] -= eps; xmm[j] -= eps
            H[i][j] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * eps * eps)
    return H

# ─────────────────────── РЕШЕНИЕ СЛАУ (Гаусс) ───────────────────────

def solve_linear(A, b):
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        if abs(M[col][col]) < 1e-14:
            return None
        for row in range(col + 1, n):
            c = M[row][col] / M[col][col]
            for k in range(col, n + 1):
                M[row][k] -= c * M[col][k]
    sol = [0.0] * n
    for i in range(n - 1, -1, -1):
        sol[i] = M[i][n]
        for j in range(i + 1, n):
            sol[i] -= M[i][j] * sol[j]
        sol[i] /= M[i][i]
    return sol

# ─────────────────────── МЕТОД НЬЮТОНА ───────────────────────────────

def newton_method(f, x0, tol=1e-9, max_iter=200):
    x = x0[:]
    for _ in range(max_iter):
        g = grad(f, x)
        norm_g = math.sqrt(sum(gi ** 2 for gi in g))
        if norm_g < tol:
            break
        H = hess(f, x)
        d = solve_linear(H, [-gi for gi in g])
        if d is None or sum(di * gi for di, gi in zip(d, g)) >= 0:
            d = [-gi for gi in g]
        t, fx = 1.0, f(x)
        slope = sum(gi * di for gi, di in zip(g, d))
        for _ in range(60):
            xnew = [x[i] + t * d[i] for i in range(len(x))]
            if f(xnew) <= fx + 1e-4 * t * slope:
                break
            t *= 0.5
        x = [x[i] + t * d[i] for i in range(len(x))]
    return x

# ─────────────────────── МЕТОД ШТРАФОВ ───────────────────────────────
# F(x,r^k) = f(x) + (r^k/2) * Σ[g_j(x)]²
# Критерий останова: |g(x*)| < eps

def penalty_method(f, eq_constraints, x0, r0=1.0, C=10.0, eps=1e-5, max_iter=15):
    print("=" * 60)
    print("МЕТОД ШТРАФОВ (внешних штрафов)")
    print("=" * 60)

    x = x0[:]
    r = r0

    for k in range(max_iter):
        r_k = r

        def F(x, r=r_k):
            return f(x) + (r / 2.0) * sum(g(x) ** 2 for g in eq_constraints)

        x = newton_method(F, x)
        viol = math.sqrt(sum(g(x) ** 2 for g in eq_constraints))

        print(f"  k={k:2d}  r={r:.4g}  x*={[round(xi, 6) for xi in x]}"
              f"  f(x*)={round(f(x), 6)}  |g(x)|={round(viol, 8)}")

        if viol <= eps:
            break
        r *= C

    print(f"\n  Результат: x* = {[round(xi, 6) for xi in x]}, f(x*) = {round(f(x), 6)}\n")
    return x, f(x)

# ─────────────────── МОДИФИЦИРОВАННЫЙ МЕТОД МНОЖИТЕЛЕЙ ───────────────
# L(x,λ^k,r^k) = f(x) + λ_j^k·g_j(x) + (r^k/2)·[g_j(x)]²
# Пересчёт: λ^{k+1} = λ^k + r^k · g_j(x*)
# Критерий останова: |g(x*)| < eps

def augmented_lagrangian_method(f, eq_constraints, x0, lam0=None,
                                r0=1.0, C=4.0, eps=1e-5, max_iter=15):
    print("=" * 60)
    print("МОДИФИЦИРОВАННЫЙ МЕТОД МНОЖИТЕЛЕЙ ЛАГРАНЖА")
    print("=" * 60)

    m = len(eq_constraints)
    lam = lam0[:] if lam0 else [0.0] * m
    x = x0[:]
    r = r0

    for k in range(max_iter):
        lam_k, r_k = lam[:], r

        def L(x, lam=lam_k, r=r_k):
            val = f(x)
            for j, g in enumerate(eq_constraints):
                gx = g(x)
                val += lam[j] * gx + (r / 2.0) * gx ** 2
            return val

        x = newton_method(L, x)
        viol = math.sqrt(sum(g(x) ** 2 for g in eq_constraints))

        print(f"  k={k:2d}  r={r:.4g}  λ={[round(l, 6) for l in lam]}")
        print(f"         x*={[round(xi, 6) for xi in x]}"
              f"  f(x*)={round(f(x), 6)}  |g(x)|={round(viol, 8)}")

        if viol <= eps:
            break

        lam = [lam[j] + r * eq_constraints[j](x) for j in range(m)]
        r *= C

    print(f"\n  Результат: x* = {[round(xi, 6) for xi in x]}, f(x*) = {round(f(x), 6)}\n")
    return x, f(x)

# ─────────────────────── ЗАДАЧА 10 ───────────────────────────────────
# f(x) = 8x1² + x2² - x1*x2 + x1  →  min
# 2x1 + x2 = 3

if __name__ == "__main__":
    print("=" * 60)
    print("ЗАДАЧА 10")
    print("f(x) = 8x1² + x2² - x1*x2 + x1  →  min")
    print("2x1 + x2 = 3")
    print("=" * 60 + "\n")

    f  = lambda x: 8*x[0]**2 + x[1]**2 - x[0]*x[1] + x[0]
    g1 = lambda x: 2*x[0] + x[1] - 3.0

    x0 = [0.0, 0.0]

    penalty_method(f, [g1], x0)
    augmented_lagrangian_method(f, [g1], x0, lam0=[0.0])