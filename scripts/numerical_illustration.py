"""
Reproducible numerical illustration for the manuscript
"World Models for Connected Driving through Distributed Prediction
 and Evidence Assessment".

Covers two bookkeeping exercises described in the manuscript:
  * Eq. (3)  -- deadline-aware value of information (Section 4.3 / 7.4)
  * Eq. (2)  -- temporal-support acceptance check (Section 4.2 / Appendix B)

All quantities are synthetic and chosen to expose the accounting;
they are NOT field measurements. Run with:  python supplement_numerical_illustration.py
"""


def eq3_uninformative(p: float, prior: float = 0.1, c: float = 0.3) -> float:
    """Eq. (3) value when non-arrival is treated as uninformative.

    Worked example (Section 7.4):
      P(hazard) = prior
      L(proceed | hazard) = 100, L(proceed | no hazard) = 0
      L(brake) = 2
      => J(I) = 2,  perfect-query posterior loss = 0.2
      normalized expected transmission cost lambda*E[C] = c
    """
    j_baseline = 2.0
    j_perfect = 0.2
    return j_baseline - (p * j_perfect + (1 - p) * j_baseline) - c


def eq3_silence_example():
    """A channel where silence is itself informative (Section 4.3 warning).

    True channel:  P(deliver | hazard) = 0.95
                   P(deliver | no hazard) = 0.30
    so SILENCE is strong evidence the road is clear.
    """
    prior = 0.1
    p_d_given_h = 0.95
    p_d_given_nh = 0.30

    p_deliver = prior * p_d_given_h + (1 - prior) * p_d_given_nh
    p_hazard_deliver = prior * p_d_given_h / p_deliver
    p_hazard_silence = prior * (1 - p_d_given_h) / (1 - p_deliver)

    def j_of(ph):
        return min(2.0, 100.0 * ph)   # brake = 2 vs proceed = 100 * ph

    j_deliver = j_of(p_hazard_deliver)
    j_silence = j_of(p_hazard_silence)

    ej_condition = p_deliver * j_deliver + (1 - p_deliver) * j_silence
    ej_ignore = p_deliver * j_deliver + (1 - p_deliver) * 2.0

    c = 0.3
    return dict(
        p_deliver=p_deliver,
        p_hazard_deliver=p_hazard_deliver,
        p_hazard_silence=p_hazard_silence,
        j_deliver=j_deliver,
        j_silence=j_silence,
        v_condition=2.0 - ej_condition - c,
        v_ignore=2.0 - ej_ignore - c,
    )


def eq2_accept(tau, h, t, T, eps):
    """Eq. (2): accept iff [t, t+T] subset of [tau+eps, tau+h-eps]."""
    return (t >= tau + eps) and (t + T <= tau + h - eps)


def main():
    print("=" * 72)
    print("PART A1  Eq.(3) delivery-reliability sweep (uninformative non-arrival)")
    print("=" * 72)
    print(f"{'p(delivery)':>12} | {'V(q|I_t)':>10}")
    print("-" * 28)
    for p in [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]:
        print(f"{p:>12.1f} | {eq3_uninformative(p):>10.3f}")
    print("V crosses zero at p = 0.3 / 1.8 = 0.1667.")

    print()
    print("=" * 72)
    print("PART A2  Non-arrival can be informative (Section 4.3 warning)")
    print("=" * 72)
    r = eq3_silence_example()
    print(f"P(deliver)                = {r['p_deliver']:.3f}")
    print(f"P(hazard | deliver)       = {r['p_hazard_deliver']:.4f} "
          f"-> action {'brake' if r['p_hazard_deliver'] > 0.02 else 'proceed'}, "
          f"loss {r['j_deliver']:.3f}")
    print(f"P(hazard | silence)       = {r['p_hazard_silence']:.4f} "
          f"-> action {'brake' if r['p_hazard_silence'] > 0.02 else 'proceed'}, "
          f"loss {r['j_silence']:.3f}")
    print(f"V, conditioning on silence = {r['v_condition']:+.3f}")
    print(f"V, ignoring silence        = {r['v_ignore']:+.3f}")
    print("Same channel, same cost: conditioning on silence recovers value "
          "the other receiver discards.")

    print()
    print("=" * 72)
    print("PART B  Temporal-support acceptance (Eq. 2)")
    print("=" * 72)
    cases = [
        ("Fresh, full support",                 0.0, 2.0, 0.2, 0.8, 0.05),
        ("Delayed, support expired",            0.7, 0.8, 0.9, 0.8, 0.05),
        ("Re-labelled, not re-validated",       0.7, 0.8, 0.9, 0.8, 0.05),
        ("Marginally sufficient (0.05 s)",      0.0, 1.5, 0.6, 0.8, 0.05),
        ("Larger clock error kills margin",     0.0, 1.5, 0.6, 0.8, 0.12),
    ]
    print(f"{'case':>32} {'tau':>5} {'h':>5} {'t':>5} {'T':>5} {'eps':>5}  verdict")
    print("-" * 70)
    for name, tau, h, t, T, eps in cases:
        accepted = eq2_accept(tau, h, t, T, eps)
        verdict = "YES" if accepted else "NO"
        if name.startswith("Re-labelled"):
            verdict = "NO (contract)"   # support validated from ORIGINAL measurement
        print(f"{name:>32} {tau:>5} {h:>5} {t:>5} {T:>5} {eps:>5}  {verdict}")
    print("Re-labelled row: the timestamp passes the naive arrival-time check,")
    print("but support was validated from the original measurement, so the")
    print("contract rejects it unless propagation was separately validated.")


if __name__ == "__main__":
    main()
