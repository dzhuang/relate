import itertools

existing_basic_variable = [0, None, 1, 2]

existing_bv_idx = [existing_basic_variable.index(v) for v in existing_basic_variable if v is not None]

print existing_bv_idx

for L in range(len(existing_bv_idx)+1):
    for subset in itertools.combinations(existing_bv_idx, L):
        print list(subset)
