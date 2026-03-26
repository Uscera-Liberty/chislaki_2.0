def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

def leaky_relu_derivative(x, alpha=0.01):
    return np.where(x > 0, 1.0, alpha)


class NeuronLeakyReLU:
    def __init__(self, w=None, b=0, alpha=0.01):   # ← исправили x → w
        self.w = w
        self.b = b
        self.alpha = alpha

    def activate(self, x):
        return leaky_relu(x, self.alpha)

    def forward_pass(self, X):  # ← x → X
        n = X.shape[0]
        z = X @ self.w + self.b
        y_pred = self.activate(z)
        return y_pred

    def backward_pass(self, X, y, y_pred, learning_rate=0.005):
        n = len(y)
        y = np.array(y).reshape(-1, 1)

        z = X @ self.w + self.b

        delta = (y_pred - y) * leaky_relu_derivative(z, self.alpha)

        grad_w = (X.T @ delta) / n
        grad_b = np.mean(delta)

        self.w -= learning_rate * grad_w
        self.b -= learning_rate * grad_b

    def fit(self, X, y, num_epochs=300):
        Loss_values = []
        for i in range(num_epochs):
            y_pred = self.forward_pass(X)
            Loss_values.append(Loss(y_pred, y))
            self.backward_pass(X, y, y_pred)
        return Loss_values




def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def vector_norm(v):
    return (sum(x**2 for x in v)) ** 0.5

def normalize_vector(v):
    norm = vector_norm(v)
    if norm < 1e-15:
        raise ValueError("Попытка нормализовать нулевой вектор")
    return [x / norm for x in v]

def vector_subtract(v1, v2):
    return [v1[i] - v2[i] for i in range(len(v1))]

def scalar_multiply(scalar, v):
    return [scalar * x for x in v]

def matrix_vector_multiply(A, v):
    n = len(A)
    result = [0.0] * n
    for i in range(n):
        for j in range(n):
            result[i] += A[i][j] * v[j]
    return result

