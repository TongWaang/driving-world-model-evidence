import itertools
import unittest
from scripts.metrics import (candidate_regret, ranking_error, regret_interval,
    hazardous_false_clearance, brier_score, selective_risk, scenario_macro_average)


class ReportingDefinitionTests(unittest.TestCase):
    def test_strict_practical_margin_excludes_boundary(self):
        self.assertIsNone(ranking_error([0,0.5],[1,0],delta=0.5)['score'])

    def test_difference_interval_must_exceed_margin(self):
        # Excludes an interval that excludes zero but not the practical margin.
        result=ranking_error([2,0],[0,2],delta=0.5,difference_intervals={(0,1):(0.1,2.0)})
        self.assertEqual(result['eligible_pairs'],0)

    def test_model_tie_is_half_error(self):
        self.assertEqual(ranking_error([0,2],[1,1],0.5)['score'],0.5)

    def test_reference_eligibility_does_not_depend_on_predictor(self):
        bounds={(0,1):(-2,-1),(0,2):(-0.1,0.1),(1,2):(0.8,1.2)}
        a=ranking_error([0,2,1],[0,2,1],0.5,bounds)
        b=ranking_error([0,2,1],[2,0,1],0.5,bounds)
        self.assertEqual(a['eligible_pairs'],b['eligible_pairs'])
        self.assertEqual(a['eligible_pairs'],2)

    def test_rank_invariance_to_candidate_permutation(self):
        ref=[4,1.2,3]
        pred=[0.5,1.2,3]
        for order in itertools.permutations(range(3)):
            result=ranking_error([ref[i] for i in order],[pred[i] for i in order],0.5)
            self.assertAlmostEqual(result['score'],2/3)

    def test_single_candidate_has_no_pair_coverage(self):
        result=ranking_error([1],[0])
        self.assertIsNone(result['score'])
        self.assertIsNone(result['pair_coverage'])

    def test_regret_intervals_contain_all_corner_realizations(self):
        boxes=[(0,1),(2,4),(-1,3)]
        for selected in range(3):
            lo,hi=regret_interval(boxes,selected)
            for costs in itertools.product(*boxes):
                regret=costs[selected]-min(costs)
                self.assertLessEqual(lo,regret)
                self.assertLessEqual(regret,hi)

    def test_exact_regret_intervals_collapse(self):
        self.assertEqual(regret_interval([(4,4),(1.2,1.2),(3,3)],0),(2.8,2.8))

    def test_standard_bound_for_all_small_finite_vectors(self):
        for ref in itertools.product([0,1,3],repeat=3):
            for pred in itertools.product([0,2],repeat=3):
                result=candidate_regret(ref,pred)
                self.assertLessEqual(result['regret'],result['standard_bound'])

    def test_selection_tie_break_is_explicit(self):
        self.assertEqual(candidate_regret([2,0],[1,1])['selected_index'],0)

    def test_no_resolved_hazard_is_undefined(self):
        result=hazardous_false_clearance([(0,0.01),(0.01,0.04)],[True,True],0.02)
        self.assertIsNone(result['score'])
        self.assertEqual(result['unresolved'],1)

    def test_threshold_crossing_is_unresolved(self):
        result=hazardous_false_clearance([(0.02,0.03),(0.02,0.02),(0.03,0.04)], [True,True,False],0.02)
        self.assertEqual(result['unresolved'],1)
        self.assertEqual(result['resolved_nonhazardous'],1)
        self.assertEqual(result['resolved_hazardous'],1)
        self.assertEqual(result['score'],0)

    def test_brier_perfect_and_opposite_predictions(self):
        self.assertEqual(brier_score([0,1],[0,1]),0)
        self.assertEqual(brier_score([1,0],[0,1]),1)

    def test_selective_empty_retained_set_is_undefined(self):
        result=selective_risk([0.8,0.4],[1,0],[0,0.5,0.9])
        self.assertEqual(result[0]['risk'],0.5)
        self.assertEqual(result[1]['coverage'],0.5)
        self.assertEqual(result[1]['risk'],1)
        self.assertIsNone(result[2]['risk'])

    def test_scenario_macro_average_keeps_excluded_count(self):
        self.assertEqual(scenario_macro_average([0,None,1]),dict(score=0.5,resolved_scenarios=2,total_scenarios=3))

    def test_invalid_probability_rejected(self):
        with self.assertRaises(ValueError):
            hazardous_false_clearance([(0.1,1.1)],[True],0.02)

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            candidate_regret([1,2],[1])

    def test_nonfinite_values_rejected(self):
        with self.assertRaises(ValueError):
            ranking_error([1,float('nan')],[1,2])

    def test_missing_pair_interval_rejected(self):
        with self.assertRaises(ValueError):
            ranking_error([1,2],[1,2],difference_intervals={})


if __name__=='__main__':
    unittest.main()
