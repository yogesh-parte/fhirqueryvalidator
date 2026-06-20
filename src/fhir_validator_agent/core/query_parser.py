import urllib.parse
from typing import Dict, List, Optional, Tuple


def parse_fhir_query(query_url: str) -> Tuple[Optional[str], Dict[str, List[str]]]:
    parsed = urllib.parse.urlparse(query_url)
    resource_type = None
    path_splits = parsed.path.strip("/").split("/")
    if path_splits:
        resource_type = path_splits[-1]
    return resource_type, urllib.parse.parse_qs(parsed.query)