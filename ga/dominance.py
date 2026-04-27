def dominates(a, b):
    """
    Return True if solution a dominates solution b.
    All objectives are minimised: a is better than b if
    a_i <= b_i for all i, AND strict inequality in at least one.
    """
    better = False
    for ai, bi in zip(a, b):
        if ai > bi:          # worse in any objective → does not dominate
            return False
        if ai < bi:
            better = True
    return better


def non_dominated_sort(fitness_vectors):
    """
    Perform fast non‑dominated sort (Deb et al.).
    fitness_vectors: list of tuples (f1, f2, ...) to minimise.
    Returns: list of fronts, each front is a list of indices.
    """
    n = len(fitness_vectors)
    domination_count = [0] * n
    dominated_list = [[] for _ in range(n)]
    fronts = [[]]

    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if dominates(fitness_vectors[p], fitness_vectors[q]):
                dominated_list[p].append(q)
            elif dominates(fitness_vectors[q], fitness_vectors[p]):
                domination_count[p] += 1
        if domination_count[p] == 0:
            fronts[0].append(p)

    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in dominated_list[p]:
                domination_count[q] -= 1
                if domination_count[q] == 0:
                    next_front.append(q)
        i += 1
        fronts.append(next_front)
    return fronts[:-1]  # last front is always empty


def crowding_distance(fitness_vectors, front_indices):
    """
    Assign crowding distance to each individual in a front.
    """
    if not front_indices:
        return {}
    m = len(fitness_vectors[0])   # number of objectives
    dist = {idx: 0.0 for idx in front_indices}

    for obj in range(m):
        sorted_front = sorted(front_indices, key=lambda idx: fitness_vectors[idx][obj])
        f_min = fitness_vectors[sorted_front[0]][obj]
        f_max = fitness_vectors[sorted_front[-1]][obj]
        if f_max == f_min:
            continue
        dist[sorted_front[0]] = float('inf')
        dist[sorted_front[-1]] = float('inf')
        for k in range(1, len(sorted_front) - 1):
            dist[sorted_front[k]] += (
                fitness_vectors[sorted_front[k+1]][obj] -
                fitness_vectors[sorted_front[k-1]][obj]
            ) / (f_max - f_min)
    return dist