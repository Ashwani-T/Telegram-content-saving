# forwarder.py

import os
import tempfile
from telethon import errors
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    DocumentAttributeAudio,
    DocumentAttributeSticker,
)

from config import client, TARGET, resolve_target
from db import was_forwarded, mark_forwarded


# ---------------------------------------------------------
# Extract proper filename + detect media attributes
# ---------------------------------------------------------
def extract_attributes(msg):
    filename = None
    is_video = False
    supports_streaming = False

    attrs = getattr(msg.media, "document", None)
    attributes = getattr(attrs, "attributes", []) if attrs else []

    for attr in attributes:
        if isinstance(attr, DocumentAttributeFilename):
            filename = attr.file_name

        elif isinstance(attr, DocumentAttributeVideo):
            is_video = True
            supports_streaming = True

        elif isinstance(attr, DocumentAttributeAudio):
            # audio files (mp3, voice, etc.)
            pass

        elif isinstance(attr, DocumentAttributeSticker):
            # stickers
            pass

    # If filename is still None → fallback
    if not filename:
        ext = msg.file.ext or ""
        filename = f"media_{msg.id}{ext}"

    return filename, attributes, is_video, supports_streaming


# ---------------------------------------------------------
# Upload any media with correct metadata
# ---------------------------------------------------------
async def upload_media(msg):
    TARGETID = await resolve_target(client, TARGET)

    caption = msg.text or ""

    # Extract filename and original attributes
    filename, attributes, is_video, supports_streaming = extract_attributes(msg)

    # Temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = tmp.name

    # Fast download
    await client.download_media(msg, file=temp_path)

    # Upload using preserved metadata
    await client.send_file(
        TARGETID,
        temp_path,
        caption=caption,
        file_name=filename,
        mime_type=msg.file.mime_type,
        attributes=attributes,
        supports_streaming=supports_streaming  # ensures video uploads properly
    )

    os.remove(temp_path)


# ---------------------------------------------------------
# Forward wrapper
# ---------------------------------------------------------
async def forward_message(msg):
    TARGETID = await resolve_target(client, TARGET)

    if was_forwarded(msg.chat_id, msg.id):
        return False

    try:
        if msg.media:
            await upload_media(msg)
        else:
            await client.send_message(TARGETID, msg.text or "")
    except Exception as e:
        print(f"[ERROR] Failed forwarding message {msg.id}: {e}")
        return False

    mark_forwarded(msg.chat_id, msg.id)
    return True
