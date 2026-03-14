import numpy as np

# ============================================================
# ЗАДАЧА 5, задание 3д: Уравнение теплопроводности 1D
# dU/dt = d^2U/dx^2,   x in [0,1],  t in [0, T]
#
# Граничные условия:
#   U'_x(t, 0) = phi1(t)  -- Неймана на левой границе
#   U(t, 1)    = phi2(t)  -- Дирихле на правой границе
#
# Аппроксимация производной U'_x(t,0) с погрешностью O(h^2):
#   (-3*u_0 + 4*u_1 - u_2) / (2h) = phi1
#   => u_0 = (4*u_1 - u_2 - 2h*phi1) / 3
#
# Явная схема (условие устойчивости: r = tau/h^2 <= 0.5)
#
# Конкретный пример:
#   Точное: U(t,x) = e^{-pi^2*t} * cos(pi*x)
#   phi1(t) = U'_x(t,0) = 0
#   phi2(t) = U(t,1) = -e^{-pi^2*t}
#   НУ: U(0,x) = cos(pi*x)
# ============================================================

def exact(t, x): return np.exp(-np.pi**2 * t) * np.cos(np.pi * x)
def phi1(t):     return 0.0
def phi2(t):     return -np.exp(-np.pi**2 * t)
def u0(x):       return np.cos(np.pi * x)

def solve(nx, T=0.1):
    h   = 1.0 / nx
    # Выбираем tau так чтобы r=0.25 < 0.5 (условие устойчивости)
    tau = 0.25 * h**2
    nt  = int(T / tau) + 1
    tau = T / nt          # пересчитываем точно чтобы попасть ровно в T
    r   = tau / h**2

    x = np.linspace(0, 1, nx + 1)
    u = u0(x).copy()     # начальное условие

    for k in range(nt):
        t     = (k + 1) * tau
        u_new = u.copy()

        # Явная схема для внутренних узлов i=1..nx-1:
        # u_i^{k+1} = u_i^k + r*(u_{i-1}^k - 2*u_i^k + u_{i+1}^k)
        for i in range(1, nx):
            u_new[i] = u[i] + r * (u[i-1] - 2*u[i] + u[i+1])

        # Правое ГУ Дирихле: U(t,1) = phi2(t)
        u_new[nx] = phi2(t)

        # Левое ГУ Неймана O(h^2):
        # (-3*u_0 + 4*u_1 - u_2) / (2h) = phi1
        # => u_0 = (4*u_1 - u_2 - 2h*phi1) / 3
        u_new[0] = (4*u_new[1] - u_new[2] - 2*h*phi1(t)) / 3.0

        u = u_new

    return x, u, nt, r

def run():
    T = 0.1
    print("=" * 60)
    print("УРАВНЕНИЕ ТЕПЛОПРОВОДНОСТИ: dU/dt = d^2U/dx^2")
    print("ГУ: U'_x(t,0)=0 (Неймана, O(h^2))")
    print("    U(t,1)=-e^{-pi^2*t} (Дирихле)")
    print("НУ: U(0,x)=cos(pi*x)")
    print("Точное: U = e^{-pi^2*t} * cos(pi*x)")
    print("Явная схема, r = tau/h^2 = 0.25 < 0.5")
    print("=" * 60)

    nxs = [20, 40, 80]
    errs = []
    for nx in nxs:
        x, u, nt, r = solve(nx, T)
        e = np.max(np.abs(u - exact(T, x)))
        errs.append(e)
        h = 1.0/nx; tau = T/nt
        print(f"nx={nx:3d}, nt={nt:6d},  h={h:.4f}, tau={tau:.2e}, r={r:.3f},  max|err|={e:.2e}")

    print()
    for i in range(1, len(nxs)):
        pr = np.log2(errs[i-1] / errs[i])
        print(f"Порядок сходимости ({nxs[i-1]}->{nxs[i]}): {pr:.2f}")

run()