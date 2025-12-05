# forwarder.py
import os
import tempfile
from telethon import errors
from telethon.tl.types import DocumentAttributeFilename

from config import client, TARGET, resolve_target
from db import was_forwarded, mark_forwarded

async def upload_media(msg):
    TARGETID=await resolve_target(client,TARGET)
    caption = msg.text or ""

    filename = None
    for attr in getattr(msg.file, "attributes", []):
        if isinstance(attr, DocumentAttributeFilename):
            filename = attr.file_name

    if not filename:
        ext = msg.file.ext or ""
        filename = f"file_{msg.id}{ext}"

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        path = temp.name

    await client.download_media(msg, file=path)

    attrs = getattr(msg.media.document, "attributes", None)

    await client.send_file(
        TARGETID,
        path,
        caption=caption,
        attributes=attrs,
        mime_type=msg.file.mime_type,
        file_name=filename
    )

    os.remove(path)

async def forward_message(msg):
    TARGETID=await resolve_target(client,TARGET)
    """Main forward logic"""
    if was_forwarded(msg.chat_id, msg.id):
        return False

    if msg.media:
        await upload_media(msg)
    else:
        await client.send_message(TARGETID, msg.text or "")

    mark_forwarded(msg.chat_id, msg.id)
    return True
