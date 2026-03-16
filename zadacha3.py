
import math


def exact_F1(t):
    return [math.cos(t) +
            -math.sin(t)]

def exact_F2(t):
    return [math.exp(t),
            math.exp(2*t)]

def F_new(t, Y):
    y1, y2 = Y
    return [y2, -4*y1]


def exact_new(t):
    return [math.cos(2*t),
            -2*math.sin(2*t)]

def F1(t, Y):
    y1, y2 = Y
    return [y2, -y1]


def F2(t, Y):
    y1, y2 = Y
    return [y1, 2*y2]




def rk4_system(F, t0, Y0, h, N):

    t_values = [t0]
    Y_values = [Y0[:]]

    t = t0
    Y = Y0[:]

    for _ in range(N):

        K1 = F(t, Y)

        Y_K2 = [Y[i] + h*K1[i]/2 for i in range(len(Y))]
        K2 = F(t + h/2, Y_K2)

        Y_K3 = [Y[i] + h*K2[i]/2 for i in range(len(Y))]
        K3 = F(t + h/2, Y_K3)

        Y_K4 = [Y[i] + h*K3[i] for i in range(len(Y))]
        K4 = F(t + h, Y_K4)

        Y = [
            Y[i] + h*(K1[i] + 2*K2[i] + 2*K3[i] + K4[i])/6
            for i in range(len(Y))
        ]

        t = t + h

        t_values.append(t)
        Y_values.append(Y[:])

    return t_values, Y_values

def pretty_print_system(t_vals, Y_vals, title="Решение системы"):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

    print(f"{'t':>8} | {'y1':>12} | {'y2':>12}")
    print("-" * 70)

    for t, Y in zip(t_vals, Y_vals):
        print(f"{t:8.3f} | {Y[0]:12.6f} | {Y[1]:12.6f}")

    print("=" * 70 + "\n")

def compare_with_exact(t_vals, Y_vals, exact_func, title):

    print("\n" + "=" * 70)
    print(f" {title} — сравнение с точным решением")
    print("=" * 70)

    errors = []

    print(f"{'t':>8} | {'y_num':>12} | {'y_exact':>12} | {'error':>12}")
    print("-" * 70)

    for t, Y in zip(t_vals, Y_vals):

        y_exact = exact_func(t)[0]
        y_num = Y[0]

        error = abs(y_num - y_exact)
        errors.append(error)

        print(f"{t:8.3f} | {y_num:12.6f} | {y_exact:12.6f} | {error:12.6f}")

    print("-" * 70)
    print(f"Максимальная ошибка = {max(errors):.8f}")
    print("=" * 70 + "\n")

t0 = 0
Y0 = [1.0, 0.5]

h = 0.1
N = 30


t_vals, Y_vals = rk4_system(F1, 0, [1,0], 0.05, 50)

pretty_print_system(
    t_vals,
    Y_vals,
    "Система 1: F1(t,Y)"
)
compare_with_exact(
    t_vals,
    Y_vals,
    exact_F1,
    "Система 1"
)
t_vals, Y_vals = rk4_system(F2, 0, [1,1], 0.1, 30)

pretty_print_system(
    t_vals,
    Y_vals,
    "Система 2: F2(t,Y)"
)
compare_with_exact(
    t_vals,
    Y_vals,
    exact_F2,
    "Система 2"
)

t_vals, Y_vals = rk4_system(
    F_new,
    0,
    [1.0, 0.0],
    0.05,
    50
)

pretty_print_system(
    t_vals,
    Y_vals,
    "Система 3"
)


compare_with_exact(
    t_vals,
    Y_vals,
    exact_new,
    "Система 3"
)