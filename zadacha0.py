"""
Лабораторная работа №8. Вариант 10.
Задание 2, пункт 10:
  Найти количество супермаркетов каждой из торговых сетей
  (Пятёрочка, Магнит, Лента и др.) на заданном участке карты.

Файлы: 10.osm и 10-2.osm
Положите их в ту же папку, что и этот скрипт, и запустите:
  python lab8_task2_variant10.py

Участок карты берётся АВТОМАТИЧЕСКИ из тега <bounds> в самом OSM-файле.
Если тег <bounds> отсутствует — берутся min/max координат всех узлов файла.
Никаких изменений в коде делать не нужно.
"""

import xml.etree.ElementTree as ET
from collections import Counter

# ─────────────────────────────────────────────────────────────
# Названия файлов (лежат рядом со скриптом)
# ─────────────────────────────────────────────────────────────
OSM_FILES = ["10.osm", "10-2.osm"]

# ─────────────────────────────────────────────────────────────
# Словарь торговых сетей: ключевое слово → название сети
# ─────────────────────────────────────────────────────────────
CHAIN_KEYWORDS = {
    "пятёрочка":     "Пятёрочка",
    "пятерочка":     "Пятёрочка",
    "pyaterochka":   "Пятёрочка",
    "магнит":        "Магнит",
    "magnit":        "Магнит",
    "лента":         "Лента",
    "lenta":         "Лента",
    "перекрёсток":   "Перекрёсток",
    "perekrestok":   "Перекрёсток",
    "ашан":          "Ашан",
    "auchan":        "Ашан",
    "карусель":      "Карусель",
    "окей":          "О'КЕЙ",
    "o'key":         "О'КЕЙ",
    "okey":          "О'КЕЙ",
    "дикси":         "Дикси",
    "dixy":          "Дикси",
    "spar":          "SPAR",
    "спар":          "SPAR",
    "metro":         "Metro C&C",
    "fix price":     "Fix Price",
    "fixprice":      "Fix Price",
    "верный":        "Верный",
    "вкусвилл":      "ВкусВилл",
    "vkusvill":      "ВкусВилл",
    "глобус":        "Глобус",
    "билла":         "Билла",
    "billa":         "Билла",
    "семёрочка":     "Семёрочка",
    "семерочка":     "Семёрочка",
    "мираторг":      "Мираторг",
    "красное&белое": "Красное&Белое",
    "красное белое": "Красное&Белое",
    "простор":       "Простор",
}


def get_tags(element) -> dict:
    return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}


def normalize_chain(name: str) -> str:
    if not name:
        return "Без названия / неизвестно"
    low = name.lower()
    for keyword, chain in CHAIN_KEYWORDS.items():
        if keyword in low:
            return chain
    return f"Другое ({name})"


def get_node_coords(root) -> dict:
    coords = {}
    for node in root.findall("node"):
        nid = node.get("id")
        lat = node.get("lat")
        lon = node.get("lon")
        if nid and lat and lon:
            coords[nid] = (float(lat), float(lon))
    return coords


def get_way_center(way, node_coords: dict):
    lats, lons = [], []
    for nd in way.findall("nd"):
        ref = nd.get("ref")
        if ref in node_coords:
            lat, lon = node_coords[ref]
            lats.append(lat)
            lons.append(lon)
    if lats:
        return sum(lats) / len(lats), sum(lons) / len(lons)
    return None, None


def get_bbox_from_file(root, node_coords: dict):
    """
    Читает bbox прямо из OSM-файла (тег <bounds>).
    Если его нет — вычисляет по координатам всех узлов.
    Это и есть «заданный участок карты».
    """
    bounds = root.find("bounds")
    if bounds is not None:
        return (float(bounds.get("minlat")),
                float(bounds.get("minlon")),
                float(bounds.get("maxlat")),
                float(bounds.get("maxlon")))
    if not node_coords:
        return None
    lats = [c[0] for c in node_coords.values()]
    lons = [c[1] for c in node_coords.values()]
    return min(lats), min(lons), max(lats), max(lons)


