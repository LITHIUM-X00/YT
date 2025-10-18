# YouTube Telegram Downloader Bot

A Telegram bot to download YouTube videos and audio in multiple qualities.

## Features
- Choose video quality (144p–2160p)
- Convert to MP3 (requires ffmpeg)
- Shows download & upload progress
- Works on Replit, Heroku, Railway, VPS, Termux

## Setup
1. Clone repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export API_ID=your_api_id
   export API_HASH=your_api_hash
   export BOT_TOKEN=your_bot_token
   export OWNER=your_telegram_id
   ```
4. Run bot:
   ```bash
   python main.py
   ```

## Deploy to Replit
- Add `API_ID`, `API_HASH`, `BOT_TOKEN`, `OWNER` in **Secrets**  
- Run with ▶ button

## Deploy to Heroku
```bash
heroku create yt-telegram-bot
git push heroku main
heroku config:set API_ID=xxx API_HASH=xxx BOT_TOKEN=xxx OWNER=xxx
heroku ps:scale worker=1
```

---

👨‍💻 Developer: LITHIUM_X00
