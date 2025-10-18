import os
import asyncio
import tempfile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

import config  # import env variables

app = Client(
    "yt_downloader_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

QUALITY_MAP = [
    ("144p", "144"),
    ("240p", "240"),
    ("360p", "360"),
    ("480p", "480"),
    ("720p", "720"),
    ("1080p", "1080"),
    ("1440p", "1440"),
    ("2160p", "2160"),
    ("🎧 mp3", "mp3"),
]

USER_STATE = {}

def human_filesize(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def make_progress_hook(chat_id, msg_id, stage):
    def hook(d):
        try:
            status = d.get("status")
            if status in ["downloading", "finished"]:
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                percent = int(downloaded * 100 / total) if total else 0
                text = f"{'Downloading' if stage=='download' else 'Uploading'}: {percent}%"
                asyncio.get_event_loop().create_task(
                    safe_edit(chat_id, msg_id, text)
                )
        except Exception as e:
            print("hook error:", e)
    return hook

async def safe_edit(chat_id, msg_id, text):
    try:
        await app.edit_message_text(chat_id, msg_id, text)
    except:
        pass

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "👋 Welcome!\n"
        "Send me a YouTube link to download audio/video.\n\n"
        "⚠ Use only for videos you have rights to.\n\n"
        "👨‍💻 Developer: LITHIUM_X00"
    )

@app.on_message(filters.text & ~filters.edited)
async def get_link(_, message):
    url = message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        msg = await message.reply_text("Fetching video info...")
        ydl_opts = {"quiet": True, "no_warnings": True}
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except:
            await msg.edit("❌ Invalid or restricted link.")
            return

        USER_STATE[message.from_user.id] = {"url": url, "info": info}
        title = info.get("title", "video")

        kb = [[InlineKeyboardButton(label, callback_data=f"ql|{code}")]
              for label, code in QUALITY_MAP]

        await msg.edit(
            f"🎬 **{title}**\n\nSelect format:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

@app.on_callback_query(filters.regex(r"^ql\|"))
async def quality_selected(_, cq):
    user_id = cq.from_user.id
    _, quality = cq.data.split("|", 1)
    state = USER_STATE.get(user_id)

    if not state:
        await cq.answer("Session expired. Send link again.", show_alert=True)
        return

    url = state["url"]
    info = state["info"]
    msg = await cq.message.reply_text("Preparing download...")

    tmpdir = tempfile.mkdtemp(prefix="ytbot_")
    safe_title = "".join(c for c in info.get("title","video") if c.isalnum() or c in " _-").strip()
    out_template = os.path.join(tmpdir, safe_title + ".%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [make_progress_hook(cq.message.chat.id, msg.id, "download")]
    }

    if quality == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": config.AUDIO_FORMAT,
                "preferredquality": "192",
            }]
        })
    else:
        ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best"

    async def download_upload():
        try:
            loop = asyncio.get_event_loop()
            def run_ydl():
                with YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=True)
            await loop.run_in_executor(None, run_ydl)

            file_path = None
            for f in os.listdir(tmpdir):
                if f.startswith(safe_title):
                    file_path = os.path.join(tmpdir, f)
                    break

            if not file_path:
                await msg.edit("❌ File not found after download.")
                return

            size = os.path.getsize(file_path)
            await msg.edit(f"✅ Downloaded ({human_filesize(size)}). Uploading...")

            async def progress(current, total):
                percent = int(current * 100 / total) if total else 0
                await safe_edit(cq.message.chat.id, msg.id, f"Uploading: {percent}%")

            if file_path.lower().endswith((".mp4", ".mkv", ".webm")):
                await app.send_video(cq.message.chat.id, file_path, caption=info.get("title",""), progress=progress)
            else:
                await app.send_document(cq.message.chat.id, file_path, caption=info.get("title",""), progress=progress)

            await msg.edit("✅ Upload complete!\n\n👨‍💻 Developer: LITHIUM_X00")
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    await cq.answer("Started download...")
    asyncio.create_task(download_upload())

if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run()
