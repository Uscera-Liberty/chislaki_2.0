"""
задание 2, пункт 10:
  Найти количество супермаркетов каждой из торговых сетей
  (Пятёрочка, Магнит, Лента и др.) на заданном участке карты.
"""

import xml.etree.ElementTree as ET
from collections import Counter


def get_tags(element) -> dict:
    #Возвращает словарь тегов для XML-элемента OSM.
    return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}


def load_osm(filepath: str):
    #Парсит OSM-файл и возвращает корневой элемент.
    try:
        tree = ET.parse(filepath)
        return tree.getroot()
    except FileNotFoundError:
        print(f"Файл не найден: {filepath}")
        return None
    except ET.ParseError as e:
        print(f"Ошибка разбора XML в файле {filepath}: {e}")
        return None

# Ключевые слова → название сети
CHAIN_KEYWORDS = {
    "пятёрочка":    "Пятёрочка",
    "пятерочка":    "Пятёрочка",
    "pyaterochka":  "Пятёрочка",
    "5ka":          "Пятёрочка",

    "магнит":       "Магнит",
    "magnit":       "Магнит",

    "лента":        "Лента",
    "lenta":        "Лента",

    "перекрёсток":  "Перекрёсток",
    "perekrestok":  "Перекрёсток",

    "ашан":         "Ашан",
    "auchan":       "Ашан",

    "карусель":     "Карусель",
    "karusel":      "Карусель",

    "окей":         "О'КЕЙ",
    "o'key":        "О'КЕЙ",
    "okey":         "О'КЕЙ",

    "дикси":        "Дикси",
    "dixy":         "Дикси",
    "dixie":        "Дикси",

    "билла":        "Билла",
    "billa":        "Билла",

    "spar":         "SPAR",
    "спар":         "SPAR",

    "metro":        "Metro C&C",
    "метро":        "Metro C&C",

    "fixprice":     "Fix Price",
    "fix price":    "Fix Price",

    "верный":       "Верный",
    "verniy":       "Верный",

    "семёрочка":    "Семёрочка",
    "семерочка":    "Семёрочка",
}


def normalize_chain(name: str) -> str:
    if not name:
        return "Прочее / неизвестно"
    name_lower = name.lower()
    for keyword, chain in CHAIN_KEYWORDS.items():
        if keyword in name_lower:
            return chain
    return f"Другое: {name}"


def is_supermarket(tags: dict) -> bool:
    shop = tags.get("shop", "").lower()
    return shop in ("supermarket", "grocery")


def process_file(root, filename: str, chains: Counter, raw_names: list):
    count = 0
    for element in root.iter():
        if element.tag not in ("node", "way", "relation"):
            continue
        tags = get_tags(element)
        if not is_supermarket(tags):
            continue

        name = tags.get("name", tags.get("name:ru", "")).strip()
        chain = normalize_chain(name)
        chains[chain] += 1
        raw_names.append((name or "(без названия)", chain, filename))
        count += 1
    return count


def task10_osm(files: list[str]) -> None:
    print("=" * 65)
    print("Количество супермаркетов по торговым сетям")
    print("=" * 65)

    chains: Counter = Counter()
    raw_names: list = []
    total = 0

    for filepath in files:
        root = load_osm(filepath)
        if root is None:
            continue
        n = process_file(root, filepath, chains, raw_names)
        print(f"\nФайл: {filepath} найдено супермаркетов: {n}")
        total += n

    if total == 0:
        print("\nСупермаркеты не найдены (возможно, файлы ещё не скачаны).")
        return

    print(f"\n{'Торговая сеть':<30} {'Количество':>10}")
    print("-" * 42)
    for chain, cnt in sorted(chains.items(), key=lambda x: -x[1]):
        print(f"{chain:<30} {cnt:>10}")
    print("-" * 42)
    print(f"{'ИТОГО':.<30} {total:>10}")

    print("\nПодробный список всех супермаркетов:")
    print(f"{'№':<4} {'Название':<35} {'Сеть':<25} {'Файл'}")
    print("-" * 80)
    for i, (name, chain, src) in enumerate(sorted(raw_names, key=lambda x: x[1]), 1):
        print(f"{i:<4} {name:<35} {chain:<25} {src}")


if __name__ == "__main__":
    OSM_FILES = ["10.osm", "10-2.osm"]
    task10_osm(OSM_FILES)