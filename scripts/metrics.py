"""Deterministic implementations of the manuscript's reporting definitions.

Intervals are inputs, not confidence intervals estimated by this module.
The caller must establish joint coverage, independence and sampling validity.
"""
from itertools import combinations
from math import isfinite


def numbers(values, name, nonempty=True):
    values = list(values)
    if nonempty and not values:
        raise ValueError(f'{name} must be nonempty')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) for x in values):
        raise ValueError(f'{name} must contain finite numbers')
    return values


def matched(a, b, aname='reference', bname='estimate'):
    a, b = numbers(a, aname), numbers(b, bname)
    if len(a) != len(b):
        raise ValueError('Vectors must have equal lengths')
    return a, b


def intervals(values, probability=False):
    result = []
    for pair in values:
        pair = numbers(pair, 'interval')
        if len(pair) != 2 or pair[0] > pair[1]:
            raise ValueError('Each interval must have ordered lower and upper limits')
        if probability and not (0 <= pair[0] <= pair[1] <= 1):
            raise ValueError('Probability intervals must lie in [0,1]')
        result.append(tuple(pair))
    if not result:
        raise ValueError('At least one interval is required')
    return result


def candidate_regret(reference_costs, estimates):
    reference, estimates = matched(reference_costs, estimates)
    selected = min(range(len(estimates)), key=estimates.__getitem__)
    # Exact model ties use the first candidate; this rule is explicit and stable.
    return dict(selected_index=selected, regret=reference[selected]-min(reference),
                uniform_cost_error=max(abs(a-b) for a,b in zip(reference,estimates)),
                standard_bound=2*max(abs(a-b) for a,b in zip(reference,estimates)))


def ranking_error(reference_costs, estimates, delta=0.0, difference_intervals=None):
    reference, estimates = matched(reference_costs, estimates)
    if not isfinite(delta) or delta < 0:
        raise ValueError('delta must be finite and nonnegative')
    errors = 0.0
    eligible = 0
    total = len(reference)*(len(reference)-1)//2
    for i,j in combinations(range(len(reference)),2):
        if difference_intervals is None:
            lo = hi = reference[i]-reference[j]
        else:
            if (i,j) not in difference_intervals:
                raise ValueError('Supply reference-only difference intervals for every pair')
            lo,hi = intervals([difference_intervals[(i,j)]])[0]
        direction = 1 if lo > delta else -1 if hi < -delta else 0
        if not direction:
            continue
        eligible += 1
        predicted = estimates[i]-estimates[j]
        errors += 0.5 if predicted == 0 else float(predicted*direction < 0)
    return dict(score=errors/eligible if eligible else None, error_count=errors,
                eligible_pairs=eligible, total_pairs=total,
                pair_coverage=eligible/total if total else None)


def regret_interval(cost_intervals, selected):
    bounds = intervals(cost_intervals)
    if isinstance(selected,bool) or not isinstance(selected,int) or not 0 <= selected < len(bounds):
        raise ValueError('Invalid selected candidate index')
    lower,upper = bounds[selected]
    return (max(0.0, lower-min(u for _,u in bounds)), upper-min(l for l,_ in bounds))


def hazardous_false_clearance(reference_probability_intervals, cleared, q):
    bounds = intervals(reference_probability_intervals, probability=True)
    cleared = list(cleared)
    if len(bounds) != len(cleared) or any(type(v) is not bool for v in cleared):
        raise ValueError('Provide one boolean clearance decision per candidate')
    if not isfinite(q) or not 0 <= q <= 1:
        raise ValueError('q must lie in [0,1]')
    hazardous = [i for i,(lo,hi) in enumerate(bounds) if lo > q]
    safe = [i for i,(lo,hi) in enumerate(bounds) if hi <= q]
    unresolved = len(bounds)-len(hazardous)-len(safe)
    missed = sum(cleared[i] for i in hazardous)
    return dict(score=missed/len(hazardous) if hazardous else None,
                missed_hazards=missed,resolved_hazardous=len(hazardous),
                resolved_nonhazardous=len(safe),unresolved=unresolved,
                resolved_coverage=(len(hazardous)+len(safe))/len(bounds),
                clearance_rate=sum(cleared)/len(bounds))


def brier_score(probabilities, outcomes):
    probabilities,outcomes = matched(probabilities,outcomes,'probabilities','outcomes')
    if any(not 0 <= p <= 1 for p in probabilities) or any(y not in (0,1) for y in outcomes):
        raise ValueError('Use probabilities in [0,1] and binary outcomes')
    return sum((p-y)**2 for p,y in zip(probabilities,outcomes))/len(outcomes)


def selective_risk(confidences, losses, thresholds):
    confidences,losses = matched(confidences,losses,'confidences','losses')
    thresholds = numbers(thresholds,'thresholds')
    if any(not 0 <= p <= 1 for p in confidences+thresholds) or any(x < 0 for x in losses):
        raise ValueError('Confidence/threshold must be in [0,1]; loss must be nonnegative')
    output=[]
    for threshold in thresholds:
        kept=[loss for confidence,loss in zip(confidences,losses) if confidence >= threshold]
        output.append(dict(threshold=threshold, retained=len(kept), coverage=len(kept)/len(losses),
                           risk=sum(kept)/len(kept) if kept else None))
    return output


def scenario_macro_average(scores):
    values = numbers([x for x in scores if x is not None],'resolved scenario scores',nonempty=False)
    return dict(score=sum(values)/len(values) if values else None,
                resolved_scenarios=len(values), total_scenarios=len(scores))
