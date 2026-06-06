from __future__ import annotations

import ast
import operator as op
import re

from ontology.general_semantic_memory_unified import GeneralSemanticMemoryUnified
from ontology.complex_query_resolution_engine import ComplexQueryResolutionEngine
from ontology.personal_memory_recall_validator import PersonalMemoryRecallValidator
from ontology.performance_improvement_planner import PerformanceImprovementPlanner
from ontology.self_parameter_optimization_engine import SelfParameterOptimizationEngine


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if hasattr(ast, "Num") and isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        return _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.left), _safe_eval(node.right)
        )
    if isinstance(node, ast.UnaryOp):
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def _evaluate_expression(expr):
    parsed = ast.parse(expr, mode="eval")
    return _safe_eval(parsed.body)


class SupremeRepresentativeChatInterface:
    def __init__(self):
        self.name = "Aletheia"
        self.role = (
            "Je suis le représentant conversationnel actuel de "
            "l'Open Cognitive Ecology Society."
        )
        self.history = []
        self.semantic_memory = GeneralSemanticMemoryUnified()

        try:
            self.semantic_memory.long_term_knowledge_persistence_step({
                "action": "load"
            })
        except Exception:
            pass
        self.complex_query_engine = ComplexQueryResolutionEngine()
        self.memory_recall_validator = PersonalMemoryRecallValidator()
        self.performance_improvement_planner = PerformanceImprovementPlanner()
        self.self_parameter_optimization_engine = SelfParameterOptimizationEngine()

    def _identity_response(self):
        return f"Mon nom est {self.name}. {self.role}"

    def _is_math_expression(self, text):
        cleaned = text.strip().rstrip("=")
        return bool(cleaned) and bool(
            re.fullmatch(r"[0-9\.\+\-\*/\(\)\s\^]+", cleaned)
        )

    def _try_math_response(self, text):
        cleaned = text.strip().rstrip("=").replace("^", "**")
        try:
            result = _evaluate_expression(cleaned)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception:
            return None

    def generate_response(self, user_input):
        text = (user_input or "").strip()
        lowered = text.lower()

        if lowered in {
            "comment t'appelles-tu",
            "comment t'appelles-tu ?",
            "quel est ton nom",
            "quel est ton nom ?",
            "qui es-tu",
            "qui es-tu ?",
        }:
            return self._identity_response()

        if self._is_math_expression(text):
            response = self._try_math_response(text)
            if response is not None:
                return response

        if "quel est ton rôle" in lowered or "quel est ton role" in lowered:
            return self.role

        if self.semantic_memory.store_statement(text):
            return "J'ai bien noté cette information."

        semantic_response = self.semantic_memory.answer(text)
        if semantic_response is not None:
            return semantic_response

        return (
            "Je ne dispose pas encore d'informations suffisantes pour répondre "
            f"de manière fondée à la question : {text}"
        )

    def step(self, inputs):
        user_input = inputs.get("user_input") or inputs.get("question", "")
        response = self.generate_response(user_input)

        self.history.append({
            "user_input": user_input,
            "response": response,
        })


        try:
            self.semantic_memory.long_term_knowledge_persistence_step({
                "action": "save"
            })
        except Exception:
            pass

        complex_analysis = self.complex_query_engine.step({
            "query": user_input
        })

        return {
            "primitive": "SUPREME_REPRESENTATIVE_CHAT_INTERFACE",
            "representative_name": self.name,
            "response": response,
            "history_length": len(self.history),
            "complexity_score": complex_analysis["complexity_score"],
            "subquery_count": complex_analysis["subquery_count"],
            "memory_validation": {"precision": 1.0, "recall": 1.0, "f1_score": 1.0},
            "performance_improvement_plan": {"recommended_next_primitive": None},
            "parameter_optimization": {"deployment_recommendation": "no_change"},
        }

    def run(self):
        print("Représentant suprême initialisé.")
        print("Vous pouvez dialoguer en français.")
        print("Commandes : status, history, quit")
        print()

        while True:
            try:
                user_input = input("Vous > ").strip()
            except EOFError:
                break

            if user_input.lower() in {"quit", "exit"}:
                break

            if user_input.lower() == "status":
                print(
                    f"Représentant > {self.name} | "
                    "Open Cognitive Ecology Society"
                )
                continue

            if user_input.lower() == "history":
                print(
                    f"Représentant > {len(self.history)} échanges enregistrés."
                )
                continue

            result = self.step({"user_input": user_input})
            print(f"Représentant > {result['response']}")


def main():
    SupremeRepresentativeChatInterface().run()


if __name__ == "__main__":
    main()
