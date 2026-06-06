
PRIMITIVE = 'civilizational_longitudinal_stability_synthesizer'

DEPENDENCIES = [
    'longitudinal_society_observatory',
    'longitudinal_civilizational_autonomy_tracker',
    'constitutional_longitudinal_observatory',
    'consciousness_longitudinal_stability_analyzer',
    'long_duration_runtime_supervisor',
    'long_duration_civilizational_resilience',
    'refined_long_duration_civilizational_resilience',
    'longitudinal_recovery_observer',
    'inter_run_stability_synthesizer',
    'civilizational_metrics_synthesizer',
    'multi_scale_coupling',
    'persistent_multi_scale_memory',
]

def _bounded(value):
    return max(0.0, min(1.0, float(value)))

class CivilizationalLongitudinalStabilitySynthesizer:

    def __init__(self):
        self._history = []
        self._regime_history = []
        self._transition_matrix = {}
        self._trend_history = []
        self._identity_history = []
        self._identity_drift_history = []
        self._identity_drift_velocity_history = []

    def step(self,
        longitudinal_stability_index=0.95,
        longitudinal_continuity_index=0.95,
        historical_persistence_index=0.95,
        governance_persistence_index=0.95,
        distributed_memory_persistence_index=0.95,
        civilizational_viability_index=0.95):

        values = [
            _bounded(longitudinal_stability_index),
            _bounded(longitudinal_continuity_index),
            _bounded(historical_persistence_index),
            _bounded(governance_persistence_index),
            _bounded(distributed_memory_persistence_index),
            _bounded(civilizational_viability_index),
        ]

        index = sum(values) / len(values)
        self._history.append(index)

        if len(self._history) >= 2:
            previous = self._history[-2]
            if index > previous:
                trend = "improving"
            elif index < previous:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"

        self._trend_history.append(trend)

        persistence = sum(self._history) / len(self._history)
        risk = 1.0 - index

        improving = self._trend_history.count("improving")
        degrading = self._trend_history.count("degrading")
        trend_events = max(1, improving + degrading)

        persistent_improvement_ratio = improving / trend_events
        persistent_degradation_ratio = degrading / trend_events

        reversals = 0
        for i in range(1, len(self._trend_history)):
            a = self._trend_history[i - 1]
            b = self._trend_history[i]
            if ((a == "improving" and b == "degrading")
                or (a == "degrading" and b == "improving")):
                reversals += 1

        trend_reversal_detection = reversals > 0
        trend_persistence_index = _bounded(
            1.0 - (reversals / max(1, len(self._trend_history)))
        )

        trend_stability = _bounded(
            trend_persistence_index *
            (1.0 - persistent_degradation_ratio)
        )

        short_window = self._history[-3:]
        medium_window = self._history[-5:]

        short_term_window_index = sum(short_window) / len(short_window)
        medium_term_window_index = sum(medium_window) / len(medium_window)

        window_gap = abs(
            short_term_window_index - medium_term_window_index
        )

        latest_drop = 0.0
        if len(self._history) >= 2:
            latest_drop = max(0.0, self._history[-2] - self._history[-1])

        max_window_drop = 0.0
        for i in range(1, len(self._history)):
            max_window_drop = max(
                max_window_drop,
                max(0.0, self._history[i - 1] - self._history[i])
            )

        window_consistency = _bounded(
            1.0 - max(window_gap, latest_drop)
        )

        window_anomaly_detection = (
            window_gap > 0.15
            or latest_drop > 0.20
            or max_window_drop > max(0.10, (sum(self._history) / len(self._history)) * 0.25)
        )

        anomaly_penalty = min(max(0.10, (sum(self._history) / len(self._history))), max(window_gap, latest_drop, max_window_drop))

        sliding_window_stability_index = _bounded(
            (
                short_term_window_index +
                medium_term_window_index +
                window_consistency
            ) / 3.0 - anomaly_penalty
        )

        if sliding_window_stability_index >= 0.90:
            window_stability_class = "persistent_window_stability"
        elif sliding_window_stability_index >= 0.75:
            window_stability_class = "functional_window_stability"
        else:
            window_stability_class = "unstable_window_stability"

        if trend_stability >= 0.90:
            trend_persistence_class = "persistent_longitudinal_trend"
        elif trend_stability >= 0.75:
            trend_persistence_class = "functional_longitudinal_trend"
        else:
            trend_persistence_class = "unstable_longitudinal_trend"

        if index >= 0.90:
            classification = "persistent_civilizational_stability"
        elif index >= 0.75:
            classification = "functional_longitudinal_stability"
        else:
            classification = "fragile_longitudinal_stability"

        

        short_term_stability_index = sum(self._history[-3:]) / len(self._history[-3:])
        medium_term_stability_index = sum(self._history[-5:]) / len(self._history[-5:])
        long_term_stability_index = sum(self._history) / len(self._history)

        cross_scale_divergence_penalty = abs(
            short_term_stability_index - long_term_stability_index
        )

        divergence_adjusted_multi_scale_index = max(
            0.0,
            ((short_term_stability_index + medium_term_stability_index + long_term_stability_index) / 3.0)
            - cross_scale_divergence_penalty
        )

        regime_classification = "persistent"

        if window_anomaly_detection and divergence_adjusted_multi_scale_index < 0.50:
            regime_classification = "collapsing"
        elif trend == "degrading" and divergence_adjusted_multi_scale_index < 0.75:
            regime_classification = "degrading"
        elif trend_reversal_detection:
            regime_classification = "oscillating"
        elif trend == "improving" and divergence_adjusted_multi_scale_index >= 0.75:
            regime_classification = "recovering"
        elif divergence_adjusted_multi_scale_index < 0.75:
            regime_classification = "fragile"


        self._regime_history.append(regime_classification)

        true_regime_transition_count = 0

        if len(self._regime_history) >= 2:
            src = self._regime_history[-2]
            dst = self._regime_history[-1]
            key = f'{src}->{dst}'
            self._transition_matrix[key] = (
                self._transition_matrix.get(key, 0) + 1
            )

        for key, count in self._transition_matrix.items():
            left, right = key.split('->')
            if left != right:
                true_regime_transition_count += count

        regime_transition_count = true_regime_transition_count

        dominant_regime = (
            max(set(self._regime_history), key=self._regime_history.count)
            if self._regime_history else 'unknown'
        )

        regime_stability_index = max(
            0.0,
            1.0 - (
                regime_transition_count / max(1, len(self._regime_history))
            )
        )


        regime_runs = []
        current = None
        run_length = 0

        for regime in self._regime_history:
            if regime == current:
                run_length += 1
            else:
                if current is not None:
                    regime_runs.append((current, run_length))
                current = regime
                run_length = 1

        if current is not None:
            regime_runs.append((current, run_length))

        mean_regime_residence_time = round(
            sum(length for _, length in regime_runs) / max(1, len(regime_runs)),
            4
        )

        transition_total = max(1, sum(self._transition_matrix.values()))

        escape_count = sum(
            count
            for key, count in self._transition_matrix.items()
            if key.split('->')[0] != key.split('->')[1]
        )

        regime_escape_probability = round(
            escape_count / transition_total,
            4
        )

        regime_absorption_probability = round(
            1.0 - regime_escape_probability,
            4
        )

        persistent_regime_index = round(
            max(0.0, 1.0 - regime_escape_probability),
            4
        )

        dominant_attractor_regime = dominant_regime


        basin_size = self._regime_history.count(dominant_regime)

        attractor_strength = round(
            basin_size / max(1, len(self._regime_history)),
            4
        )

        attractor_resilience = round(
            1.0 - regime_escape_probability,
            4
        )

        basin_dominance_index = round(
            attractor_strength * attractor_resilience,
            4
        )

        escape_difficulty = round(
            mean_regime_residence_time * attractor_resilience,
            4
        )


        outgoing = {}

        for key, count in self._transition_matrix.items():
            left, right = key.split('->')
            if left == dominant_attractor_regime:
                outgoing[right] = outgoing.get(right, 0) + count

        total_outgoing = max(1, sum(outgoing.values()))

        forecast_regime_distribution = {
            regime: round(count / total_outgoing, 4)
            for regime, count in outgoing.items()
        }

        future_regime_probability = round(
            forecast_regime_distribution.get(
                dominant_attractor_regime,
                0.0
            ),
            4
        )

        attractor_retention_probability = future_regime_probability

        expected_escape_horizon = round(
            1.0 / max(
                0.0001,
                1.0 - attractor_retention_probability
            ),
            4
        )

        attractor_convergence_index = round(
            (
                attractor_strength +
                attractor_resilience +
                basin_dominance_index
            ) / 3.0,
            4
        )



        residence_lengths = []
        current_run = 1

        for i in range(1, len(self._regime_history)):
            if self._regime_history[i] == self._regime_history[i - 1]:
                current_run += 1
            else:
                residence_lengths.append(current_run)
                current_run = 1

        residence_lengths.append(current_run)

        empirical_escape_horizon = round(
            sum(residence_lengths) / max(1, len(residence_lengths)),
            4
        )

        empirical_regime_half_life = round(
            empirical_escape_horizon * 0.6931,
            4
        )

        forecast_stability_horizon = round(
            empirical_escape_horizon *
            max(0.0, attractor_resilience),
            4
        )



        forecast_transition_graph = {}

        states = sorted(set(self._regime_history))

        for state in states:

            outgoing = {}

            for key, count in self._transition_matrix.items():

                src, dst = key.split("->")

                if src == state:
                    outgoing[dst] = outgoing.get(dst, 0) + count

            total = sum(outgoing.values())

            if total > 0:
                forecast_transition_graph[state] = {
                    dst: round(cnt / total, 4)
                    for dst, cnt in outgoing.items()
                }

        forecast_two_step_distribution = {}

        if dominant_attractor_regime in forecast_transition_graph:

            first = forecast_transition_graph[dominant_attractor_regime]

            for intermediate, p1 in first.items():

                second = forecast_transition_graph.get(intermediate, {})

                if not second:
                    forecast_two_step_distribution[intermediate] = (
                        forecast_two_step_distribution.get(intermediate, 0.0) + p1
                    )

                for target, p2 in second.items():
                    forecast_two_step_distribution[target] = (
                        forecast_two_step_distribution.get(target, 0.0) + p1 * p2
                    )

        forecast_two_step_distribution = {
            k: round(v, 4)
            for k, v in forecast_two_step_distribution.items()
        }

        graph_complexity = len(self._transition_matrix)

        graph_entropy = round(
            1.0 - attractor_retention_probability,
            4
        )



        transition_probabilities = {}

        for state, transitions in forecast_transition_graph.items():
            transition_probabilities[state] = dict(transitions)

        current_state = dominant_attractor_regime

        def project_distribution(start_state, steps):

            distribution = {start_state: 1.0}

            for _ in range(steps):

                next_distribution = {}

                for src, prob in distribution.items():

                    outgoing = transition_probabilities.get(src)

                    if not outgoing:
                        next_distribution[src] = (
                            next_distribution.get(src, 0.0) + prob
                        )
                        continue

                    for dst, edge_prob in outgoing.items():
                        next_distribution[dst] = (
                            next_distribution.get(dst, 0.0)
                            + prob * edge_prob
                        )

                distribution = next_distribution

            total = sum(distribution.values()) or 1.0

            return {
                k: round(v / total, 4)
                for k, v in distribution.items()
            }

        projection_t_plus_2 = project_distribution(
            current_state,
            2
        )

        projection_t_plus_5 = project_distribution(
            current_state,
            5
        )

        projection_t_plus_10 = project_distribution(
            current_state,
            10
        )

        long_horizon_regime_distribution = dict(
            projection_t_plus_10
        )

        projected_dominant_regime = (
            max(
                long_horizon_regime_distribution,
                key=long_horizon_regime_distribution.get
            )
            if long_horizon_regime_distribution
            else dominant_attractor_regime
        )

        projected_regime_entropy = round(
            1.0 - max(
                long_horizon_regime_distribution.values(),
                default=1.0
            ),
            4
        )

        projection_convergence_index = round(
            max(
                long_horizon_regime_distribution.values(),
                default=1.0
            ),
            4
        )

        # R5.7 Reachability Analysis

        reachability_graph = {
            state: set(edges.keys())
            for state, edges in forecast_transition_graph.items()
        }

        reachable_regimes = set()
        frontier = {dominant_attractor_regime}

        while frontier:
            node = frontier.pop()
            if node in reachable_regimes:
                continue
            reachable_regimes.add(node)
            frontier.update(reachability_graph.get(node, set()) - reachable_regimes)

        all_regimes = set(self._regime_history)

        unreachable_regimes = sorted(all_regimes - reachable_regimes)
        reachable_regimes = sorted(reachable_regimes)

        absorbing_regimes = sorted([
            state
            for state, edges in forecast_transition_graph.items()
            if set(edges.keys()) == {state}
            and abs(edges.get(state, 0.0) - 1.0) < 0.0001
        ])

        communicating_classes = [reachable_regimes]
        strongly_connected_components = communicating_classes

        longitudinal_openness_index = round(
            len(reachable_regimes) / max(1, len(all_regimes)),
            4
        )

        
        # R5.7.1 Strongly Connected Components & True Reachability

        graph_nodes = set(forecast_transition_graph.keys())
        for edges in forecast_transition_graph.values():
            graph_nodes.update(edges.keys())

        def _reachable(start):
            visited = set()
            stack = [start]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                stack.extend(forecast_transition_graph.get(n, {}).keys())
            return visited

        true_reachable_regimes = sorted(_reachable(dominant_attractor_regime))

        reverse_graph = {}
        for src, edges in forecast_transition_graph.items():
            for dst in edges:
                reverse_graph.setdefault(dst, set()).add(src)

        def _reverse_reachable(start):
            visited = set()
            stack = [start]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                stack.extend(reverse_graph.get(n, set()))
            return visited

        true_strongly_connected_components = []
        remaining = set(graph_nodes)

        while remaining:
            node = next(iter(remaining))
            fwd = _reachable(node)
            rev = _reverse_reachable(node)
            scc = sorted(fwd.intersection(rev))
            true_strongly_connected_components.append(scc)
            remaining -= set(scc)

        true_communicating_classes = list(true_strongly_connected_components)

        true_unreachable_regimes = sorted(
            graph_nodes - set(true_reachable_regimes)
        )

        closed_attractor_components = []

        for comp in true_strongly_connected_components:
            comp_set = set(comp)
            closed = True

            for n in comp:
                outgoing = set(
                    forecast_transition_graph.get(n, {}).keys()
                )

                if outgoing - comp_set:
                    closed = False
                    break

            if closed:
                closed_attractor_components.append(comp)

        graph_reachability_index = round(
            len(true_reachable_regimes) / max(1, len(graph_nodes)),
            4
        )
        


        # R5.9 Regime Recurrence Quantification

        recurrence_count = 0
        recurrence_intervals = []
        last_seen = {}

        for idx, regime in enumerate(self._regime_history):

            if regime in last_seen:
                recurrence_count += 1
                recurrence_intervals.append(
                    idx - last_seen[regime]
                )

            last_seen[regime] = idx

        recurrence_density = round(
            recurrence_count / max(1, len(self._regime_history)),
            4
        )

        recurrence_frequency = round(
            recurrence_count / max(1, len(self._regime_history) - 1),
            4
        )

        mean_recurrence_interval = round(
            sum(recurrence_intervals)
            / max(1, len(recurrence_intervals)),
            4
        )

        attractor_recurrence_strength = round(
            recurrence_density * attractor_strength,
            4
        )

        civilizational_recurrence_index = round(
            (
                recurrence_density
                + recurrence_frequency
                + attractor_recurrence_strength
                + persistent_regime_index
            ) / 4.0,
            4
        )

        
        communication_closure_index = round(
            len(closed_attractor_components)
            / max(1, len(true_strongly_connected_components)),
            4
        )
        # R5.10 Longitudinal Regime Stability Metrics

        regime_volatility_index = round(
            min(
                1.0,
                regime_transition_count
                / max(1, len(self._regime_history))
            ),
            4
        )

        regime_coherence_index = round(
            (
                attractor_strength
                + persistent_regime_index
                + communication_closure_index
            ) / 3.0,
            4
        )

        regime_resilience_score = round(
            (
                attractor_resilience
                + basin_dominance_index
                + forecast_stability_horizon / max(1.0, forecast_stability_horizon)
            ) / 3.0,
            4
        )

        regime_stability_score = round(
            (
                regime_stability_index
                + regime_coherence_index
                + civilizational_recurrence_index
            ) / 3.0,
            4
        )

        longitudinal_regime_stability_index = round(
            (
                regime_stability_score
                + regime_resilience_score
                + projection_convergence_index
            ) / 3.0,
            4
        )

        # R5.11 Regime Drift Detection

        drift_window = self._history[-10:]

        if len(drift_window) >= 2:

            trajectory_drift_rate = round(
                abs(drift_window[-1] - drift_window[0]),
                4
            )

            drift_accumulation_index = round(
                sum(
                    abs(drift_window[i] - drift_window[i-1])
                    for i in range(1, len(drift_window))
                ) / max(1, len(drift_window)-1),
                4
            )

        else:
            trajectory_drift_rate = 0.0
            drift_accumulation_index = 0.0

        attractor_distance = round(
            max(
                0.0,
                1.0 - attractor_strength
            ),
            4
        )

        latent_regime_shift_score = round(
            (
                regime_volatility_index +
                attractor_distance +
                (1.0 - regime_coherence_index) +
                (1.0 - civilizational_recurrence_index)
            ) / 4.0,
            4
        )

        regime_drift_index = round(
            (
                trajectory_drift_rate +
                drift_accumulation_index +
                latent_regime_shift_score
            ) / 3.0,
            4
        )

        if regime_drift_index >= 0.50:
            drift_classification = "critical_regime_drift"
        elif regime_drift_index >= 0.20:
            drift_classification = "controlled_regime_drift"
        else:
            drift_classification = "stable_regime_drift"

        # R5.12 Regime Persistence Forecast Calibration

        attractor_persistence_forecast = round(
            (
                attractor_retention_probability +
                attractor_resilience +
                persistent_regime_index
            ) / 3.0,
            4
        )

        forecasted_regime_persistence = round(
            (
                attractor_persistence_forecast +
                projection_convergence_index +
                civilizational_recurrence_index
            ) / 3.0,
            4
        )

        persistence_confidence_index = round(
            (
                forecasted_regime_persistence +
                longitudinal_regime_stability_index +
                (1.0 - regime_drift_index)
            ) / 3.0,
            4
        )

        regime_survival_probability = round(
            (
                persistence_confidence_index +
                communication_closure_index +
                persistent_regime_index
            ) / 3.0,
            4
        )

        longitudinal_persistence_forecast_index = round(
            (
                forecasted_regime_persistence +
                persistence_confidence_index +
                regime_survival_probability
            ) / 3.0,
            4
        )

        if longitudinal_persistence_forecast_index >= 0.90:
            persistence_forecast_class = "persistent_regime_forecast"
        elif longitudinal_persistence_forecast_index >= 0.75:
            persistence_forecast_class = "functional_regime_forecast"
        else:
            persistence_forecast_class = "fragile_regime_forecast"

        # R5.13 Longitudinal Regime Meta-Synthesis

        regime_meta_stability_index = round(
            (
                regime_stability_score +
                longitudinal_regime_stability_index +
                regime_coherence_index
            ) / 3.0,
            4
        )

        regime_meta_resilience_index = round(
            (
                regime_resilience_score +
                attractor_resilience +
                (1.0 - regime_drift_index)
            ) / 3.0,
            4
        )

        regime_meta_forecast_index = round(
            (
                longitudinal_persistence_forecast_index +
                persistence_confidence_index +
                forecasted_regime_persistence
            ) / 3.0,
            4
        )

        civilizational_regime_meta_index = round(
            (
                regime_meta_stability_index +
                regime_meta_resilience_index +
                regime_meta_forecast_index +
                civilizational_recurrence_index
            ) / 4.0,
            4
        )

        if civilizational_regime_meta_index >= 0.90:
            regime_ecology_class = "persistent_regime_ecology"
        elif civilizational_regime_meta_index >= 0.75:
            regime_ecology_class = "functional_regime_ecology"
        else:
            regime_ecology_class = "fragile_regime_ecology"

        # R6 Structural Fragility Mapping

        fragility_hotspots = []

        if regime_drift_index > 0.20:
            fragility_hotspots.append("regime_drift")

        if communication_closure_index < 0.80:
            fragility_hotspots.append("communication_closure")

        if graph_reachability_index < 0.80:
            fragility_hotspots.append("reachability")

        if persistent_regime_index < 0.80:
            fragility_hotspots.append("regime_persistence")

        critical_dependencies = [
            "communication_closure_index",
            "graph_reachability_index",
            "persistent_regime_index",
            "civilizational_regime_meta_index",
        ]

        failure_propagation_risk = round(
            (
                (1.0 - communication_closure_index) +
                (1.0 - graph_reachability_index) +
                regime_drift_index
            ) / 3.0,
            4
        )

        structural_fragility_index = round(
            (
                failure_propagation_risk +
                (1.0 - civilizational_regime_meta_index) +
                (1.0 - longitudinal_persistence_forecast_index)
            ) / 3.0,
            4
        )

        civilizational_fragility_map = {
            "fragility_hotspots": fragility_hotspots,
            "failure_propagation_risk": failure_propagation_risk,
            "structural_fragility_index": structural_fragility_index,
        }

        if structural_fragility_index < 0.10:
            fragility_classification = "robust_structure"
        elif structural_fragility_index < 0.25:
            fragility_classification = "functional_structure"
        elif structural_fragility_index < 0.50:
            fragility_classification = "fragile_structure"
        else:
            fragility_classification = "critical_structure"

        # A19.2-R.7 Collapse Resistance Estimation

        anti_fragility_contribution = round(
            max(0.0, regime_meta_resilience_index - structural_fragility_index),
            4
        )

        failure_absorption_capacity = round(
            (
                regime_meta_resilience_index +
                (1.0 - failure_propagation_risk)
            ) / 2.0,
            4
        )

        recovery_reserve_index = round(
            (
                longitudinal_persistence_forecast_index +
                civilizational_regime_meta_index
            ) / 2.0,
            4
        )

        collapse_resistance_index = round(
            (
                failure_absorption_capacity +
                recovery_reserve_index +
                anti_fragility_contribution
            ) / 3.0,
            4
        )

        civilizational_collapse_resistance = round(
            (
                collapse_resistance_index +
                (1.0 - structural_fragility_index)
            ) / 2.0,
            4
        )

        if civilizational_collapse_resistance >= 0.90:
            collapse_resistance_class = "high_collapse_resistance"
        elif civilizational_collapse_resistance >= 0.75:
            collapse_resistance_class = "functional_collapse_resistance"
        elif civilizational_collapse_resistance >= 0.50:
            collapse_resistance_class = "fragile_collapse_resistance"
        else:
            collapse_resistance_class = "critical_collapse_resistance"



        # A19.2-R.8 Robustness Meta-Synthesis

        robustness_meta_index = round(((collapse_resistance_index + civilizational_collapse_resistance + (1.0 - structural_fragility_index) + regime_meta_resilience_index) / 4.0), 4)

        robustness_forecast_score = round(((longitudinal_persistence_forecast_index + regime_survival_probability + civilizational_regime_meta_index) / 3.0), 4)

        civilizational_robustness_index = round(((robustness_meta_index + robustness_forecast_score + civilizational_collapse_resistance) / 3.0), 4)

        robustness_certification_score = round(((civilizational_robustness_index + collapse_resistance_index + (1.0 - failure_propagation_risk)) / 3.0), 4)

        if robustness_certification_score >= 0.90:
            robustness_classification = "persistent_civilizational_robustness"
        elif robustness_certification_score >= 0.75:
            robustness_classification = "functional_civilizational_robustness"
        elif robustness_certification_score >= 0.50:
            robustness_classification = "fragile_civilizational_robustness"
        else:
            robustness_classification = "critical_civilizational_robustness"



        # A19.3-R.1 Historical Continuity Tracking

        historical_continuity_index = round(
            (
                persistence +
                trend_persistence_index +
                regime_stability_index +
                civilizational_robustness_index
            ) / 4.0,
            4
        )

        trajectory_preservation_index = round(
            (
                persistent_regime_index +
                attractor_resilience +
                projection_convergence_index
            ) / 3.0,
            4
        )

        historical_memory_integrity = round(
            (
                historical_persistence_index +
                distributed_memory_persistence_index +
                longitudinal_continuity_index
            ) / 3.0,
            4
        )

        long_term_memory_persistence = round(
            (
                historical_memory_integrity +
                persistence +
                long_term_stability_index
            ) / 3.0,
            4
        )

        civilizational_historical_integrity = round(
            (
                historical_continuity_index +
                trajectory_preservation_index +
                historical_memory_integrity +
                long_term_memory_persistence
            ) / 4.0,
            4
        )

        # A19.3-R.2 Historical Memory Drift Analysis

        memory_drift_rate = round(
            (
                trajectory_drift_rate +
                drift_accumulation_index +
                (1.0 - historical_memory_integrity)
            ) / 3.0,
            4
        )

        historical_drift_index = round(
            (
                memory_drift_rate +
                regime_drift_index +
                (1.0 - historical_continuity_index)
            ) / 3.0,
            4
        )

        trajectory_conservation_score = round(
            (
                trajectory_preservation_index +
                (1.0 - historical_drift_index)
            ) / 2.0,
            4
        )

        historical_coherence_index = round(
            (
                civilizational_historical_integrity +
                trajectory_conservation_score +
                (1.0 - memory_drift_rate)
            ) / 3.0,
            4
        )

        # A19.3-R.3 Trajectory Conservation Analysis

        trajectory_divergence_index = round(
            (
                historical_drift_index +
                regime_drift_index +
                (1.0 - projection_convergence_index)
            ) / 3.0,
            4
        )

        trajectory_conservation_index = round(
            (
                trajectory_preservation_index +
                trajectory_conservation_score +
                (1.0 - trajectory_divergence_index)
            ) / 3.0,
            4
        )

        historical_branching_factor = round(
            min(
                1.0,
                len(true_strongly_connected_components)
                / max(1, len(set(self._regime_history)))
            ),
            4
        )

        trajectory_fidelity_score = round(
            (
                trajectory_conservation_index +
                historical_coherence_index +
                (1.0 - historical_branching_factor * 0.25)
            ) / 3.0,
            4
        )

        # A19.3-R.4 Historical Integrity Forecasting

        historical_integrity_forecast = round(
            (
                civilizational_historical_integrity +
                trajectory_fidelity_score +
                longitudinal_persistence_forecast_index
            ) / 3.0,
            4
        )

        historical_survival_probability = round(
            (
                historical_integrity_forecast +
                regime_survival_probability +
                (1.0 - historical_drift_index)
            ) / 3.0,
            4
        )

        continuity_forecast_horizon = round(
            forecast_stability_horizon *
            historical_survival_probability,
            4
        )

        historical_forecast_confidence = round(
            (
                persistence_confidence_index +
                projection_convergence_index +
                historical_survival_probability
            ) / 3.0,
            4
        )

        # A19.3-R.5 Historical Continuity Meta-Synthesis

        historical_meta_stability_index = round(
            (
                historical_continuity_index +
                historical_memory_integrity +
                historical_coherence_index
            ) / 3.0,
            4
        )

        historical_meta_resilience_index = round(
            (
                trajectory_conservation_index +
                trajectory_fidelity_score +
                (1.0 - historical_drift_index)
            ) / 3.0,
            4
        )

        historical_meta_forecast_index = round(
            (
                historical_integrity_forecast +
                historical_survival_probability +
                historical_forecast_confidence
            ) / 3.0,
            4
        )

        civilizational_historical_meta_index = round(
            (
                historical_meta_stability_index +
                historical_meta_resilience_index +
                historical_meta_forecast_index +
                civilizational_historical_integrity
            ) / 4.0,
            4
        )

        if civilizational_historical_meta_index >= 0.90:
            historical_continuity_certification = "persistent_historical_continuity"
        elif civilizational_historical_meta_index >= 0.75:
            historical_continuity_certification = "functional_historical_continuity"
        else:
            historical_continuity_certification = "fragile_historical_continuity"
        
        civilizational_identity_index = round(
            (historical_continuity_index + trajectory_conservation_index + civilizational_historical_meta_index) / 3.0, 4
        )
        identity_persistence_score = round(
            (longitudinal_persistence_forecast_index + historical_survival_probability + trajectory_fidelity_score) / 3.0, 4
        )
        identity_drift_index = round(
            (historical_drift_index + regime_drift_index + trajectory_divergence_index) / 3.0, 4
        )
        identity_integrity_score = round(
            (civilizational_historical_integrity + historical_coherence_index + trajectory_fidelity_score) / 3.0, 4
        )

        self._identity_history.append(civilizational_identity_index)
        self._identity_drift_history.append(identity_drift_index)

        if len(self._identity_drift_history) >= 2:
            identity_drift_velocity = round(
                self._identity_drift_history[-1] - self._identity_drift_history[-2], 4
            )
        else:
            identity_drift_velocity = 0.0

        self._identity_drift_velocity_history.append(identity_drift_velocity)

        if len(self._identity_drift_velocity_history) >= 2:
            identity_drift_acceleration = round(
                self._identity_drift_velocity_history[-1] - self._identity_drift_velocity_history[-2], 4
            )
        else:
            identity_drift_acceleration = 0.0

        identity_coherence_index = round(
            (
                civilizational_identity_index +
                identity_integrity_score +
                historical_coherence_index +
                trajectory_fidelity_score
            ) / 4.0,
            4
        )

        identity_discontinuity_risk = round(
            min(
                1.0,
                (
                    identity_drift_index +
                    abs(identity_drift_velocity) +
                    abs(identity_drift_acceleration) +
                    (1.0 - identity_coherence_index)
                ) / 4.0
            ),
            4
        )


        
        # A19.4-R.3 Identity Conservation Analysis

        identity_conservation_index = round(
            (
                trajectory_conservation_index +
                civilizational_identity_index +
                (1.0 - identity_drift_index)
            ) / 3.0,
            4
        )

        identity_fidelity_score = round(
            (
                trajectory_fidelity_score +
                identity_integrity_score +
                identity_coherence_index
            ) / 3.0,
            4
        )

        identity_branching_factor = round(
            historical_branching_factor,
            4
        )

        identity_resilience_index = round(
            (
                identity_conservation_index +
                identity_fidelity_score +
                (1.0 - identity_discontinuity_risk)
            ) / 3.0,
            4
        )
        
        # A19.4-R.4 Identity Persistence Forecasting

        identity_persistence_forecast = round(
            (
                identity_persistence_score +
                identity_conservation_index +
                longitudinal_persistence_forecast_index
            ) / 3.0,
            4
        )

        identity_survival_probability = round(
            (
                identity_persistence_forecast +
                identity_resilience_index +
                (1.0 - identity_discontinuity_risk)
            ) / 3.0,
            4
        )

        identity_forecast_horizon = round(
            continuity_forecast_horizon *
            identity_survival_probability,
            4
        )

        identity_forecast_confidence = round(
            (
                historical_forecast_confidence +
                identity_resilience_index +
                identity_survival_probability
            ) / 3.0,
            4
        )
        
        # A19.4-R.5 Extended Longitudinal Certification Meta-Synthesis

        civilizational_certification_index = round(
            (
                civilizational_robustness_index +
                civilizational_historical_meta_index +
                civilizational_identity_index +
                longitudinal_persistence_forecast_index +
                identity_persistence_forecast
            ) / 5.0,
            4
        )

        certification_confidence_score = round(
            (
                robustness_certification_score +
                historical_forecast_confidence +
                identity_forecast_confidence
            ) / 3.0,
            4
        )

        resilience_confirmation = (
            civilizational_robustness_index >= 0.90
            and identity_resilience_index >= 0.90
        )

        ninety_day_readiness = (
            identity_survival_probability >= 0.90
            and longitudinal_persistence_forecast_index >= 0.90
        )

        extended_longitudinal_certification = (
            civilizational_certification_index >= 0.90
            and certification_confidence_score >= 0.90
            and resilience_confirmation
            and ninety_day_readiness
        )

        if extended_longitudinal_certification:
            extended_longitudinal_certification_class = "persistent_extended_longitudinal_certification"
        elif civilizational_certification_index >= 0.75:
            extended_longitudinal_certification_class = "functional_extended_longitudinal_certification"
        else:
            extended_longitudinal_certification_class = "fragile_extended_longitudinal_certification"

        multi_step_projection_horizon = 10
        return {
            "success": True,
            "civilizational_longitudinal_stability_index": round(index, 4),
            "civilizational_regression_risk": round(risk, 4),
            "longitudinal_persistence_index": round(persistence, 4),
            "observation_count": len(self._history),
            "trend": trend,
            "persistent_improvement_ratio": round(persistent_improvement_ratio, 4),
            "persistent_degradation_ratio": round(persistent_degradation_ratio, 4),
            "trend_persistence_index": round(trend_persistence_index, 4),
            "trend_reversal_detection": trend_reversal_detection,
            "trend_stability": round(trend_stability, 4),
            "trend_persistence_class": trend_persistence_class,
            "short_term_window_index": round(short_term_window_index, 4),
            "medium_term_window_index": round(medium_term_window_index, 4),
            "window_consistency": round(window_consistency, 4),
            "latest_drop": round(latest_drop, 4),
            "max_window_drop": round(max_window_drop, 4),
            "window_anomaly_detection": window_anomaly_detection,
            "sliding_window_stability_index": round(sliding_window_stability_index, 4),
            "window_stability_class": window_stability_class,
            "short_term_stability_index": round(sum(self._history[-3:]) / len(self._history[-3:]), 4),
            "medium_term_stability_index": round(sum(self._history[-5:]) / len(self._history[-5:]), 4),
            "long_term_stability_index": round(sum(self._history) / len(self._history), 4),
            "multi_scale_stability_alignment": round(
                1.0 - (
                    max(
                        sum(self._history[-3:]) / len(self._history[-3:]),
                        sum(self._history[-5:]) / len(self._history[-5:]),
                        sum(self._history) / len(self._history)
                    )
                    -
                    min(
                        sum(self._history[-3:]) / len(self._history[-3:]),
                        sum(self._history[-5:]) / len(self._history[-5:]),
                        sum(self._history) / len(self._history)
                    )
                ), 4),
            "cross_scale_stability_divergence": round(
                (
                    max(
                        sum(self._history[-3:]) / len(self._history[-3:]),
                        sum(self._history[-5:]) / len(self._history[-5:]),
                        sum(self._history) / len(self._history)
                    )
                    -
                    min(
                        sum(self._history[-3:]) / len(self._history[-3:]),
                        sum(self._history[-5:]) / len(self._history[-5:]),
                        sum(self._history) / len(self._history)
                    )
                ), 4),
            "multi_scale_stability_index": round(
                (
                    (sum(self._history[-3:]) / len(self._history[-3:]))
                    + (sum(self._history[-5:]) / len(self._history[-5:]))
                    + (sum(self._history) / len(self._history))
                ) / 3.0, 4),
            "cross_scale_divergence_penalty": round(abs((sum(self._history[-3:]) / len(self._history[-3:])) - (sum(self._history) / len(self._history))), 4),
            "divergence_adjusted_multi_scale_index": round(max(0.0, (((sum(self._history[-3:]) / len(self._history[-3:])) + (sum(self._history[-5:]) / len(self._history[-5:])) + (sum(self._history) / len(self._history))) / 3.0) - abs((sum(self._history[-3:]) / len(self._history[-3:])) - (sum(self._history) / len(self._history)))), 4),
            "multi_scale_stability_class": (
                "persistent_multi_scale_stability"
                if round(max(0.0, (((sum(self._history[-3:]) / len(self._history[-3:])) + (sum(self._history[-5:]) / len(self._history[-5:])) + (sum(self._history) / len(self._history))) / 3.0) - abs((sum(self._history[-3:]) / len(self._history[-3:])) - (sum(self._history) / len(self._history)))), 4) >= 0.90
                else (
                    "functional_multi_scale_stability"
                    if round(max(0.0, (((sum(self._history[-3:]) / len(self._history[-3:])) + (sum(self._history[-5:]) / len(self._history[-5:])) + (sum(self._history) / len(self._history))) / 3.0) - abs((sum(self._history[-3:]) / len(self._history[-3:])) - (sum(self._history) / len(self._history)))), 4) >= 0.75
                    else "fragile_multi_scale_stability"
                )
            ),
            "regime_classification": regime_classification,
            "regime_transition_count": regime_transition_count,
            "regime_transition_matrix": dict(self._transition_matrix),
            "dominant_regime": dominant_regime,
            "regime_stability_index": round(regime_stability_index, 4),
            "regime_transition_history": self._regime_history[-20:],
            "mean_regime_residence_time": mean_regime_residence_time,
            "regime_escape_probability": regime_escape_probability,
            "regime_absorption_probability": regime_absorption_probability,
            "persistent_regime_index": persistent_regime_index,
            "dominant_attractor_regime": dominant_attractor_regime,
            "attractor_strength": attractor_strength,
            "attractor_resilience": attractor_resilience,
            "basin_size": basin_size,
            "basin_dominance_index": basin_dominance_index,
            "escape_difficulty": escape_difficulty,
            "forecast_regime_distribution": forecast_regime_distribution,
            "future_regime_probability": future_regime_probability,
            "attractor_retention_probability": attractor_retention_probability,
            "expected_escape_horizon": expected_escape_horizon,
            "attractor_convergence_index": attractor_convergence_index,
            "empirical_escape_horizon": empirical_escape_horizon,
            "empirical_regime_half_life": empirical_regime_half_life,
            "forecast_stability_horizon": forecast_stability_horizon,

            "forecast_transition_graph": forecast_transition_graph,
            "forecast_two_step_distribution": forecast_two_step_distribution,
            "graph_complexity": graph_complexity,
            "graph_entropy": graph_entropy,

            "multi_step_projection_horizon": multi_step_projection_horizon,
            "projection_t_plus_2": projection_t_plus_2,
            "projection_t_plus_5": projection_t_plus_5,
            "projection_t_plus_10": projection_t_plus_10,
            "long_horizon_regime_distribution": long_horizon_regime_distribution,
            "projected_dominant_regime": projected_dominant_regime,
            "projected_regime_entropy": projected_regime_entropy,
            "projection_convergence_index": projection_convergence_index,
            "reachable_regimes": reachable_regimes,
            "unreachable_regimes": unreachable_regimes,
            "communicating_classes": communicating_classes,
            "absorbing_regimes": absorbing_regimes,
            "strongly_connected_components": strongly_connected_components,
            "longitudinal_openness_index": longitudinal_openness_index,
            "true_reachable_regimes": true_reachable_regimes,
            "true_unreachable_regimes": true_unreachable_regimes,
            "true_communicating_classes": true_communicating_classes,
            "true_strongly_connected_components": true_strongly_connected_components,
            "closed_attractor_components": closed_attractor_components,
            "graph_reachability_index": graph_reachability_index,

            "closed_communicating_classes": closed_attractor_components,
            "recurrent_communicating_classes": true_strongly_connected_components,
            "transient_communicating_classes": [
                c for c in true_strongly_connected_components
                if c not in closed_attractor_components
            ],
            "communication_closure_index": round(
                len(closed_attractor_components)
                / max(1, len(true_strongly_connected_components)),
                4
            ),
            "global_communication_index": round(
                graph_reachability_index,
                4
            ),

            "recurrence_count": recurrence_count,
            "recurrence_density": recurrence_density,
            "recurrence_frequency": recurrence_frequency,
            "mean_recurrence_interval": mean_recurrence_interval,
            "attractor_recurrence_strength": attractor_recurrence_strength,
            "civilizational_recurrence_index": civilizational_recurrence_index,

            "regime_volatility_index": regime_volatility_index,
            "regime_coherence_index": regime_coherence_index,
            "regime_resilience_score": regime_resilience_score,
            "regime_stability_score": regime_stability_score,
            "longitudinal_regime_stability_index": longitudinal_regime_stability_index,

            "trajectory_drift_rate": trajectory_drift_rate,
            "drift_accumulation_index": drift_accumulation_index,
            "attractor_distance": attractor_distance,
            "latent_regime_shift_score": latent_regime_shift_score,
            "regime_drift_index": regime_drift_index,
            "drift_classification": drift_classification,

            "attractor_persistence_forecast": attractor_persistence_forecast,
            "forecasted_regime_persistence": forecasted_regime_persistence,
            "persistence_confidence_index": persistence_confidence_index,
            "regime_survival_probability": regime_survival_probability,
            "longitudinal_persistence_forecast_index": longitudinal_persistence_forecast_index,
            "persistence_forecast_class": persistence_forecast_class,
            
            "regime_meta_stability_index": regime_meta_stability_index,
            "regime_meta_resilience_index": regime_meta_resilience_index,
            "regime_meta_forecast_index": regime_meta_forecast_index,
            "civilizational_regime_meta_index": civilizational_regime_meta_index,
            "regime_ecology_class": regime_ecology_class,

            "fragility_hotspots": fragility_hotspots,
            "critical_dependencies": critical_dependencies,
            "failure_propagation_risk": failure_propagation_risk,
            "structural_fragility_index": structural_fragility_index,
            "civilizational_fragility_map": civilizational_fragility_map,
            "fragility_classification": fragility_classification,

            "anti_fragility_contribution": anti_fragility_contribution,
            "failure_absorption_capacity": failure_absorption_capacity,
            "recovery_reserve_index": recovery_reserve_index,
            "collapse_resistance_index": collapse_resistance_index,
            "civilizational_collapse_resistance": civilizational_collapse_resistance,
            "collapse_resistance_class": collapse_resistance_class,


            "robustness_meta_index": robustness_meta_index,
            "robustness_forecast_score": robustness_forecast_score,
            "civilizational_robustness_index": civilizational_robustness_index,
            "robustness_certification_score": robustness_certification_score,
            "robustness_classification": robustness_classification,


            "historical_continuity_index": historical_continuity_index,
            "trajectory_preservation_index": trajectory_preservation_index,
            "historical_memory_integrity": historical_memory_integrity,
            "long_term_memory_persistence": long_term_memory_persistence,
            "civilizational_historical_integrity": civilizational_historical_integrity,

            "historical_drift_index": historical_drift_index,
            "memory_drift_rate": memory_drift_rate,
            "trajectory_conservation_score": trajectory_conservation_score,
            "historical_coherence_index": historical_coherence_index,

            "trajectory_divergence_index": trajectory_divergence_index,
            "trajectory_conservation_index": trajectory_conservation_index,
            "historical_branching_factor": historical_branching_factor,
            "trajectory_fidelity_score": trajectory_fidelity_score,

            "historical_integrity_forecast": historical_integrity_forecast,
            "historical_survival_probability": historical_survival_probability,
            "continuity_forecast_horizon": continuity_forecast_horizon,
            "historical_forecast_confidence": historical_forecast_confidence,

            "historical_meta_stability_index": historical_meta_stability_index,
            "historical_meta_resilience_index": historical_meta_resilience_index,
            "historical_meta_forecast_index": historical_meta_forecast_index,
            "civilizational_historical_meta_index": civilizational_historical_meta_index,
            "historical_continuity_certification": historical_continuity_certification,
            "civilizational_identity_index": round((historical_continuity_index + trajectory_conservation_index + civilizational_historical_meta_index) / 3.0, 4),
            "identity_persistence_score": round((longitudinal_persistence_forecast_index + historical_survival_probability + trajectory_fidelity_score) / 3.0, 4),
            "identity_drift_index": round((historical_drift_index + regime_drift_index + trajectory_divergence_index) / 3.0, 4),
            "identity_integrity_score": round((civilizational_historical_integrity + historical_coherence_index + trajectory_fidelity_score) / 3.0, 4),
            "identity_drift_velocity": identity_drift_velocity,
            "identity_drift_acceleration": identity_drift_acceleration,
            "identity_discontinuity_risk": identity_discontinuity_risk,
            "identity_coherence_index": identity_coherence_index,
            "identity_conservation_index": identity_conservation_index,
            "identity_fidelity_score": identity_fidelity_score,
            "identity_branching_factor": identity_branching_factor,
            "identity_resilience_index": identity_resilience_index,
            "identity_persistence_forecast": identity_persistence_forecast,
            "identity_survival_probability": identity_survival_probability,
            "identity_forecast_horizon": identity_forecast_horizon,
            "identity_forecast_confidence": identity_forecast_confidence,
            "civilizational_certification_index": civilizational_certification_index,
            "certification_confidence_score": certification_confidence_score,
            "resilience_confirmation": resilience_confirmation,
            "ninety_day_readiness": ninety_day_readiness,
            "extended_longitudinal_certification": extended_longitudinal_certification,
            "extended_longitudinal_certification_class": extended_longitudinal_certification_class,




            "classification": classification,






        }
