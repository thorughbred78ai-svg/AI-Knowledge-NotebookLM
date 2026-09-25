import os
import sys
from pathlib import Path

import google.auth
from google.auth.transport.requests import AuthorizedSession

PROJECT_NUMBER = os.environ.get(
"GOOGLE_CLOUD_PROJECT_NUMBER"
)

LOCATION = os.environ.get(
"GOOGLE_CLOUD_LOCATION",
"global"
)

NOTEBOOK_ID = os.environ.get(
"NOTEBOOK_ID"
)

if not PROJECT_NUMBER:
raise RuntimeError(
"GOOGLE_CLOUD_PROJECT_NUMBER is not set."
)

if not NOTEBOOK_ID:
raise RuntimeError(
"NOTEBOOK_ID is not set."
)

def get_session():
credentials, _ = google.auth.default(
scopes=[
"https://www.googleapis.com/auth/cloud-platform"
]
)

credentials.refresh(
    google.auth.transport.requests.Request()
)

return AuthorizedSession(
    credentials
)


def upload_file(session, path):
path = Path(path)

if not path.exists():
    raise FileNotFoundError(path)

endpoint = (
    f"https://{LOCATION}-discoveryengine.googleapis.com"
    f"/upload/v1alpha"
    f"/projects/{PROJECT_NUMBER}"
    f"/locations/{LOCATION}"
    f"/notebooks/{NOTEBOOK_ID}"
    f"/sources:uploadFile"
)

headers = {
    "X-Goog-Upload-File-Name": path.name,
    "X-Goog-Upload-Protocol": "raw",
    "Content-Type": "text/markdown",
}

print(
    f"Uploading to Gemini Notebook: {path}"
)

with path.open("rb") as file:
    response = session.post(
        endpoint,
        headers=headers,
        data=file,
        timeout=300
    )

if not response.ok:
    raise RuntimeError(
        "Notebook upload failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

result = response.json()

print(
    "Notebook source uploaded:"
)

print(result)

return result


def main():
if len(sys.argv) < 2:
print(
"Usage:"
)
print(
"python scripts/notebooklm.py "
"<file1> [file2 ...]"
)
sys.exit(1)

session = get_session()

for filename in sys.argv[1:]:
    upload_file(
        session,
        filename
    )


if name == "main":
main()
