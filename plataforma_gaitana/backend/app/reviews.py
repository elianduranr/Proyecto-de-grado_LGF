"""Revisión explícita de identidades de una propuesta, independiente del modelo."""
import hashlib
import json
import math
from collections import defaultdict


def identity_key(product, color, variety):
    return json.dumps([product, color, variety], ensure_ascii=False, separators=(',', ':'))


def fingerprint(lines):
    values = sorted((r.horizon, r.final_value) for r in lines)
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()


def review_summary(lines, saved):
    groups = defaultdict(list)
    for line in lines:
        groups[identity_key(line.product, line.color, line.variety)].append(line)
    varieties = []
    for key, group in groups.items():
        first = group[0]
        entry = saved.get(key, {})
        status = entry.get('status', 'pendiente') if entry.get('fingerprint') == fingerprint(group) else 'pendiente'
        varieties.append({'product': first.product, 'color': first.color, 'variety': first.variety,
                         'status': status, 'reviewed_at': entry.get('at') if status != 'pendiente' else None,
                         'reviewed_by': entry.get('actor') if status != 'pendiente' else None,
                         'modified': any(r.final_value != int(math.floor(r.model_value + .5)) for r in group)})
    varieties.sort(key=lambda r: (r['product'], r['color'], r['variety']))
    pairs = defaultdict(list)
    for item in varieties:
        pairs[(item['product'], item['color'])].append(item)
    progress = []
    for (product, color), items in pairs.items():
        reviewed = sum(r['status'] != 'pendiente' for r in items)
        progress.append({'product': product, 'color': color, 'total': len(items), 'reviewed': reviewed,
                         'pending': len(items) - reviewed, 'complete': reviewed == len(items)})
    reviewed = sum(r['status'] != 'pendiente' for r in varieties)
    total = len(varieties)
    return {'varieties': varieties, 'groups': progress, 'total': total, 'reviewed': reviewed,
            'pending': total - reviewed, 'percent': round(100 * reviewed / total, 1) if total else 0}
