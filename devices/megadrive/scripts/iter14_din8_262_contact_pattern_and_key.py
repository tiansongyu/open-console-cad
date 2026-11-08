"""Correct the original Model 1 AV socket and detached plug mating topology."""
from cadlib.fidelity_megadrive import refine_megadrive


def build(model):
    return refine_megadrive(model)
