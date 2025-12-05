# forwarder.py

import os
import tempfile
import platform
from telethon import errors
from telethon.tl.types import DocumentAttributeFilename

from config import client, TARGET, resolve_target
from db import was_forwarded, mark_forwarded

# ---------------------------------------------------------
# MIME DETECTION: python-magic for Linux, fallback for Windows
# ---------------------------------------------------------
USE_MAGIC = False
if platform.system().lower() != "windows":
    try:
        import magic
        USE_MAGIC = True
        print("Using python-magic for MIME detection")
    except Exception:
        print("python-magic not found → using Telethon MIME fallback")
else:
    print("Windows detected → skipping python-magic")


def detect_mime(path, msg):
    """
    MIME detection logic that works on both Linux & Windows.
    """
    # Linux: use python-magic
    if USE_MAGIC:
        try:
            return magic.from_file(path, mime=True)
        except:
            pass

    # Windows or fallback
    if msg.file and msg.file.mime_type:
        return msg.file.mime_type

    return "application/octet-stream"


# ---------------------------------------------------------
# UPLOAD MEDIA (reupload bypass protected files)
# ---------------------------------------------------------
async def upload_media(msg):
    target = await resolve_target(client, TARGET)

    caption = msg.text or ""

    # Extract filename attribute properly
    filename = None
    for attr in getattr(msg.file, "attributes", []):
        if isinstance(attr, DocumentAttributeFilename):
            filename = attr.file_name

    if not filename:
        ext = msg.file.ext or ""
        filename = f"file_{msg.id}{ext}"

    # Download media to a temp file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        path = temp.name

    await client.download_media(msg, file=path)

    # Detect MIME type
    mime_type = detect_mime(path, msg)

    # Preserve Telethon attributes (width, height, duration, etc.)
    attrs = getattr(msg.media.document, "attributes", None)

    try:
        await client.send_file(
            target,
            path,
            caption=caption,
            attributes=attrs,
            mime_type=mime_type,
            file_name=filename
        )
    except errors.FloodWaitError as e:
        print(f"FloodWait {e.seconds}s → retrying...")
        await asyncio.sleep(e.seconds)
        await client.send_file(
            target,
            path,
            caption=caption,
            attributes=attrs,
            mime_type=mime_type,
            file_name=filename
        )

    os.remove(path)


# ---------------------------------------------------------
# FORWARD MAIN ENTRY
# ---------------------------------------------------------
async def forward_message(msg):
    """
    Main forward entry point. Handles:
    - duplicate check
    - text forwarding
    - media forwarding (protected bypass)
    """
    target = await resolve_target(client, TARGET)

    if was_forwarded(msg.chat_id, msg.id):
        return False

    if msg.media:
        await upload_media(msg)
    else:
        await client.send_message(target, msg.text or "")

    mark_forwarded(msg.chat_id, msg.id)
    return True
