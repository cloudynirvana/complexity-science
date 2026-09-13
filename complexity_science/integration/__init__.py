"""Future Confluence seam — contracts only, no hard dependency."""

from complexity_science.integration.confluence_adapter import (
    SCHEMA_ID,
    ConfluenceRequest,
    ConfluenceResponse,
    from_pipeline_result,
    parse_request,
    to_confluence_payload,
)

__all__ = [
    "SCHEMA_ID",
    "ConfluenceRequest",
    "ConfluenceResponse",
    "from_pipeline_result",
    "parse_request",
    "to_confluence_payload",
]
