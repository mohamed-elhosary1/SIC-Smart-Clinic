"""Functional programming closures and recursive visit search."""

from datetime import datetime
from typing import List, Callable
from .models import Patient, Appointment

def make_triage_calculator(base_fee: float = 100.0, initial_emergency_count: int = 0):
    """Closure capturing emergency_count using nonlocal with accessor functions."""
    emergency_count = int(initial_emergency_count)

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return base_fee * 1.5
        return base_fee

    def get_emergency_count() -> int:
        return emergency_count

    def decrement_emergency_count() -> int:
        nonlocal emergency_count
        if emergency_count > 0:
            emergency_count -= 1
        return emergency_count

    def reset_count():
        nonlocal emergency_count
        emergency_count = 0

    calculate.get_emergency_count = get_emergency_count
    calculate.decrement_emergency_count = decrement_emergency_count
    calculate.reset_count = reset_count
    return calculate


def find_visits_recursive(visits: list, index: int = 0) -> list:
    """Recursively filter completed appointments from visit history without loops."""
    if index >= len(visits):
        return []

    current = visits[index]
    rest = find_visits_recursive(visits, index + 1)

    if getattr(current, "status", None) == "completed":
        return [current] + rest
    return rest


