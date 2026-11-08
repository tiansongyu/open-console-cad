"""Correct original vent count, tactile marks and standard connector contacts."""
from cadlib.fidelity_seriesx import refine_seriesx


def build(model):
    return refine_seriesx(model)
