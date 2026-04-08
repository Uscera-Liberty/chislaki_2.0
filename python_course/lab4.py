import sys

def pervaya(path: str) -> int:
    """
    Читает файл с количеством пунктов N и весами мусора w[0..N-1].
    Возвращает номер пункта (с 1), рядом с которым выгоднее всего
    поставить завод (минимальная суммарная стоимость доставки).

    Алгоритм:
    - Стоимость доставки из пункта i в завод в пункте j на кольце длиной N:
        min(|i-j|, N - |i-j|)
    - Используем технику скользящего окна / пересчёта:
        При сдвиге завода на 1 позицию вперёд по кольцу стоимость меняется на:
        cur_cost += total - 2 * front
        где front — сумма весов «перед» заводом (в полукольце справа от него).
    """
    with open(path, "r", encoding="utf-8") as f:
        n = int(f.readline())
        w = [int(f.readline()) for _ in range(n)]

    total = sum(w)

    cur_cost = sum(w[i] * min(i, n - i) for i in range(n))

    best_pos = 1          # номер пункта с 1
    best_cost = cur_cost

    half = n // 2
    front = sum(w[1: half + 1])

    for c in range(n - 1):
        cur_cost += total - 2 * front
        front = front - w[(c + 1) % n] + w[(c + half + 1) % n]
        if cur_cost < best_cost:
            best_cost = cur_cost
            best_pos = c + 2  # следующий пункт, нумерация с 1

    return best_pos


# ─────────────────────────────────────────────────────────────
# ЗАДАНИЕ 2
# Вариант 10: Подсчитать слова, начинающиеся с заданной буквы
# ─────────────────────────────────────────────────────────────
def vtoraya(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Первая строка — буква
    letter = lines[0].strip().lower()

    # Остальное — текст
    text = " ".join(lines[1:]).lower()

    # Убираем знаки препинания
    for ch in ".,!?;:-()\"'«»—":
        text = text.replace(ch, " ")

    words = text.split()
    count = sum(1 for word in words if len(word) > 0 and word[0] == letter)
    return count


# ─────────────────────────────────────────────────────────────
# ЗАДАНИЕ 3
# Вариант 1: Беркомнадзор — оптимизация чёрного списка IPv4
# ─────────────────────────────────────────────────────────────
def ip_to_int(ip: str) -> int:
    a, b, c, d = map(int, ip.split('.'))
    return (a << 24) + (b << 16) + (c << 8) + d

def int_to_ip(x: int) -> str:
    return f"{(x>>24)&255}.{(x>>16)&255}.{(x>>8)&255}.{x&255}"

def subnet_to_range(subnet: str):
    if '/' in subnet:
        ip, mask = subnet.split('/')
        mask = int(mask)
        start = ip_to_int(ip) & (~0 << (32 - mask) & 0xFFFFFFFF)
        end = start | ((1 << (32 - mask)) - 1)
    else:
        start = end = ip_to_int(subnet)
    return start, end

def range_to_subnets(start: int, end: int):
    result = []
    while start <= end:
        max_size = 32
        # Находим максимальную маску, которая выравнивает стартовый адрес
        while max_size > 0:
            mask = (1 << (32 - max_size))
            if start % mask != 0:
                break
            max_size -= 1
        max_len = max_size + 1

        # Уменьшаем маску, если блок выходит за предел end
        while max_len <= 32:
            block = 1 << (32 - max_len)
            if start + block - 1 > end:
                max_len += 1
            else:
                break

        result.append(f"{int_to_ip(start)}/{max_len}")
        start += 1 << (32 - max_len)
    return result

def merge_ranges(ranges):
    if not ranges:
        return []
    ranges.sort()
    merged = [ranges[0]]
    for s, e in ranges[1:]:
        if s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged

def tretya(path: str):
    black, white = [], []

    with open(path, 'r', encoding='utf-8') as f:
        n = int(f.readline())
        for _ in range(n):
            line = f.readline().strip()
            sign, subnet = line[0], line[1:]
            rng = subnet_to_range(subnet)
            if sign == '-':
                black.append(rng)
            else:
                white.append(rng)

    black = merge_ranges(black)
    white = merge_ranges(white)

    # Проверка пересечения
    bi, wi = 0, 0
    while bi < len(black) and wi < len(white):
        bl, br = black[bi]
        wl, wr = white[wi]
        if br < wl:
            bi += 1
        elif wr < bl:
            wi += 1
        else:
            print(-1)
            return

    # Вычитаем белые диапазоны из черных
    result = []
    wi = 0
    for bl, br in black:
        cur = bl
        while wi < len(white) and white[wi][1] < cur:
            wi += 1
        wj = wi
        while wj < len(white) and white[wj][0] <= br:
            wl, wr = white[wj]
            if cur < wl:
                result.append((cur, wl - 1))
            cur = max(cur, wr + 1)
            wj += 1
        if cur <= br:
            result.append((cur, br))

    # Преобразуем диапазоны в минимальные CIDR-блоки
    output = []
    for s, e in result:
        output.extend(range_to_subnets(s, e))

    print(len(output))
    for subnet in output:
        print(subnet)

# ─────────────────────────────────────────────────────────────
# Точка входа
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Задание 1 ===")
    #print("Результат для файла A:", pervaya("27-99a.txt"))
    #print("Результат для файла B:", pervaya("27-99b.txt"))

    print("\n=== Задание 2 ===")
    print("Количество слов:", vtoraya("input.txt"))

    print("\n=== Задание 3 ===")
    tretya("input2.txt")