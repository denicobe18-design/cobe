"""Sedam zasebnih mozgova. Svaki glasa iz svojih težina i sam se podešava."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any

from doxa.types import Doctrine


@dataclass
class Brain:
    name: str
    weights: list[float]
    bias: float
    threshold: float
    shift: float = 0.0
    seen: int = 0
    wins: int = 0
    reward: float = 0.0
    generation: int = 0
    memory: dict[str, dict[str, float]] = field(default_factory=dict)

    def remember(self, key: str, reward: float) -> None:
        slot = dict(self.memory.get(key) or {})
        seen = int(slot.get("n", 0)) + 1
        ema = float(slot.get("ema", 0.0))
        ema += (reward - ema) / seen
        self.memory[key] = {"ema": ema, "n": float(seen)}

    def cold(self, key: str) -> bool:
        """Igra koja je nekoliko puta izgubila više se ne nudi."""
        slot = self.memory.get(key) or {}
        seen = int(slot.get("n", 0))
        if seen < 4:
            return False
        return float(slot.get("ema", 0.0)) < -0.012

    def belief(self, features: list[float]) -> float:
        score = self.bias
        for weight, feature in zip(self.weights, features):
            score += weight * feature
        if score >= 0:
            return 1.0 / (1.0 + math.exp(-score))
        expo = math.exp(score)
        return expo / (1.0 + expo)

    def vote(self, features: list[float]) -> tuple[bool, float]:
        probability = self.belief(features)
        return probability >= self.threshold, probability

    def learn(self, features: list[float], won: bool, reward: float) -> None:
        """Jedan korak logističke regresije, pa prag prema vlastitom rezultatu."""
        probability = self.belief(features)
        error = (1.0 if won else 0.0) - probability
        rate = 0.55
        self.weights = [
            max(-4.0, min(4.0, weight + rate * error * feature))
            for weight, feature in zip(self.weights, features)
        ]
        self.bias = max(-3.0, min(3.0, self.bias + rate * error * 0.5))
        self.seen += 1
        if won:
            self.wins += 1
        self.reward += (reward - self.reward) / self.seen
        if won:
            self.threshold = max(0.40, self.threshold - 0.008)
        else:
            self.threshold = min(0.74, self.threshold + 0.015)
        if self.seen % 5 == 0:
            rate_won = self.wins / self.seen
            if rate_won >= 0.55:
                self.threshold = max(0.40, self.threshold - 0.02)
            elif rate_won <= 0.40:
                self.threshold = min(0.74, self.threshold + 0.02)
        self.generation += 1


def default_brains() -> dict[str, Brain]:
    specs = {
        "whale": ([2.4, 1.8, 0.5, 0.3], -2.2, 0.56),
        "guard": ([1.2, 1.4, 0.4, 0.3], -1.2, 0.55),
        "skeptic": ([1.5, 1.2, 0.8, 0.6], -1.8, 0.52),
        "trail": ([0.8, 0.8, 0.4, 0.6], -0.6, 0.45),
        "radar": ([0.4, 1.4, 0.6, 0.5], -1.3, 0.50),
        "mtf": ([1.8, 1.7, 0.6, 0.8], -2.3, 0.62),
        "kelly": ([1.2, 0.8, 1.0, 0.4], -1.5, 0.50),
    }
    brains: dict[str, Brain] = {}
    for name, (weights, bias, threshold) in specs.items():
        brains[name] = Brain(name=name, weights=list(weights), bias=bias, threshold=threshold)
    return brains


def restore_brains(raw: Any) -> dict[str, Brain]:
    brains = default_brains()
    if not isinstance(raw, dict):
        return brains
    for name, item in raw.items():
        if name not in brains or not isinstance(item, dict):
            continue
        base = brains[name]
        weights = item.get("weights")
        if not isinstance(weights, list) or len(weights) != 4:
            weights = list(base.weights)
        brains[name] = Brain(
            name=name,
            weights=[float(value) for value in weights],
            bias=float(item.get("bias", base.bias)),
            threshold=float(item.get("threshold", base.threshold)),
            shift=float(item.get("shift", 0.0)),
            seen=int(item.get("seen", 0)),
            wins=int(item.get("wins", 0)),
            reward=float(item.get("reward", 0.0)),
            generation=int(item.get("generation", 0)),
            memory=_memory(item.get("memory")),
        )
    return brains


def _memory(raw: Any) -> dict[str, dict[str, float]]:
    if not isinstance(raw, dict):
        return {}
    cleaned: dict[str, dict[str, float]] = {}
    for key, slot in raw.items():
        if not isinstance(slot, dict):
            continue
        cleaned[str(key)] = {"ema": float(slot.get("ema", 0.0)), "n": float(slot.get("n", 0))}
    return cleaned


def brains_to_plain(brains: dict[str, Brain]) -> dict[str, dict[str, Any]]:
    return {name: asdict(brain) for name, brain in brains.items()}


def tune(doctrine: Doctrine, brains: dict[str, Brain]) -> None:
    """Primijeni osobni pomak svakog mozga, pa vrati doktrinu u tvrde granice."""
    doctrine.whale_min += brains["whale"].shift
    doctrine.btc_drop += brains["guard"].shift
    doctrine.rsi_veto += brains["skeptic"].shift
    doctrine.atr_mult += brains["trail"].shift
    doctrine.sentiment_boost += brains["radar"].shift
    doctrine.kelly_cap += brains["kelly"].shift
    doctrine.mtf_rsi_low += brains["mtf"].shift
    doctrine.__dict__.update(doctrine.clamped().__dict__)


_NUDGE = {
    "whale": (0.01, -0.006, -0.07, 0.16),
    "guard": (-0.0005, 0.0003, -0.003, 0.004),
    "skeptic": (-0.8, 0.4, -8.0, 6.0),
    "trail": (-0.08, 0.05, -0.2, 0.4),
    "radar": (-0.04, 0.03, -0.25, 0.2),
    "kelly": (-0.02, 0.015, -0.2, 0.15),
    "mtf": (0.4, -0.3, -6.0, 6.0),
}


def learn_pack(brains: dict[str, Brain], context: dict[str, Any], pnl: float, pnl_pct: float) -> list[str]:
    """Svaki mozak uči samo iz značajki koje je sam vidio na ulazu."""
    saved = context.get("brains") or {}
    if not isinstance(saved, dict):
        return []
    won = pnl > 0
    reward = max(-1.0, min(1.0, float(pnl_pct)))
    notes: list[str] = []
    for name, brain in brains.items():
        item = saved.get(name)
        if not isinstance(item, dict):
            continue
        features = item.get("x")
        if not isinstance(features, list) or len(features) != 4:
            continue
        voted = bool(item.get("yes"))
        brain.learn([float(value) for value in features], won, reward)
        loss_step, win_step, low, high = _NUDGE[name]
        if voted:
            brain.shift += win_step if won else loss_step
            lead = str(context.get("lead") or "pack")
            brain.remember(lead, reward)
        elif won:
            brain.shift += win_step * 0.5
        brain.shift = max(low, min(high, brain.shift))
        belief = brain.belief([float(value) for value in features])
        slot = brain.memory.get(str(context.get("lead") or "pack")) or {}
        edge = float(slot.get("ema", brain.reward))
        notes.append(
            f"{name} gen {brain.generation} prag {brain.threshold * 100:.0f}% "
            f"vjera {belief * 100:.0f}% rub {edge * 100:.1f}%"
        )
    return notes
