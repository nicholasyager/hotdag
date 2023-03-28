from enum import StrEnum

from hotdag.renderer import renderers

OutputTypes = StrEnum("OutputTypes", list(renderers.keys()))
