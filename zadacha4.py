import numpy as np

# ============================================================
# МЕТОД ПРОГОНКИ
# y'' + p(x)*y' + q(x)*y = f(x)
#
# Граничные условия
# y'(a) = alpha
# y(b)  = beta
# ============================================================


def solve(n, a_bc, b_bc, alpha, beta, p, q, f):

    h = (b_bc - a_bc) / n
    x = np.linspace(a_bc, b_bc, n + 1)

    N = n + 1
    MAT = np.zeros((N, N))
    RHS = np.zeros(N)

    # --- левое граничное условие (Неймана) ---
    MAT[0,0] = -3.0
    MAT[0,1] = 4.0
    MAT[0,2] = -1.0
    RHS[0] = 2*h*alpha

    # --- внутренние узлы ---
    for i in range(1,n):

        pi_ = p(x[i])

        MAT[i,i-1] = 1/h**2 - pi_/(2*h)
        MAT[i,i]   = -2/h**2 + q(x[i])
        MAT[i,i+1] = 1/h**2 + pi_/(2*h)

        RHS[i] = f(x[i])

    # --- правое граничное условие (Дирихле) ---
    MAT[n,n] = 1
    RHS[n] = beta

    y = np.linalg.solve(MAT,RHS)

    return x,y


def run_example(name,a_bc,b_bc,alpha,beta,p,q,f,exact):

    print("\n"+"="*60)
    print(name)
    print("="*60)

    ns=[10,20,40,80]

    errs=[]

    for n in ns:

        x,y=solve(n,a_bc,b_bc,alpha,beta,p,q,f)

        e=np.max(np.abs(y-exact(x)))
        errs.append(e)

        print(f"n={n:3d}, h={(b_bc-a_bc)/n:.5f}, max|err|={e:.2e}")

    print()

    for i in range(1,len(ns)):

        pr=np.log2(errs[i-1]/errs[i])
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
        0,np.pi,
        0.5,0,
        lambda x:0,
        lambda x:-1,
        lambda x:-np.sin(x),
        lambda x:np.sin(x)/2
    )

    # ===============================
    # ПРИМЕР 2
    # y'' - y = 0
    # y'(0)=1
    # y(1)=e
    # ===============================

    run_example(
        "Пример 2: y'' - y = 0,  y'(0)=1, y(1)=e",
        0,1,
        1,np.e,
        lambda x:0,
        lambda x:-1,
        lambda x:0,
        lambda x:np.exp(x)
    )

    # ===============================
    # ПРИМЕР 3
    # y'' + y = 0
    # y'(0)=1
    # y(pi)=0
    # ===============================

    run_example(
        "Пример 3: y'' + y = 0,  y'(0)=1, y(pi)=0",
        0,np.pi,
        1,0,
        lambda x:0,
        lambda x:1,
        lambda x:0,
        lambda x:np.sin(x)
    )


run()