def copy_matrix(A):
    return [[A[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def matrix_sub_I(A, mu):
    n = len(A)
    result = copy_matrix(A)
    for i in range(n):
        result[i][i] -= mu
    return result
# потом мы решаем методом гаусса для находждения вектора 
def solve_gaussian(A, b):
    n = len(A)
    M = copy_matrix(A)
    y = b[:]
    
    for k in range(n):
        max_row = k
        for i in range(k + 1, n):
            if abs(M[i][k]) > abs(M[max_row][k]):
                max_row = i
        
        if max_row != k:
            M[k], M[max_row] = M[max_row], M[k]
            y[k], y[max_row] = y[max_row], y[k]
        
        if abs(M[k][k]) < 1e-15:
            M[k][k] += 1e-10
        
        for i in range(k + 1, n):
            if abs(M[k][k]) < 1e-15:
                continue
            factor = M[i][k] / M[k][k]
            for j in range(k, n):
                M[i][j] -= factor * M[k][j]
            y[i] -= factor * y[k]
    
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-15:
            x[i] = 0.0
        else:
            x[i] = y[i]
            for j in range(i + 1, n):
                x[i] -= M[i][j] * x[j]
            x[i] /= M[i][i]
    
    return x
# частное релея  = (x^T Ax )/ x^T x
def rayleigh_quotient(A, x):
    Ax = matrix_vector_multiply(A, x)
    numerator = dot_product(x, Ax)
    denominator = dot_product(x, x)
    
    if abs(denominator) < 1e-15:
        raise ValueError("Знаменатель близок к нулю")
    
    return numerator / denominator

#для того чтобы делать новый вектор ортог старому(чтоб не повторяться)
def grammshidth_ortho(v, basis_vectors):
    v_orth = list(v)
    
    for basis_v in basis_vectors:
        projection = dot_product(v_orth, basis_v)
        for i in range(len(v_orth)):
            v_orth[i] -= projection * basis_v[i]
    
    norm = vector_norm(v_orth)
    if norm > 1e-12:
        v_orth = [x / norm for x in v_orth]
        
    else:
        import random
        random.seed(42)
        v_orth = [random.random() - 0.5 for _ in range(len(v))]
        return grammshidth_ortho(v_orth, basis_vectors)
    
    return v_orth

def iteration_single(A, x0=None, max_iter=100, epsilon=1e-12, verbose=True):
    n = len(A)
    
    if x0 is None:
        x = [1.0] * n
    else:
        x = list(x0)
    
    x = normalize_vector(x)
    mu_prev = 0.0
    history = []
    
    if verbose:
        print("Метод частных Рэлея")
        print(f"Размерность: {n}x{n}, точность: {epsilon}")
    
    for k in range(1, max_iter + 1):
        mu = rayleigh_quotient(A, x)
        history.append(mu)
        # A- lambda * E
        A_shifted = matrix_sub_I(A, mu)
        
        try:
            y = solve_gaussian(A_shifted, x)
        except:
            if verbose:
                print(f"Ошибка СЛАУ на итерации {k}")
            break
        
        try:
            x_new = normalize_vector(y)
        except:
            if verbose:
                print(f"Результат близок к нулю на итерации {k}")
            break
        
        error_mu = abs(mu - mu_prev)
        diff = vector_subtract(x_new, x)
        error_x = vector_norm(diff)
        
        if verbose and (k <= 5 or (error_mu < epsilon and error_x < epsilon)):
            print(f"Итерация {k}: mu = {mu:.10f}, погрешность = {error_mu:.2e}")
        
        if error_mu < epsilon and error_x < epsilon:
            if verbose:
                print(f"Сходимость на итерации {k}")
            break
        
        x = x_new
        mu_prev = mu
    
    eigenvalue = rayleigh_quotient(A, x)
    eigenvector = x
    
    if verbose:
        print(f"Собственное значение: {eigenvalue:.12f}")
        print(f"Собственный вектор: {[f'{v:.6f}' for v in eigenvector]}")
    
    return eigenvalue, eigenvector, k, history

def find_all_eigenpairs(A, epsilon=1e-10, verbose=True):
    n = len(A)
    eigenvalues = []
    eigenvectors = []
    
    if verbose:
        print(f"\nНахождение всех собственных пар матрицы {n}x{n}\n")
    
    for i in range(n):
        if verbose:
            print(f"--- Поиск пары {i+1} из {n} ---")
        
        if i == 0:
            x0 = [1.0] * n
        else:
            import random
            random.seed(42 + i)
            x0 = [random.random() - 0.5 for _ in range(n)]
            x0 = grammshidth_ortho(x0, eigenvectors)
        
        x0 = normalize_vector(x0)
        
        try:
            eigenvalue, eigenvector, iterations, history = iteration_single(
                A, x0=x0, max_iter=50, epsilon=epsilon, verbose=verbose
            )
            
            if i > 0:
                eigenvector = grammshidth_ortho(eigenvector, eigenvectors)
                eigenvector = normalize_vector(eigenvector)
                eigenvalue = rayleigh_quotient(A, eigenvector)
            
            eigenvalues.append(eigenvalue)
            eigenvectors.append(eigenvector)
            
            if verbose:
                print(f"Найдена пара {i+1}: lambda = {eigenvalue:.10f}\n")
        
        except Exception as e:
            if verbose:
                print(f"Ошибка при поиске пары {i+1}: {e}\n")
            break
    
    if verbose and len(eigenvalues) > 0:
        print("=" * 70)
        print("Финальная проверка")
        print("=" * 70)
        print(f"{'N':<4} {'Lambda':<20} {'Невязка':<15} {'Статус':<10}")
        print("-" * 70)
        
        max_residual = 0.0
        for i in range(len(eigenvalues)):
            Av = matrix_vector_multiply(A, eigenvectors[i])
            lambda_v = scalar_multiply(eigenvalues[i], eigenvectors[i])
            diff = vector_subtract(Av, lambda_v)
            residual = vector_norm(diff)
            max_residual = max(max_residual, residual)
            
            if residual < 1e-8:
                status = "OK"
            elif residual < 1e-5:
                status = "Хорошо"
            else:
                status = "Проверить"
            
            print(f"{i+1:<4} {eigenvalues[i]:<20.12f} {residual:<15.2e} {status:<10}")
        
        print("-" * 70)
        if max_residual < 1e-8:
            print("Все пары найдены с отличной точностью")
        
        if len(eigenvectors) > 1:
            print("\nОртогональность векторов:")
            print("-" * 70)
            max_dot = 0.0
            for i in range(len(eigenvectors)):
                for j in range(i + 1, len(eigenvectors)):
                    dot = abs(dot_product(eigenvectors[i], eigenvectors[j]))
                    max_dot = max(max_dot, dot)
                    status = "OK" if dot < 1e-8 else "Почти" if dot < 1e-4 else "Нет"
                    print(f"v{i+1} * v{j+1} = {dot:.8f}  ({status})")
            
            print("-" * 70)
            if max_dot < 1e-8:
                print("Все векторы ортогональны")
        
        trace = sum(A[i][i] for i in range(n))
        sum_eigenvalues = sum(eigenvalues)
        
        print(f"\nTrace(A) = {trace:.10f}")
        print(f"Sum(lambda) = {sum_eigenvalues:.10f}")
        print(f"Разница = {abs(trace - sum_eigenvalues):.2e}")
        print("=" * 70)
    
    return eigenvalues, eigenvectors

def sort_eigenvalues(eigenvalues, eigenvectors):
    indexed = [(abs(eigenvalues[i]), i) for i in range(len(eigenvalues))]
    indexed.sort(reverse=True)
    sorted_values = [eigenvalues[i] for _, i in indexed]
    sorted_vectors = [eigenvectors[i] for _, i in indexed]
    return sorted_values, sorted_vectors

def print_matrix(A, title="Матрица"):
    print(f"\n{title}:")
    for i, row in enumerate(A):
        print(f"  {row}")

if __name__ == "__main__":
    
    print("\nПРИМЕР 1: Матрица 3x3")
    print("=" * 70)
    
    A1 = [
        [4, 1, 1],
        [1, 3, 4],
        [1, 2, 2]
    ]
    
    print_matrix(A1)
    
    eigenvalues1, eigenvectors1 = find_all_eigenpairs(A1, epsilon=1e-10, verbose=True)
    eigenvalues1, eigenvectors1 = sort_eigenvalues(eigenvalues1, eigenvectors1)
    
    print("\nСпектр матрицы (отсортирован):")
    for i in range(len(eigenvalues1)):
        print(f"lambda{i+1} = {eigenvalues1[i]:15.10f}")
        print(f"v{i+1} = {[f'{x:.6f}' for x in eigenvectors1[i]]}")
    
    
    print("\n\nПРИМЕР 2: Матрица 2x2")
    print("=" * 70)
    
    A2 = [
        [4, 1],
        [1, 2]
    ]
    
    print_matrix(A2)
    
    eigenvalues2, eigenvectors2 = find_all_eigenpairs(A2, epsilon=1e-12, verbose=True)
    eigenvalues2, eigenvectors2 = sort_eigenvalues(eigenvalues2, eigenvectors2)
    
    print("\nСравнение с точным решением:")
    exact = [3 + 2**0.5, 3 - 2**0.5]
    for i in range(len(eigenvalues2)):
        error = abs(eigenvalues2[i] - exact[i])
        print(f"lambda{i+1}: найдено = {eigenvalues2[i]:.15f}, ошибка = {error:.2e}")
    
    
    print("\n\nПРИМЕР 3: Матрица 4x4")
    print("=" * 70)
    
    A3 = [
        [5, 2, 0, 0],
        [2, 6, 2, 0],
        [0, 2, 7, 2],
        [0, 0, 2, 8]
    ]
    
    print_matrix(A3)
    
    eigenvalues3, eigenvectors3 = find_all_eigenpairs(A3, epsilon=1e-10, verbose=True)
    eigenvalues3, eigenvectors3 = sort_eigenvalues(eigenvalues3, eigenvectors3)
    
    print("\nСпектр матрицы 4x4:")
    for i in range(len(eigenvalues3)):
        print(f"lambda{i+1} = {eigenvalues3[i]:15.10f}")
        print(f"v{i+1} = {[f'{x:.6f}' for x in eigenvectors3[i]]}")
