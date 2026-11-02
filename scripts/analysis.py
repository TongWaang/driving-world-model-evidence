"""Recompute the stipulated Section 6.5 example from stored inputs."""
from .metrics import candidate_regret, ranking_error, hazardous_false_clearance, regret_interval


def compute_example(example):
    penalties=example['maneuver_penalties']
    weight=example['collision_weight']
    reference=[penalty+weight*p for penalty,p in zip(penalties,example['reference_collision_probabilities'])]
    output={'reference_costs':reference, 'models':{}}
    q=example['hazard_threshold']
    intervals=[(p,p) for p in example['reference_collision_probabilities']]
    for name,model in example['models'].items():
        cost=model['estimated_costs']
        regret=candidate_regret(reference,cost)
        probabilities=[(c-penalty)/weight for c,penalty in zip(cost,penalties)]
        if any(p<0 or p>1 for p in probabilities):
            raise ValueError('Example costs imply invalid event probabilities')
        ranking=ranking_error(reference,cost,example['practical_margin'])
        hazard=hazardous_false_clearance(intervals,[p<=q for p in probabilities],q)
        output['models'][name]=dict(
            observation_error=sum(w*e for w,e in zip(example['observation_weights'],model['observation_component_errors'])),
            selected_action=example['actions'][regret['selected_index']],
            regret=regret['regret'],ranking_error=ranking['score'],
            hazardous_false_clearance=hazard['score'],uniform_cost_error=regret['uniform_cost_error'],
            regret_bound=regret['standard_bound'],
            predicted_collision_probabilities=probabilities,
            ranking_details=ranking,hazard_details=hazard,
            exact_reference_regret_interval=regret_interval([(x,x) for x in reference],regret['selected_index']))
    return output
