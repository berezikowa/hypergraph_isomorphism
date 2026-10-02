#!/usr/bin/env python3

"""
Реализация проверки двух гиперграфов отношений на изоморфизм.
Алгоритм из статьи: T. Kosovskaya, "On the isomorphism of hypergraphs of relations".
Случай коммутативных рёбер фиксированной арности (раздел 3.2).
"""

from itertools import permutations, product
from collections import Counter

# Разбор входных данных
def parse_edges(text):
    """
    Каждая строка — одно ребро; вершины через запятую или пробел. Пустая строка — конец. Пример:
    a2 a4 a5
    a1 a5 a6
    a1 a2 a3
    a3 a4 a5
    a1 a4 a6
    """
    edges = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        line = line.strip('{}')
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
        else:
            parts = line.split()
        parts = [p for p in parts if p]
        if parts:
            edges.append(tuple(parts))
    return edges

"""
def deduplicate_edges(edges):
    # Убрать дублирующиеся рёбра
    seen, result = set(), []
    for e in edges:
        key = frozenset(e)
        if key not in seen:
            seen.add(key)
            result.append(e)
    return result
"""

# Характеристики и mapping
def compute_characteristics(edges):
    chars = {}
    for edge in edges:
        for v in edge:
            chars[v] = chars.get(v, 0) + 1
    return chars


def build_mapping(chars_H, chars_G):
    groups_H, groups_G = {}, {}
    for v, c in chars_H.items():
        groups_H.setdefault(c, []).append(v)
    for v, c in chars_G.items():
        groups_G.setdefault(c, []).append(v)

    if set(groups_H.keys()) != set(groups_G.keys()):
        return None

    mapping = []
    for c in sorted(groups_H.keys()):
        if len(groups_H[c]) != len(groups_G[c]):
            return None
        mapping.append((sorted(groups_H[c]), sorted(groups_G[c])))
    return mapping


# Вспомогательные
def var_key(v):
    # Корректная сортировка x1, x2, ..., x10
    if v and v[0] == 'x' and v[1:].isdigit():
        return (0, int(v[1:]))
    return (1, v)


def format_substitution(assignment, var_order):
    # Подстановка в виде: | x1 x3 x4  a2 a3 a6
    vars_str = ' '.join(var_order)
    vals_str = ' '.join(assignment[v] for v in var_order)
    return f"| {vars_str}  {vals_str}"


def check_assignment(assignment, edges_H, edges_G):
    new_edges = Counter()
    for edge in edges_H:
        new_edge = tuple(sorted(assignment[v] for v in edge))
        new_edges[new_edge] += 1
    set_G = Counter(tuple(sorted(e)) for e in edges_G)
    if new_edges == set_G:
        return True, Counter(), Counter()
    missing = set_G - new_edges
    extra = new_edges - set_G
    return False, missing, extra


# Пример из статьи (исправленный)
def demo_inputs():
    text1 = (
        "a2,a4,a5\n"
        "a1,a5,a6\n"
        "a1,a2,a3\n"
        "a3,a4,a5\n"
        "a1,a4,a6\n"
    )
    text2 = (
        "b4,b5,b6\n"
        "b1,b2,b6\n"
        "b2,b3,b4\n"
        "b3,b5,b6\n"
        "b1,b2,b5\n"
    )
    return text1, text2


def read_edges(prompt):
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == '':
            break
        lines.append(line)
    return '\n'.join(lines)


