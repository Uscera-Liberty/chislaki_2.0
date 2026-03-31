"""
Метод наискорейшего градиентного спуска.
Одномерная минимизация: метод Свена + золотое сечение.

Критерии остановки:
  e1 — по норме градиента: ||grad f(x^k)|| < e1
  e2 — по норме изменения точки и функции
"""

import math


# ─── Целевая функция и градиент ───────────────────────────────────

def f(x):
    return 8 * x[0]**2 + x[1]**2 - x[0]*x[1] + x[0]

def grad_f(x):
    return [16 * x[0] - x[1] + 1, 2 * x[1] - x[0]]


# ─── Векторные операции ───────────────────────────────────────────

def norm(v):       return math.sqrt(sum(vi**2 for vi in v))
def vec_sub(a, b): return [ai - bi for ai, bi in zip(a, b)]
def vec_add(a, b): return [ai + bi for ai, bi in zip(a, b)]
def vec_scale(a, v): return [a * vi for vi in v]


# ─── Одномерная функция шага ──────────────────────────────────────

def phi(t, xk, dk):
    return f(vec_add(xk, vec_scale(t, dk)))


# ─── Метод Свена ─────────────────────────────────────────────────

def sven(xk, dk, t0=1.0, delta=1e-3):
    t_prev, t_curr = t0, t0 + delta
    phi_prev, phi_curr = phi(t_prev, xk, dk), phi(t_curr, xk, dk)

    if phi_curr > phi_prev:
        delta = -delta
        t_prev, t_curr = t_curr, t_prev
        phi_prev, phi_curr = phi_curr, phi_prev

    for step in range(1, 101):
        t_next = t_curr + (2 ** step) * delta
        phi_next = phi(t_next, xk, dk)

        if phi_next >= phi_curr:
            return min(t_prev, t_next), max(t_prev, t_next)

        t_prev, phi_prev = t_curr, phi_curr
        t_curr, phi_curr = t_next, phi_next

    return min(t_prev, t_curr), max(t_prev, t_curr)


# ─── Метод золотого сечения ───────────────────────────────────────

GOLDEN_RATIO = (math.sqrt(5) - 1) / 2  # ≈ 0.618

def golden_section(xk, dk, a, b, tol=1e-6):
    t1 = a + (1 - GOLDEN_RATIO) * (b - a)
    t2 = a + GOLDEN_RATIO * (b - a)
    phi1, phi2 = phi(t1, xk, dk), phi(t2, xk, dk)

    while (b - a) > tol:
        if phi1 < phi2:
            b, t2, phi2 = t2, t1, phi1
            t1 = a + (1 - GOLDEN_RATIO) * (b - a)
            phi1 = phi(t1, xk, dk)
        else:
            a, t1, phi1 = t1, t2, phi2
            t2 = a + GOLDEN_RATIO * (b - a)
            phi2 = phi(t2, xk, dk)

    return (a + b) / 2


# ─── Метод наискорейшего спуска ───────────────────────────────────

def steepest_descent(x0, e1=0.1, e2=0.15, M=10, t0=1.0):
    print("=" * 65)
    print("  МЕТОД НАИСКОРЕЙШЕГО (ГРАДИЕНТНОГО) СПУСКА")
    print("  Одномерная минимизация: Метод Свена + Золотое сечение")
    print("=" * 65)
    print(f"\n  f(x) = 2*x1^2 + x1*x2 + x2^2")
    print(f"  grad f(x) = (4*x1 + x2 ; x1 + 2*x2)^T\n")
    print(f"  x0={x0},  e1={e1},  e2={e2},  M={M},  t0={t0}\n")

    xk = list(x0)
    prev_stop = False

    for k in range(M + 1):
        print(f"{'─'*65}")
        print(f"  ИТЕРАЦИЯ  k = {k}")
        print(f"{'─'*65}")

        gk = grad_f(xk)
        norm_gk = norm(gk)
        print(f"  ШАГ 3.  grad f = ({gk[0]:.4f}; {gk[1]:.4f}),  ||grad f|| = {norm_gk:.4f}")

        print(f"  ШАГ 4.  ||grad f|| < e1?  {norm_gk:.4f} < {e1}  →  {'ДА' if norm_gk < e1 else 'НЕТ'}")
        if norm_gk < e1:
            print("          → Стоп: критерий по градиенту.")
            return _print_result(xk)

        print(f"  ШАГ 5.  k >= M?  {k} >= {M}  →  {'ДА' if k >= M else 'НЕТ'}")
        if k >= M:
            print("          → Стоп: достигнут лимит итераций.")
            return _print_result(xk)

        dk = vec_scale(-1, gk)
        print(f"  ШАГ 6.  d^k = ({dk[0]:.4f}; {dk[1]:.4f})")

        a, b = sven(xk, dk, t0=t0)
        print(f"  [Свен]   [a, b] = [{a:.6f}; {b:.6f}]")

        tk = golden_section(xk, dk, a, b)
        print(f"  [Золото] t_k* = {tk:.6f}")

        xk_new = vec_add(xk, vec_scale(tk, dk))
        f_old, f_new = f(xk), f(xk_new)
        print(f"  ШАГ 7.  x^{{k+1}} = ({xk_new[0]:.6f}; {xk_new[1]:.6f}),  f = {f_new:.6f}")

        delta_x = norm(vec_sub(xk_new, xk))
        delta_f = abs(f_new - f_old)
        curr_stop = delta_x < e2 and delta_f < e2
        print(f"  ШАГ 8.  ||Δx|| = {delta_x:.4f} < e2? {'ДА' if delta_x < e2 else 'НЕТ'} | "
              f"|Δf| = {delta_f:.4f} < e2? {'ДА' if delta_f < e2 else 'НЕТ'}")

        xk = xk_new

        if curr_stop and prev_stop:
            print("          → Стоп: условия выполнены два раза подряд.")
            return _print_result(xk)

        prev_stop = curr_stop
        print(f"          → k = {k + 1}, перейти к шагу 3.")

    return _print_result(xk)


def _print_result(xk):
    print()
    print("=" * 65)
    print(f"  РЕЗУЛЬТАТ:  x* ≈ ({xk[0]:.6f}; {xk[1]:.6f}),  f(x*) ≈ {f(xk):.6f}")
    print("=" * 65)
    return xk


# ─── Запуск ───────────────────────────────────────────────────────

if __name__ == "__main__":
    steepest_descent(x0=[0.5, 1.0], e1=0.1, e2=0.15, M=10, t0=1.0)