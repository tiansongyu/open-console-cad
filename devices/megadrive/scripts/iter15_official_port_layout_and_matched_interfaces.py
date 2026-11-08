"""Fit the original external port layout and synchronize matching interfaces."""
from cadlib.fidelity_megadrive_interfaces import refine_megadrive_interfaces


def build(model):
    return refine_megadrive_interfaces(model)
