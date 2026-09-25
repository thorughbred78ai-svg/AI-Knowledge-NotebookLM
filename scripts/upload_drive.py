import hashlib
import mimetypes
import os
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

TOKEN_FILE = os.environ.get(
    "GOOGLE_TOKEN_FILE",
    "token.json"
)

FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

if not FOLDER_ID:
    raise RuntimeError(
        "Environment variable DRIVE_FOLDER_ID is not set."
    )


def get_credentials():
    token_json = os.environ.get("GOOGLE_TOKEN_JSON")

    if token_json:
        creds = Credentials.from_authorized_user_info(
            json.loads(token_json),
            SCOPES
        )
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )
    else:
        raise RuntimeError(
            "Google credentials not found."
        )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds.valid:
        raise RuntimeError(
            "Google credentials are invalid or expired."
        )

    return creds


def get_drive_service():
    """建立 Google Drive API service。"""

    creds = get_credentials()

    return build(
        "drive",
        "v3",
        credentials=creds
    )


def escape_drive_query_value(value):
    """處理 Google Drive query 中的單引號。"""

    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_file(service, filename):
    """尋找指定資料夾中的同名檔案。"""

    safe_filename = escape_drive_query_value(filename)

    query = (
        f"name = '{safe_filename}' "
        f"and '{FOLDER_ID}' in parents "
        "and trashed = false"
    )

    result = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields=(
                "files("
                "id,"
                "name,"
                "mimeType,"
                "md5Checksum,"
                "modifiedTime"
                ")"
            ),
            pageSize=10,
        )
        .execute()
    )

    files = result.get("files", [])

    return files[0] if files else None


def calculate_md5(path):
    """計算本機檔案 MD5。"""

    md5 = hashlib.md5()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            md5.update(chunk)

    return md5.hexdigest()


def get_mime_type(path):
    """取得檔案 MIME type。"""

    mime_type, _ = mimetypes.guess_type(
        path.name
    )

    return mime_type or "application/octet-stream"


def create_file(service, path):
    """建立新的 Google Drive 檔案。"""

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

    print(f"Creating: {path.name}")

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
    """更新 Google Drive 中既有檔案。"""

    mime_type = get_mime_type(path)

    media = MediaFileUpload(
        str(path),
        mimetype=mime_type,
        resumable=True
    )

    print(f"Updating: {path.name}")

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
    """
    同步單一檔案。

    Drive 沒有：
        → Create

    Drive 有且內容相同：
        → Skip

    Drive 有但內容不同：
        → Update
    """

    path = Path(local_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {local_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Not a file: {local_path}"
        )

    print()
    print(f"Checking: {path}")

    local_md5 = calculate_md5(path)

    existing = find_file(
        service,
        path.name
    )

    # --------------------------------------------------------
    # Google Drive 沒有同名檔案
    # --------------------------------------------------------

    if not existing:
        create_file(
            service,
            path
        )
        return "created"

    # --------------------------------------------------------
    # Google Drive 有同名檔案
    # --------------------------------------------------------

    remote_md5 = existing.get(
        "md5Checksum"
    )

    # --------------------------------------------------------
    # 內容相同
    # --------------------------------------------------------

    if remote_md5 and remote_md5 == local_md5:
        print(
            f"Skipping: {path.name} "
            "(unchanged)"
        )

        print(
            f"Drive ID: {existing['id']}"
        )

        return "skipped"

    # --------------------------------------------------------
    # 內容不同
    # --------------------------------------------------------

    update_file(
        service,
        path,
        existing
    )

    return "updated"


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:"
        )
        print(
            "  python upload_drive.py "
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

            print()
            print(
                f"ERROR: {filename}"
            )
            print(
                f"  {error}"
            )

    print()
    print("==============================")
    print("Sync completed")
    print("==============================")
    print(f"Created : {created}")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")
    print(f"Failed  : {failed}")


if __name__ == "__main__":
    main()
