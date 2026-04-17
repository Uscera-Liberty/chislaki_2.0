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


def find_optimal_step_golden(x, d, a=0.0, b=2.0, tol=1e-5):
    phi = (math.sqrt(5) - 1)/2

    def phi_f(t):
        return f(vec_add(x, vec_mul_scalar(d, t)))

    x1 = b - phi*(b-a)
    x2 = a + phi*(b-a)
    f1 = phi_f(x1)
    f2 = phi_f(x2)

    while abs(b-a) > tol:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - phi*(b-a)
            f1 = phi_f(x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + phi*(b-a)
            f2 = phi_f(x2)

    return (a+b)/2


# ===== ФЛЕТЧЕР-РИВС =====

def fletcher_reeves_method(x0, eps1=0.1, eps2=0.15, M=10):
    n = len(x0)
    x = x0[:]
    k = 0

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
        t_k = find_optimal_step_golden(x, d)
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
            print("  ✓ Условия выполнены")
            return x

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
            beta = (grad_norm**2)/(grad_norm_prev**2)
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

    print("\n" + "="*70)
    print("МЕТОД ДЭВИДОНА-ФЛЕТЧЕРА-ПАУЭЛЛА")
    print("="*70)

    A = identity(n)

    print(f"Итерация {k}:")
    print(f"  A^{k} = E")
    print(f"  {A}")

    grad = numerical_gradient(x)
    grad_norm = norm(grad)

    print(f"  x^{k} = [{x[0]:.6f}, {x[1]:.6f}]ᵀ")
    print(f"  f(x^{k}) = {f(x):.6f}")
    print(f"  ∇f(x^{k}) = [{grad[0]:.6f}, {grad[1]:.6f}]ᵀ")
    print(f"  ‖∇f(x^{k})‖ = {grad_norm:.6f}")

    while k < M:
        d = vec_mul_scalar(mat_vec(A, grad), -1)
        print(f"  d^{k} = [{d[0]:.6f}, {d[1]:.6f}]ᵀ")

        t_k = find_optimal_step_golden(x, d)
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

        if k >= M:
            break

        grad = numerical_gradient(x)

        delta_g = vec_sub(grad, grad_old)
        delta_x = vec_sub(x, x_old)

        print(f"  Δg = [{delta_g[0]:.6f}, {delta_g[1]:.6f}]ᵀ")
        print(f"  Δx = [{delta_x[0]:.6f}, {delta_x[1]:.6f}]ᵀ")

    return x


# ===== MAIN =====

def main():
    x0 = [2.0, 2.0]

    print("\n" + "="*70)
    print("РЕШЕНИЕ ЗАДАЧИ 10")
    print("="*70)

    x_fr = fletcher_reeves_method(x0)
    x_dfp = davidon_fletcher_powell_method(x0)

    print("\nРезультат FR:", x_fr)
    print("Результат DFP:", x_dfp)


if __name__ == "__main__":
    main()