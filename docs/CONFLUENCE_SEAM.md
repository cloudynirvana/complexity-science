# Confluence seam

Later integration with Project Confluence should go through the JSON
contract in `complexity_science/integration/confluence_adapter.py`.

Rules:

- **Inputs and outputs only.** No import of Confluence packages.
- **No UI copy.** This project’s identity is attractors, multi-scale
  dynamics, and constrained pathway search — not a connectome / flybody /
  dark-lab shell.
- **Version the schema** (`complexity_science.confluence.v1`). Breaking
  changes increment the version; do not silently reuse field names.
- **Honesty fields travel with every payload** (`disclaimer`, `non_claims`).

See `ConfluenceRequest` and `ConfluenceResponse` in the adapter module.
A round-trip helper `to_confluence_payload` / `from_pipeline_result` is
provided so a future HTTP or CLI bridge can stay thin.
