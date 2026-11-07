import math

def allocate(total: int, weights: list[float]) -> list[int]:
    """Restos mayores; mismo total exacto, empates en orden estable."""
    if total < 0 or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('Las cantidades deben ser finitas y no negativas.')
    if not weights:
        raise ValueError('La selección no contiene variedades.')
    if sum(weights) == 0:
        if total == 0:
            return [0]*len(weights)
        if len(weights) == 1:
            return [total]
        raise ValueError('La selección suma cero. Distribuye primero las cantidades por variedad.')
    raw = [total*w/sum(weights) for w in weights]
    values = [math.floor(v) for v in raw]
    remaining = total-sum(values)
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i]-values[i]), i))
    for i in order[:remaining]:
        values[i] += 1
    assert sum(values) == total
    return values

