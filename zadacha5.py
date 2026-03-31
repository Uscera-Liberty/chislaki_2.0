import math

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

def exact(t, x): 
    return math.exp(-math.pi**2 * t) * math.cos(math.pi * x)

def phi1(t):     
    return 0.0

def phi2(t):     
    return -math.exp(-math.pi**2 * t)

def u0(x):       
    return math.cos(math.pi * x)

def linspace(a, b, n):
    """Создаёт список из n равноотстоящих точек от a до b включительно."""
    if n < 2:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]

def solve_with_history(nx, T=0.1, save_steps=5):
    """Решает уравнение с сохранением истории по времени."""
    h = 1.0 / nx
    tau = 0.25 * h**2
    nt = int(T / tau) + 1
    tau = T / nt
    r = tau / h**2
    
    x = linspace(0, 1, nx + 1)
    u = [u0(xi) for xi in x]
    
    history_t = [0]
    history_u = [u[:]]
    
    save_interval = max(1, nt // save_steps)
    
    for k in range(nt):
        t = (k + 1) * tau
        u_new = u[:]
        
        # Внутренние узлы: явная схема
        for i in range(1, nx):
            u_new[i] = u[i] + r * (u[i-1] - 2*u[i] + u[i+1])
        
        # Правая граница: Дирихле
        u_new[nx] = phi2(t)
        
        # Левая граница: Нейман с аппроксимацией O(h^2)
        u_new[0] = (4*u_new[1] - u_new[2] - 2*h*phi1(t)) / 3.0
        
        u = u_new
        
        if (k + 1) % save_interval == 0 or (k + 1) == nt:
            history_t.append(t)
            history_u.append(u[:])
    
    return x, u, nt, r, history_t, history_u

def solve(nx, T=0.1):
    """Основной решатель уравнения теплопроводности."""
    h = 1.0 / nx
    tau = 0.25 * h**2
    nt = int(T / tau) + 1
    tau = T / nt
    r = tau / h**2
    
    x = linspace(0, 1, nx + 1)
    u = [u0(xi) for xi in x]
    
    for k in range(nt):
        t = (k + 1) * tau
        u_new = u[:]
        
        # Внутренние узлы: явная схема
        for i in range(1, nx):
            u_new[i] = u[i] + r * (u[i-1] - 2*u[i] + u[i+1])
        
        # Правая граница: Дирихле
        u_new[nx] = phi2(t)
        
        # Левая граница: Нейман с аппроксимацией O(h^2)
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
    
    # Исследование сходимости по пространству
    for nx in nxs:
        x, u, nt, r = solve(nx, T)
        u_exact = [exact(T, xi) for xi in x]
        e = max(abs(u[i] - u_exact[i]) for i in range(len(u)))
        errs.append(e)
        
        h = 1.0 / nx
        tau = T / nt
        
        print(f"nx={nx:3d}, nt={nt:6d}, h={h:.4f}, tau={tau:.2e}, r={r:.3f}, max|err|={e:.2e}")
    
    # Оценка порядка сходимости
    print()
    for i in range(1, len(nxs)):
        pr = math.log2(errs[i-1] / errs[i])
        print(f"Порядок сходимости ({nxs[i-1]}->{nxs[i]}): {pr:.2f}")
    
    # Детальный вывод для одного из расчётов
    nx_plot = 40
    x_plot, u_plot, nt_plot, r_plot = solve(nx_plot, T)
    u_exact_plot = [exact(T, xi) for xi in x_plot]
    
    print(f"\nПример решения при nx={nx_plot}:")
    print(f"{'x':>8} {'U_num':>12} {'U_exact':>12} {'Error':>12}")
    step_print = max(1, len(x_plot) // 10)
    for i in range(0, len(x_plot), step_print):
        err = abs(u_plot[i] - u_exact_plot[i])
        print(f"{x_plot[i]:8.4f} {u_plot[i]:12.6f} {u_exact_plot[i]:12.6f} {err:12.2e}")

if __name__ == "__main__":
    run()