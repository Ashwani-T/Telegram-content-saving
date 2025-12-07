# forwarder.py (refactored)

import os
import tempfile

from telethon.tl import functions
from telethon.tl.types import (
    InputMediaUploadedPhoto,
    InputMediaUploadedDocument,
    DocumentAttributeVideo,
    DocumentAttributeAudio,
)

from config import client, TARGET
from db import was_forwarded, mark_forwarded


# ---------------------------------------------------------
# PHOTO UPLOADER (pure photos only)
# ---------------------------------------------------------
async def upload_photo(msg, caption, filepath):
    

    uploaded = await client.upload_file(filepath)

    media = InputMediaUploadedPhoto(uploaded)

    await client(
        functions.messages.SendMediaRequest(
            peer=TARGET,
            media=media,
            message=caption
        )
    )
    return True


# ---------------------------------------------------------
# DOCUMENT / VIDEO / AUDIO / GIF / STICKER UPLOADER
# ---------------------------------------------------------
async def upload_document(msg, caption, filepath):
    document = msg.media.document
    attributes = document.attributes
    mime = document.mime_type or "application/octet-stream"

    uploaded = await client.upload_file(filepath)

    is_video = any(isinstance(a, DocumentAttributeVideo) for a in attributes)
    is_audio = any(isinstance(a, DocumentAttributeAudio) for a in attributes)

    media = InputMediaUploadedDocument(
        file=uploaded,
        mime_type=mime,
        attributes=attributes,
        nosound_video=False if is_video else None
    )

    await client(
        functions.messages.SendMediaRequest(
            peer=TARGET,
            media=media,
            message=caption
        )
    )
    return True


# ---------------------------------------------------------
# MAIN MEDIA ROUTER
# ---------------------------------------------------------
async def upload_media(msg):
    """
    Routes photo → upload_photo
    Routes document/video/audio → upload_document
    """

    caption = msg.text or ""

    # 1. Download media
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filepath = tmp.name

    await client.download_media(msg, file=filepath)

    # 2. Detect photo vs document
    if hasattr(msg.media, "photo") and msg.media.photo:

        if not filepath.endswith((".jpg", ".jpeg", ".png")):
            new_path = filepath + ".jpg"
            os.rename(filepath, new_path)
            filepath = new_path
        
        result = await upload_photo(msg, caption, filepath)
        
    else:
        result = await upload_document(msg, caption, filepath)

    # cleanup
    os.remove(filepath)
    return result


# ---------------------------------------------------------
# FORWARD MAIN ENTRY
# ---------------------------------------------------------
async def forward_message(msg):
    if was_forwarded(msg.chat_id, msg.id):
        return False

    if msg.media:
        await upload_media(msg)
    else:
        await client.send_message(TARGET, msg.text or "")

    mark_forwarded(msg.chat_id, msg.id)
    return True
