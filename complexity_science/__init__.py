"""Complexity Science: NSTG-guided in-silico pathology dynamics.

Research software only. Not a medical device, not CDS, not dosing advice.
"""

from complexity_science.honesty import DISCLAIMER_SHORT, NON_CLAIMS
from complexity_science.pipeline import PipelineResult, run_pipeline
from complexity_science.version import __version__
__all__ = [
    "DISCLAIMER_SHORT",
    "NON_CLAIMS",
    "PipelineResult",
    "run_pipeline",
    "__version__",
]
