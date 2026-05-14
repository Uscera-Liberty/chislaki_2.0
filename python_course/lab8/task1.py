"""
адание 1:
  Вывести список слушателей в порядке возрастания затраченного времени.
  Указать Фамилию, Имя, время, итоговую оценку.
"""

import csv
import re

def parse_time_to_seconds(time_str: str) -> int:
    #Преобразует строку вида '12 мин. 28 сек.' в количество секунд.
    time_str = time_str.strip()
    total = 0

    # Часы
    match = re.search(r'(\d+)\s*ч', time_str)
    if match:
        total += int(match.group(1)) * 3600

    # Минуты
    match = re.search(r'(\d+)\s*мин', time_str)
    if match:
        total += int(match.group(1)) * 60

    # Секунды
    match = re.search(r'(\d+)\s*сек', time_str)
    if match:
        total += int(match.group(1))

    return total


def seconds_to_str(seconds: int) -> str:
    #секунды обратно в читаемую строку 'X мин. Y сек.
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if hours:
        parts.append(f"{hours} ч.")
    if minutes:
        parts.append(f"{minutes} мин.")
    parts.append(f"{secs} сек.")
    return " ".join(parts)


CSV_FILE = "10.csv"  

def load_data(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def task10(rows: list[dict]) -> None:
    print("=" * 65)
    print("Список слушателей в порядке возрастания затраченного времени")
    print("=" * 65)

    valid = []
    for row in rows:
        time_str = row.get("Затраченное время", "").strip()
        if not time_str:
            continue
        seconds = parse_time_to_seconds(time_str)
        score_raw = row.get("Оценка/10,00", "").replace(",", ".").strip()
        try:
            score = float(score_raw)
        except ValueError:
            score = 0.0

        valid.append({
            "Фамилия": row["Фамилия"].strip(),
            "Имя":     row["Имя"].strip(),
            "seconds": seconds,
            "time_str": time_str,
            "score":   score,
        })

    valid.sort(key=lambda x: x["seconds"])

    print(f"\n{'Номер':<4} {'Фамилия':<20} {'Имя':<15} {'Время':<22} {'Оценка':>7}")
    print("-" * 70)
    for i, person in enumerate(valid, start=1):
        print(
            f"{i:<4} "
            f"{person['Фамилия']:<20} "
            f"{person['Имя']:<15} "
            f"{person['time_str']:<22} "
            f"{person['score']:>7.2f}"
        )

    print(f"\nВсего записей: {len(valid)}")

    if valid:
        fastest = valid[0]
        slowest = valid[-1]
        print(f"\nБыстрее всех: {fastest['Фамилия']} {fastest['Имя']} "
              f"— {fastest['time_str']} (оценка {fastest['score']:.2f})")
        print(f"Дольше всех:  {slowest['Фамилия']} {slowest['Имя']} "
              f"— {slowest['time_str']} (оценка {slowest['score']:.2f})")

if __name__ == "__main__":
    data = load_data(CSV_FILE)
    task10(data)