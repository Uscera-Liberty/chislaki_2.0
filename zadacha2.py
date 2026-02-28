import math

def f(t, y):
    return y - t**2 + 1

def exact_solution(t):
    return (t+1)**2 + 0.5*math.exp(t)

def f1(t, y):
    return -2*y

def exact1(t):
    return math.exp(-2*t) * 1.0

def f2(t, y):
    return math.sin(t)

def exact2(t):
    return 1 - math.cos(t)


def norm(v):
    return sum(x**2 for x in v) ** 0.5

def runge_kutta4(f, t0, y0, h, n):
    t_values = [t0]
    y_values = [y0]

    t = t0
    y = y0

    for _ in range(n):

        k1 = f(t, y)
        k2 = f(t + h/2, y + h*k1/2)
        k3 = f(t + h/2, y + h*k2/2)
        k4 = f(t + h, y + h*k3)

        y = y + h*(k1 + 2*k2 + 2*k3 + k4)/6
        t = t + h

        t_values.append(t)
        y_values.append(y)

    return t_values, y_values

def pretty_print_table(t_values, y_values, title, n=None):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if n is None:
        n = len(t_values)

    print("   t\t\t y")
    print("-" * 60)

    print("".join([f"{t_values[i]:.6f}\t{y_values[i]:.6f}\n"
                   for i in range(min(n, len(t_values)))]))

    print("=" * 60)
t0 = 0
y0 = 0.5
h = 0.1
N = 20

t_h, y_h = runge_kutta4(f, t0, y0, h, N)

pretty_print_table(
    t_h,
    y_h,
    "Решение задачи 1 методом Рунге–Кутты 4-го порядка",
    N
)

t_h2, y_h2 = runge_kutta4(f, t0, y0, h/2, 2*N)

pretty_print_table(
    t_h2,
    y_h2,
    "Решение задачи 1 (шаг h/2)",
    2*N
)

y_exact = [exact_solution(t) for t in t_h]
y_exact2 = [exact_solution(t) for t in t_h2]

error = norm([yh - ye for yh, ye in zip(y_h, y_exact)])
error2 = norm([yh - ye for yh, ye in zip(y_h, y_exact2)])

print("\n" + "=" * 60)
print("НОРМА ПОГРЕШНОСТИ")
print("=" * 60)

print(f"Ошибка (шаг h)     = {error:.10f}")
print(f"Ошибка (шаг h/2)   = {error2:.10f}")
print("=" * 60)


t, y = runge_kutta4(f1, 0, 1, 0.1, 30)

pretty_print_table(
    t,
    y,
    "Решение задачи 2: f1(t,y)",
    len(t)
)

print("\nОшибка относительно точного решения:")
print("".join([f"|y_num - y_exact| = {abs(y[i]-exact1(t[i])):.8f}\n"
               for i in range(len(t))]))

t2, y2 = runge_kutta4(f2, 0, 0, 0.05, 15)

pretty_print_table(
    t2,
    y2,
    "Решение задачи 3: f2(t,y)",
    len(t2)
)

print("\nОшибка относительно точного решения:")
print("".join([f"|y_num - y_exact| = {abs(y2[i]-exact2(t2[i])):.8f}\n"
               for i in range(len(t2))]))
