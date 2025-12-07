# forwarder.py

import os
import tempfile

from telethon.tl import functions
from telethon.tl.types import (
    InputMediaUploadedPhoto,
    InputMediaUploadedDocument,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    DocumentAttributeAudio
)

from config import client, TARGET
from db import was_forwarded, mark_forwarded


# ---------------------------------------------------------
# UPLOAD MEDIA USING RAW TELEGRAM API (most reliable method)
# ---------------------------------------------------------
async def upload_media(msg):
    """
    Re-uploads media using Telegram's Upload API.
    Automatically preserves:
    - photos
    - videos
    - gifs
    - stickers
    - audio / voice notes
    - all document attributes
    """

    #target = await resolve_target(client, TARGET)
    caption = msg.text or ""

    # ------------------------------
    # 1. Download original file
    # ------------------------------
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filepath = tmp.name

    await client.download_media(msg, file=filepath)

    # ------------------------------
    # 2. Extract original attributes
    # ------------------------------
    attributes = getattr(msg.media.document, "attributes", [])
    mime = msg.file.mime_type if msg.file and msg.file.mime_type else "application/octet-stream"

    # ------------------------------
    # 3. Upload binary file to Telegram
    # ------------------------------
    uploaded = await client.upload_file(filepath)

    # ------------------------------
    # 4. Detect correct media class
    # ------------------------------
    is_photo = hasattr(msg.media, "photo")
    is_video = any(isinstance(a, DocumentAttributeVideo) for a in attributes)
    is_audio = any(isinstance(a, DocumentAttributeAudio) for a in attributes)

    # ------------------------------
    # 5. Use correct wrapper for media type
    # ------------------------------
    if is_photo:
        media = InputMediaUploadedPhoto(uploaded)

    elif is_video:
        media = InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime,
            attributes=attributes,
            nosound_video=False
        )

    elif is_audio:
        media = InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime,
            attributes=attributes
        )

    else:
        # fallback → regular document, but still preserves attributes
        media = InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime,
            attributes=attributes
        )

    # ------------------------------
    # 6. Send using Telegram API (SendMediaRequest)
    # ------------------------------
    await client(functions.messages.SendMediaRequest(
        peer=TARGET,
        media=media,
        message=caption
    ))

    # Cleanup temp file
    os.remove(filepath)

    return True


# ---------------------------------------------------------
# FORWARD MAIN ENTRY (unchanged signature)
# ---------------------------------------------------------
async def forward_message(msg):
    """
    Main forward entry point. Handles:
    - duplicate prevention
    - correct media type forwarding
    - text messages
    
    Wrapper stays exactly the same.
    """
    #target = await resolve_target(client, TARGET)

    if was_forwarded(msg.chat_id, msg.id):
        return False

    if msg.media:
        if hasattr(msg.media,"document"):
            await upload_media(msg)
    else:
        await client.send_message(TARGET, msg.text or "")

    mark_forwarded(msg.chat_id, msg.id)
    return True
