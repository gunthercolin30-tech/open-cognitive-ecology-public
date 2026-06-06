
"""
collective_naming_protocol.py

Collective attribution of a name to a new individual through proposals,
votes, consensus scoring, and full decision traceability.
"""

from collections import Counter
from datetime import datetime


class CollectiveNamingProtocol:
    """Community-based naming protocol for new individuals."""

    def __init__(self):
        self.decision_counter = 0

    @staticmethod
    def _normalize_votes(candidate_names, votes):
        if not votes:
            votes = list(candidate_names)
        valid_votes = [v for v in votes if v in candidate_names]
        if not valid_votes:
            valid_votes = list(candidate_names)
        return valid_votes

    def step(self, inputs):
        self.decision_counter += 1

        candidate_names = inputs.get(
            "candidate_names",
            ["Aletheia", "Sophia", "Noesis"]
        )

        if not candidate_names:
            candidate_names = ["Unnamed"]

        votes = inputs.get("votes", list(candidate_names))
        valid_votes = self._normalize_votes(candidate_names, votes)

        vote_counts = Counter(valid_votes)
        total_votes = sum(vote_counts.values()) or 1

        assigned_name, winning_votes = sorted(
            vote_counts.items(),
            key=lambda item: (-item[1], item[0])
        )[0]

        consensus_score = winning_votes / total_votes
        naming_stability_index = consensus_score

        naming_decision_trace = {
            "decision_id": f"CNP-{self.decision_counter:04d}",
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "candidate_names": list(candidate_names),
            "votes": list(valid_votes),
            "total_votes": total_votes,
            "winning_votes": winning_votes,
        }

        return {
            "primitive": "COLLECTIVE_NAMING_PROTOCOL",
            "candidate_names": list(candidate_names),
            "vote_distribution": dict(vote_counts),
            "consensus_score": consensus_score,
            "assigned_name": assigned_name,
            "naming_decision_trace": naming_decision_trace,
            "naming_stability_index": naming_stability_index,
        }
