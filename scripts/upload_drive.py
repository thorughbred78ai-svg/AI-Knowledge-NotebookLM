import hashlib
import mimetypes
import os
import sys
from pathlib import Path

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
"https://www.googleapis.com/auth/drive"
]

FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

if not FOLDER_ID:
raise RuntimeError(
"DRIVE_FOLDER_ID is not set."
)

def get_drive_service():
"""
使用 Application Default Credentials。

GitHub Actions:
    GitHub OIDC
        ↓
    Workload Identity Federation
        ↓
    Google Service Account
        ↓
    ADC
"""

credentials, project = google.auth.default(
    scopes=SCOPES
)

return build(
    "drive",
    "v3",
    credentials=credentials
)


def escape_drive_query_value(value):
return (
value
.replace("\", "\\")
.replace("'", "\'")
)

def find_file(service, filename):
safe_filename = escape_drive_query_value(
filename
)

query = (
    f"name = '{safe_filename}' "
    f"and '{FOLDER_ID}' in parents "
    "and trashed = false"
)

response = (
    service.files()
    .list(
        q=query,
        spaces="drive",
        pageSize=10,
        fields=(
            "files("
            "id,"
            "name,"
            "mimeType,"
            "md5Checksum,"
            "modifiedTime,"
            "webViewLink"
            ")"
        )
    )
    .execute()
)

files = response.get("files", [])

return files[0] if files else None


def calculate_md5(path):
md5 = hashlib.md5()

with path.open("rb") as file:
    for chunk in iter(
        lambda: file.read(1024 * 1024),
        b""
    ):
        md5.update(chunk)

return md5.hexdigest()


def get_mime_type(path):
mime_type, _ = mimetypes.guess_type(
path.name
)

return mime_type or "application/octet-stream"


def create_file(service, path):
mime_type = get_mime_type(path)

media = MediaFileUpload(
    str(path),
    mimetype=mime_type,
    resumable=True
)

metadata = {
    "name": path.name,
    "parents": [FOLDER_ID]
}

print(f"Creating: {path}")

result = (
    service.files()
    .create(
        body=metadata,
        media_body=media,
        fields=(
            "id,"
            "name,"
            "modifiedTime,"
            "webViewLink"
        )
    )
    .execute()
)

print(
    f"Created: {result['name']} "
    f"({result['id']})"
)

if result.get("webViewLink"):
    print(
        f"Drive: {result['webViewLink']}"
    )

return result


def update_file(service, path, existing):
mime_type = get_mime_type(path)

media = MediaFileUpload(
    str(path),
    mimetype=mime_type,
    resumable=True
)

print(f"Updating: {path}")

result = (
    service.files()
    .update(
        fileId=existing["id"],
        media_body=media,
        fields=(
            "id,"
            "name,"
            "modifiedTime,"
            "md5Checksum,"
            "webViewLink"
        )
    )
    .execute()
)

print(
    f"Updated: {result['name']} "
    f"({result['id']})"
)

if result.get("webViewLink"):
    print(
        f"Drive: {result['webViewLink']}"
    )

return result


def sync_file(service, local_path):
path = Path(local_path)

if not path.exists():
    raise FileNotFoundError(
        f"File not found: {path}"
    )

if not path.is_file():
    raise ValueError(
        f"Not a file: {path}"
    )

print()
print(f"Checking: {path}")

local_md5 = calculate_md5(path)

existing = find_file(
    service,
    path.name
)

if not existing:
    create_file(
        service,
        path
    )
    return "created"

remote_md5 = existing.get(
    "md5Checksum"
)

if remote_md5 == local_md5:
    print(
        f"Skipping: {path.name} "
        "(unchanged)"
    )
    return "skipped"

update_file(
    service,
    path,
    existing
)

return "updated"


def main():
if len(sys.argv) < 2:
print(
"Usage: "
"python scripts/upload_drive.py "
"<file1> [file2 ...]"
)
sys.exit(1)

print("==============================")
print("Google Drive File Sync")
print("==============================")

service = get_drive_service()

created = 0
updated = 0
skipped = 0
failed = 0

for filename in sys.argv[1:]:
    try:
        result = sync_file(
            service,
            filename
        )

        if result == "created":
            created += 1

        elif result == "updated":
            updated += 1

        elif result == "skipped":
            skipped += 1

    except Exception as error:
        failed += 1

        print(
            f"ERROR: {filename}"
        )
        print(error)

print()
print("==============================")
print("Sync completed")
print("==============================")
print(f"Created : {created}")
print(f"Updated : {updated}")
print(f"Skipped : {skipped}")
print(f"Failed  : {failed}")

if failed:
    sys.exit(1)


if name == "main":
main()
