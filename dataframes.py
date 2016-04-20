import pandas

def df_diff(df_old, df_new, eps=0.0001):
    added = set(df_new.columns.values.tolist())-set(df_old.columns.values.tolist())
    if len(added):
        added = df_new[added]
    else:
        added = None
    missing = set(df_old.columns.values.tolist())-set(df_new.columns.values.tolist())
    if len(missing):
        missing = df_old[missing]
    else:
        missing = None
    coln_in_both = set(df_old.columns.values.tolist()) & set(df_new.columns.values.tolist())
    rel_diff = df_new[coln_in_both].divide(df_old[coln_in_both]).substract(1)
    idx_diff = [False]*len(rel_diff.index)
    for coln, series in rel_diff.iteritems():
        idx_diff_here = [abs(v) > eps for v in series]
        if not any(idx_diff_here):
            rel_diff.drop(coln)
        idx_diff = idx_diff or idx_diff_here
    if any(idx_diff):
        rel_diff = rel_diff[idx_diff]
    else:
        rel_diff = None
    return (added, rel_diff.multiply(100.0), missing)