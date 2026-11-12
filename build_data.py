# -*- coding: utf-8 -*-
"""读取 白居易-元稹.csv，去重边（同对保留最高分），生成前端 data.js。"""
import io, csv, json, collections, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '白居易-元稹.csv')
OUT = os.path.join(BASE, 'data.js')

rows = list(csv.reader(io.StringIO(open(SRC, encoding='utf-8-sig').read())))

def clean(s):
    return (s or '').strip()

# 节点去重：key = 诗名 + 诗句
node_map = {'A': {}, 'B': {}}
nodes = {'A': [], 'B': []}

def get_node(side, title, line):
    key = title + '||' + line
    if key not in node_map[side]:
        node_map[side][key] = len(nodes[side])
        nodes[side].append([title, line])
    return node_map[side][key]

# 边：(aid, bid) -> 最高分
edge_map = {}
skipped = 0
for r in rows:
    if len(r) < 11:
        skipped += 1
        continue
    a_name, a_title, a_line, b_name, b_title, b_line = clean(r[0]), clean(r[1]), clean(r[2]), clean(r[3]), clean(r[4]), clean(r[5])
    if not a_line or not b_line:
        skipped += 1
        continue
    try:
        score = int(float(r[6]))
    except ValueError:
        skipped += 1
        continue
    aid = get_node('A', a_title, a_line)
    bid = get_node('B', b_title, b_line)
    k = (aid, bid)
    if k not in edge_map or score > edge_map[k]:
        edge_map[k] = score

edges = [[aid, bid, score] for (aid, bid), score in edge_map.items()]
# 按分值降序，便于前端默认展示高分配对
edges.sort(key=lambda e: -e[2])

data = {
    'poets': {
        'A': {'name': '白居易', 'label': '唐'},
        'B': {'name': '元稹', 'label': '唐'}
    },
    'nodesA': nodes['A'],
    'nodesB': nodes['B'],
    'edges': edges
}

payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('window.POEM_DATA = ')
    f.write(payload)
    f.write(';\n')

print('rows:', len(rows), 'skipped:', skipped)
print('nodesA:', len(nodes['A']), 'nodesB:', len(nodes['B']), 'edges:', len(edges))
print('data.js size KB:', round(os.path.getsize(OUT)/1024, 1))
