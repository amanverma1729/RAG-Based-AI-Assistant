import logging
from typing import List, Dict, Optional
import time
import re

logger = logging.getLogger(__name__)

class EvaluationLogger:
    """
    Research-Grade Evaluation System for RAG.
    Tracks Faithfulness, Answer Relevance, and Retrieval Precision.
    """
    def __init__(self):
        self.traces = []

    def _calculate_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """
        Simulates Faithfulness: What % of the answer is derived from context?
        In a research paper, this is often done via NLI (Natural Language Inference) or LLM-as-a-judge.
        Here we use a keyword-overlap proxy for local execution.
        """
        if not contexts or not answer: return 0.0
        
        combined_context = " ".join(contexts).lower()
        sentences = re.split(r'[.!?]', answer)
        grounded_sentences = 0
        
        valid_sentences = [s for s in sentences if len(s.strip()) > 10]
        if not valid_sentences: return 1.0
        
        for sent in valid_sentences:
            words = sent.lower().split()
            # If 30% of words in a sentence appear in context, we consider it 'likely grounded'
            matches = sum(1 for word in words if word in combined_context and len(word) > 3)
            if matches / max(len(words), 1) > 0.3:
                grounded_sentences += 1
                
        return round(grounded_sentences / len(valid_sentences), 2)

    def log_trace(
        self, 
        query: str, 
        contexts: List[str], 
        answer: str, 
        latency_ms: float = 0.0
    ):
        """Logs a RAG trace with calculated metrics."""
        faithfulness = self._calculate_faithfulness(answer, contexts)
        
        # Hallucination check: If faithfulness is low but answer is long
        is_hallucination = faithfulness < 0.4 and len(answer) > 100
        
        trace = {
            "query": query,
            "contexts": contexts,
            "answer": answer,
            "latency_ms": latency_ms,
            "faithfulness": faithfulness,
            "is_hallucination": is_hallucination,
            "timestamp": time.time()
        }
        self.traces.append(trace)
        logger.info(f"Research Trace: Faithfulness={faithfulness}, Hallucination={is_hallucination}")

    def get_dashboard_metrics(self) -> Dict:
        """Aggregates research metrics for the dashboard."""
        if not self.traces:
            return {
                "total_queries": 0, 
                "avg_latency_ms": 0, 
                "avg_faithfulness": 0.0,
                "hallucination_rate": 0.0
            }
            
        avg_lat = sum(t["latency_ms"] for t in self.traces) / len(self.traces)
        avg_faith = sum(t["faithfulness"] for t in self.traces) / len(self.traces)
        hallucinations = sum(1 for t in self.traces if t["is_hallucination"])
        
        return {
            "total_queries": len(self.traces),
            "avg_latency_ms": round(avg_lat, 2),
            "avg_faithfulness": round(avg_faith, 2),
            "hallucination_rate": round(hallucinations / len(self.traces), 2)
        }

    def compare_rag_impact(self, query: str, answer_with_rag: str, answer_without_rag: str) -> Dict:
        """
        Comparison logic for the 'Research Comparison' feature.
        Highlights the reduction in hallucination when context is provided.
        """
        # Logic: Answer without RAG often lacks specific entities or contains generic padding
        entities_with = len(re.findall(r'[A-Z][a-z]+', answer_with_rag))
        entities_without = len(re.findall(r'[A-Z][a-z]+', answer_without_rag))
        
        return {
            "query": query,
            "rag_benefit": "Higher Fact Density" if entities_with > entities_without else "Similar Output",
            "grounding_delta": f"+{entities_with - entities_without} facts"
        }

# Global singleton
eval_logger = EvaluationLogger()