def point_in_bbox(lat, lon, bbox):
    if lat is None or lon is None or bbox is None:
        return True
    minlat, minlon, maxlat, maxlon = bbox
    return minlat <= lat <= maxlat and minlon <= lon <= maxlon


def is_supermarket(tags: dict) -> bool:
    shop = tags.get("shop", "").lower()
    return shop in ("supermarket", "grocery", "convenience")


def process_file(filepath: str, chains: Counter, all_stores: list) -> int:
    print(f"\n📂 Обрабатываем файл: {filepath}")
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"   ⚠️  Файл не найден: {filepath}")
        print("      Скачайте по ссылке: https://cloud.mail.ru/public/XgEn/ybFcC2jzW")
        print("      и положите рядом с этим скриптом.")
        return 0
    except ET.ParseError as e:
        print(f"   ❌ Ошибка разбора XML: {e}")
        return 0

    node_coords = get_node_coords(root)
    bbox = get_bbox_from_file(root, node_coords)

    if bbox:
        print(f"   📍 Участок карты: "
              f"lat [{bbox[0]:.5f} … {bbox[2]:.5f}], "
              f"lon [{bbox[1]:.5f} … {bbox[3]:.5f}]")
    else:
        print("   📍 Участок карты: не определён, берём все объекты файла")

    count = 0

    # node
    for node in root.findall("node"):
        tags = get_tags(node)
        if not is_supermarket(tags):
            continue
        lat = float(node.get("lat", 0))
        lon = float(node.get("lon", 0))
        if not point_in_bbox(lat, lon, bbox):
            continue
        name = tags.get("name", tags.get("name:ru", "")).strip()
        chain = normalize_chain(name)
        chains[chain] += 1
        all_stores.append((name or "—", chain, filepath))
        count += 1

    # way (здания)
    for way in root.findall("way"):
        tags = get_tags(way)
        if not is_supermarket(tags):
            continue
        lat, lon = get_way_center(way, node_coords)
        if not point_in_bbox(lat, lon, bbox):
            continue
        name = tags.get("name", tags.get("name:ru", "")).strip()
        chain = normalize_chain(name)
        chains[chain] += 1
        all_stores.append((name or "—", chain, filepath))
        count += 1

    # relation
    for rel in root.findall("relation"):
        tags = get_tags(rel)
        if not is_supermarket(tags):
            continue
        name = tags.get("name", tags.get("name:ru", "")).strip()
        chain = normalize_chain(name)
        chains[chain] += 1
        all_stores.append((name or "—", chain, filepath))
        count += 1

    print(f"   ✅ Найдено супермаркетов: {count}")
    return count


def main():
    print("=" * 65)
    print("ЗАДАНИЕ 2, ПУНКТ 10 — Вариант 10")
    print("Количество супермаркетов по торговым сетям")
    print("на заданном участке карты")
    print("=" * 65)

    chains: Counter = Counter()
    all_stores: list = []
    total = 0

    for filepath in OSM_FILES:
        total += process_file(filepath, chains, all_stores)

    print()
    if total == 0:
        print("Супермаркеты не найдены.")
        print("Проверьте, что файлы 10.osm и 10-2.osm лежат рядом со скриптом.")
        return

    # Таблица по сетям
    print("=" * 45)
    print("ИТОГ: КОЛИЧЕСТВО ПО ТОРГОВЫМ СЕТЯМ")
    print("=" * 45)
    print(f"{'Торговая сеть':<30} {'Кол-во':>6}")
    print("-" * 45)
    for chain, cnt in sorted(chains.items(), key=lambda x: -x[1]):
        print(f"{chain:<30} {cnt:>6}")
    print("-" * 45)
    print(f"{'ИТОГО':<30} {total:>6}")

    # Подробный список
    print()
    print("=" * 65)
    print("ПОДРОБНЫЙ СПИСОК ВСЕХ СУПЕРМАРКЕТОВ")
    print("=" * 65)
    print(f"{'№':<4} {'Название':<35} {'Торговая сеть':<25} {'Файл'}")
    print("-" * 80)
    for i, (name, chain, src) in enumerate(
            sorted(all_stores, key=lambda x: x[1]), start=1):
        print(f"{i:<4} {name:<35} {chain:<25} {src}")


if __name__ == "__main__":
    main()