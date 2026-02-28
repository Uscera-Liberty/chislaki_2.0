df['tr_day'] = df['tr_day'].astype(int)

mcc_counts = df['mcc_code'].value_counts()
popular_mcc = mcc_counts[mcc_counts > 60000].index
df_filtered = df[df['mcc_code'].isin(popular_mcc)]

grouped = (df_filtered.groupby(['tr_day', 'mcc_code'])['amount'].mean().unstack())

mcc_labels = {
    4814: "Телеком",
    4829: "Денежные переводы",
    5411: "Бакалейные магазины",
    6010: "Финансовые институты",
    6011: "Снятие наличных (ATM)"
}
grouped = grouped.rename(columns=mcc_labels)
plt.figure(figsize=(12,6))

grouped.plot(ax=plt.gca())

plt.axhline(0, color='black', linewidth=1)

plt.xlabel("Day")
plt.ylabel("Average transaction amount")
plt.title("MCC code average amount dynamics by day")

# Легенда снизу
plt.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, -0.15),
    ncol=2,
    frameon=False
)

plt.tight_layout()
plt.show()

titanic['Age_group'] = pd.cut(
    titanic['Age'],
    bins=[0, 12, 18, 35, 60, 100],
    labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
)
age_surv = titanic.groupby('Survived')['Age'].mean()
print(round(age_surv, 2))


def matrix_multipli(A, v):
    n = len(A)
    result = [0.0]*n
    for i in range(n):
        for j in range(n):
            result[i] += A[i][j] * v[j]
    return result

def vector_norm(v):
    return sum(x**2 for x in v) ** 0.5

def normalize(v):
    norm = vector_norm(v)
    if norm == 0:
        raise ValueError("Нельзя нормализовать нулевой вектор")
    return [x/norm for x in v]

def skalar_product(v1,v2):
    return sum(a*b for a,b in zip(v1,v2))

def power_method(A, max_iter=1000, epsilon=1e-10, initial_vector=None, verbose=True):
    
    n = len(A)

    if not all(len(row) == n for row in A):
        raise ValueError("Матрица должна быть квадратной")

    if initial_vector is None:
        y_current = [1.0] * n
    else:
        if len(initial_vector) != n:
            raise ValueError(f"Длина начального вектора должна быть {n}")
        y_current = list(initial_vector)

    y_current = normalize(y_current)
    
    lambda_prev = 0.0
    history = []

    
    for k in range(1, max_iter + 1):
        # Шаг 1: z^(k) = A · y^(k-1)
        z = matrix_multipli(A, y_current)
 
        y_next = normalize(z)

        # lambda^(k) = (y^(k))ᵀ · A · y^(k) - формула Рэлея
        Ay = matrix_multipli(A, y_next)
        lambda_current = skalar_product(y_next, Ay)
        
        history.append(lambda_current)

        error = abs(lambda_current - lambda_prev)
        
        if (k <= 10 or k % 10 == 0 or error < epsilon):
            print(f"Итерация {k:4d}: λ = {lambda_current:12.8f}, "
                  f"погрешность = {error:.2e}")
        
        if error < epsilon:
            print("-" * 70)
            print(f"Сходимость достигнута на итерации {k}")
            break
        
        y_current = y_next
        lambda_prev = lambda_current
    else:
        print("-" * 70)
        print(f"⚠Достигнуто максимальное число итераций ({max_iter})")
    
    print("=" * 70)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 70)
    print(f"Старшее собственное значение λ₁ = {lambda_current:.10f}")
    print(f"Старший собственный вектор y₁:")
    for i, val in enumerate(y_current):
        print(f"  y₁[{i}] = {val:12.8f}")
    print("=" * 70)
    
    return lambda_current, y_current, k, history

def verify_pair(A, eigenvalue, eigenvector, verbose=True):
    n = len(A)
    Ay = matrix_vector_multiply(A, eigenvector)
    lambda_y = [eigenvalue * eigenvector[i] for i in range(n)]

    diff = [Ay[i] - lambda_y[i] for i in range(n)]
    residual = vector_norm(diff)
    
    if verbose:
        print("\n" + "=" * 70)
        print("ПРОВЕРКА СОБСТВЕННОЙ ПАРЫ")
        print("=" * 70)
        print("Должно выполняться: A·y = λ·y")
        print(f"\nA·y = {[f'{x:.8f}' for x in Ay]}")
        print(f"λ·y = {[f'{x:.8f}' for x in lambda_y]}")
        print(f"\nНевязка ||A·y - λ·y|| = {residual:.2e}")
        
        if residual < 1e-8:
            print("✓ Собственная пара найдена ТОЧНО!")
        elif residual < 1e-5:
            print("✓ Собственная пара найдена с хорошей точностью")
        else:
            print("⚠ Возможно, требуется больше итераций")
        print("=" * 70)
    
    return residual

if __name__ == "__main__":
    A1 = [
        [4, 1, 1],
        [1, 3, 2],
        [1, 2, 2]
    ]
    
    print("Матрица A:")
    for row in A1:
        print("  ", row)
    print()
    
    # Решение
    lambda1, y1, iterations, history = power_method(A1, epsilon=1e-10)
    verify_pair(A1, lambda1, y1)

    A2 = [
        [2, -1, 0, 0],
        [-1, 2, -1, 0],
        [0, -1, 2, -1],
        [0, 0, -1, 2]
    ]
    
    print("Матрица A:")
    for row in A2:
        print("  ", row)
    print()

    lambda2, y2, iterations2, history2 = power_method(A2, epsilon=1e-12)
    verify_pair(A2, lambda2, y2)

    A3 = [
        [5, 2, 0],
        [2, 6, 2],
        [0, 2, 7]
    ]
    
    print("Матрица A:")
    for row in A3:
        print("  ", row)
    print()
    
    lambda3, y3, iterations3, history3 = power_method(A3, epsilon=1e-10)
    verify_pair(A3, lambda3, y3)
