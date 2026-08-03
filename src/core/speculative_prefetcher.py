import time
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class PrefetchPrediction(BaseModel):
    """Speculatively predicted follow-up topic and preloaded context payload."""
    topic_key: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    preloaded_context: str
    is_cached: bool = False


class SpeculativePromptPrefetcher:
    """
    Mission 41: Dynamic Speculative Prompt Prefetching & Context Cache Engine.
    Predicts likely follow-up queries or context requirements and pre-warms the context cache.
    """

    def __init__(self, confidence_threshold: float = 0.60):
        self.confidence_threshold = confidence_threshold
        self._intent_rules: Dict[str, List[Dict[str, Any]]] = {}
        self._prewarmed_cache: Dict[str, str] = {}

    def register_intent_prediction_rule(
        self,
        trigger_keyword: str,
        predicted_topic: str,
        preloaded_context: str,
        confidence: float = 0.85
    ):
        """Registers a speculative intent association rule for pre-warming context."""
        if trigger_keyword not in self._intent_rules:
            self._intent_rules[trigger_keyword] = []

        self._intent_rules[trigger_keyword].append({
            "topic_key": predicted_topic,
            "preloaded_context": preloaded_context,
            "confidence": confidence
        })

    def predict_and_prefetch(self, current_prompt: str) -> List[PrefetchPrediction]:
        """
        Analyzes the incoming prompt, identifies triggered speculative intents,
        and pre-warms the context cache for immediate access on follow-up turns.
        """
        predictions: List[PrefetchPrediction] = []
        lower_prompt = current_prompt.lower()

        for trigger, rules in self._intent_rules.items():
            if trigger.lower() in lower_prompt:
                for rule in rules:
                    confidence = rule["confidence"]
                    if confidence >= self.confidence_threshold:
                        topic_key = rule["topic_key"]
                        context = rule["preloaded_context"]

                        # Pre-warm internal context cache
                        self._prewarmed_cache[topic_key] = context

                        predictions.append(
                            PrefetchPrediction(
                                topic_key=topic_key,
                                confidence_score=confidence,
                                preloaded_context=context,
                                is_cached=True
                            )
                        )

        return predictions

    def get_prewarmed_context(self, topic_key: str) -> Optional[str]:
        """Retrieves pre-fetched context from the cache if available."""
        return self._prewarmed_cache.get(topic_key)