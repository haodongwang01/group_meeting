"""Public URL and mount path used by the static build and link checker."""
import os
from urllib.parse import urlsplit

SITE_URL = os.environ.get("SITE_URL", "https://haodongwang01.github.io/group_meeting").rstrip("/")
SITE_PATH = urlsplit(SITE_URL).path + "/"
