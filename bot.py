import os
import re
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

# Sticker-pack names/keywords that should be blocked.
# Add more terms here if you discover a bad pack.
BLOCKED_WORDS = {
    "nsfw",
    "18+",
    "adult",
    "xxx",
    "porn",
    "sex",
    "nude",
    "naked",
}

# Sticker packs you explicitly trust.
# Put pack names here if they get falsely deleted.
ALLOWED_PACKS = set()


def looks_inappropriate(pack_name: str) -> bool:
    if not pack_name:
        return False

    name = pack_name.lower()

    if name in {x.lower() for x in ALLOWED_PACKS}:
        return False

    return any(word in name for word in BLOCKED_WORDS)


async def moderate_sticker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message

    if not message or not message.sticker:
        return

    sticker = message.sticker

    # Telegram exposes the sticker-set name when available.
    pack_name = sticker.set_name or ""

    if looks_inappropriate(pack_name):
        try:
            await message.delete()
        except Exception as e:
            print("Delete failed:", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sticker moderation is active."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.Sticker.ALL,
            moderate_sticker
        )
    )

    app.add_handler(
        MessageHandler(
            filters.COMMAND & filters.Regex(r"^/start$"),
            start
        )
    )

    print("Sticker moderation bot is running...")
    app.run_polling()


if name == "main":
    main()