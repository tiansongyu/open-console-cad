"""Correct the VCS card reader and matching blank cartridge interface."""
from cadlib.fidelity_atari2600 import refine_atari2600


def build(model):
    return refine_atari2600(model)