def main():
    print("=" * 50)
    print("ПРОВЕРКА ИЗОМОРФИЗМА ГИПЕРГРАФОВ ОТНОШЕНИЙ")
    print("(коммутативные рёбра фиксированной арности)")
    print("=" * 50)
    print("\nВведите 'demo' для запуска примера из статьи,")
    print("или нажмите Enter для ручного ввода:")
    choice = input().strip().lower()

    if choice == 'demo':
        text1, text2 = demo_inputs()
    else:
        text1 = read_edges("\nРёбра G1 (по одному на строку, пустая строка — конец ввода графа):")
        text2 = read_edges("\nРёбра G2 (по одному на строку, пустая строка — конец ввода графа):")

    G1_raw = parse_edges(text1)
    G2_raw = parse_edges(text2)

    """
    G1 = deduplicate_edges(G1_raw)
    G2 = deduplicate_edges(G2_raw)

    if len(G1) != len(G1_raw):
        print(f"\nВНИМАНИЕ: в G1 удалено дубликатов: {len(G1_raw) - len(G1)}.")
        print(f"G1 после удаления дубликатов: {G1}")
    if len(G2) != len(G2_raw):
        print(f"\nВНИМАНИЕ: в G2 удалено дубликатов: {len(G2_raw) - len(G2)}.")
        print(f"G2 после удаления дубликатов: {G2}")
    """

    # 1. Проверка входных данных
    print("\n1. Разбор входных данных")
    print(f"G1 (исходный): {G1_raw}")
    print(f"G2 (исходный): {G2_raw}")

    if not G1_raw or not G2_raw:
        print("\nОШИБКА: один из гиперграфов пуст.")
        return

    arities1 = {len(e) for e in G1_raw}
    arities2 = {len(e) for e in G2_raw}
    if arities1 != arities2 or len(arities1) != 1:
        print("\nОШИБКА: все рёбра должны иметь одинаковую арность.")
        return

    G1 = G1_raw
    G2 = G2_raw

    # 2. Характеристики
    print("\n2. Характеристики аргументов")
    chars_G1 = compute_characteristics(G1)
    chars_G2 = compute_characteristics(G2)

    print("Характеристики G1:")
    for v in sorted(chars_G1):
        print(f"  char({v}) = {chars_G1[v]}")

    print("\nХарактеристики G2:")
    for v in sorted(chars_G2):
        print(f"  char({v}) = {chars_G2[v]}")

    # 3. Мультимножества
    print("\n3. Сравнение мультимножеств характеристик")
    ms1 = sorted(chars_G1.values())
    ms2 = sorted(chars_G2.values())
    print(f"Мультимножество G1: {ms1}")
    print(f"Мультимножество G2: {ms2}")

    if ms1 != ms2:
        print("\nМультимножества НЕ совпадают.")
        print("ВЫВОД: ГИПЕРГРАФЫ НЕ ИЗОМОРФНЫ.")
        return
    print("\nМультимножества совпадают. Переходим к построению H.")

    # 4. H = G2
    print("\n4. Построение H")

    vertices_G2 = sorted(chars_G2.keys())
    var_of = {v: f"x{i+1}" for i, v in enumerate(vertices_G2)}

    print("Соответствие переменных и констант G2:")
    for v in vertices_G2:
        print(f"  {var_of[v]} <- {v}  (chi={chars_G2[v]})")

    edges_H = [tuple(var_of[v] for v in e) for e in G2]
    print(f"\nH = {edges_H}")

    chars_H = compute_characteristics(edges_H)
    print("\nХарактеристики переменных H:")
    for v in sorted(chars_H, key=var_key):
        print(f"  χ({v}) = {chars_H[v]}")

    # 5. mappin
    print("\n5. Структура mapping:")

    mapping = build_mapping(chars_H, chars_G1)
    if mapping is None:
        print("\nНе удалось построить mapping.")
        print("ВЫВОД: ГИПЕРГРАФЫ НЕ ИЗОМОРФНЫ.")
        return

    mapping_str = ', '.join(
        f"[{','.join(vg)}]:[{','.join(cg)}]"
        for vg, cg in mapping
    )
    print(f"mapping = {{ {mapping_str} }}")

    # 6. Перебор перестановок
    print("\n6. Перебор всех перестановок")

    group_perm_lists = []
    for vars_group, consts_group in mapping:
        perms = [dict(zip(vars_group, p)) for p in permutations(consts_group)]
        group_perm_lists.append(perms)

    print(f"Число групп: {len(mapping)}")
    fact_strs, prod = [], 1
    for gi, (vars_group, consts_group) in enumerate(mapping):
        n = len(vars_group)
        k = len(group_perm_lists[gi])
        prod *= k
        fact_strs.append(f"{n}!")
        print(f"  Группа {gi+1}: ({', '.join(vars_group)}) -> "
              f"({', '.join(consts_group)}), перестановок {n}! = {k}")
    print(f"Общее число комбинаций: {' × '.join(fact_strs)} = {prod}")

    print("\n" + "-" * 50)
    print("Перестановки внутри каждой группы:")
    print("-" * 50)
    for gi, (vars_group, consts_group) in enumerate(mapping):
        print(f"\nГруппа {gi+1}: ({', '.join(vars_group)}) -> ({', '.join(consts_group)})")
        for pi, p in enumerate(permutations(consts_group)):
            a = dict(zip(vars_group, p))
            print(f"  λ_{gi+1},{pi+1} = {format_substitution(a, vars_group)}")

    print("\n" + "-" * 50)
    print("Все комбинации перестановок из разных групп:")
    print("-" * 50)

    valid_count = 0
    valid_assignments = []

    for idx, combo in enumerate(product(*group_perm_lists), 1):
        merged = {}
        for d in combo:
            merged.update(d)

        parts = [format_substitution(combo[gi], mapping[gi][0])
                 for gi in range(len(mapping))]
        combined_str = ' и '.join(parts)

        ok, missing, extra = check_assignment(merged, edges_H, G1)

        print(f"\n[{idx}] {combined_str}")
        if ok:
            valid_count += 1
            valid_assignments.append(merged)
            print("       ИЗОМОРФИЗМ НАЙДЕН ✓")
        else:
            print("       НАЙДЕНО ПРОТИВОРЕЧИЕ ✗")
            if missing:
                print(f"        Не получены рёбра G1: {sorted(missing)}")
            if extra:
                print(f"        Лишние рёбра: {sorted(extra)}")

    # Итог
    print("\n" + "-" * 50)
    print("ИТОГ")
    print("-" * 50)

    print(f"Всего проверено перестановок: {prod}")
    print(f"Успешных: {valid_count}")

    if valid_count > 0:
        print("\nГИПЕРГРАФЫ G1 и G2 ИЗОМОРФНЫ.")
        print("\nУспешные подстановки:")
        for i, a in enumerate(valid_assignments, 1):
            parts = [format_substitution({v: a[v] for v in vg}, vg)
                     for vg, _ in mapping]
            print(f"  {i}) {'\n     '.join(parts)}")
    else:
        print("\nГИПЕРГРАФЫ G1 и G2 НЕ ИЗОМОРФНЫ.")


if __name__ == "__main__":
    main()