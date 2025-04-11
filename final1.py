from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from summarizer import summarize_text
from news_fetcher import fetch_rss_news, CATEGORY_EMOJIS

import requests
import pytz
import time
app = Flask(__name__)

ACCESS_TOKEN = "d8d546d31cc3458f8bd0fad8ce65a88d29b5458f2a1b4c7883"
INSTANCE_ID = "7105217740"
ALLOWED_SENDERS = {"919346859416@c.us", "918660898927@c.us", "919346711049@c.us"}

user_sessions = {}
IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)
scheduler.start()
prev_msg = {}

def send_whatsapp_message(recipient, message):
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"chatId": recipient, "message": message}
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📤 Message sent:", response.status_code)
        print("📤 Response:", response.text)
    except Exception as e:
        print("❌ Error sending message:", e)

def schedule_news_delivery(user_id, time_strs):
    def send_news():
        user_data = user_sessions.get(user_id, {})
        categories = user_data.get("categories", [])
        if not categories:
            return
        articles = fetch_rss_news(categories)
        emoji_heading = " | ".join(f"{CATEGORY_EMOJIS[cat]} {cat.capitalize()}" for cat in categories)
        message = f"🗞️ *Today's News* ({emoji_heading})\n\n"
        for i, article in enumerate(articles[:5], 1):
            result = summarize_text(article['summary'])
            message += f"{i}. *{article['title']}*\n🔗 {article['link']}\n💬 {result['summary']}\n{result['sentiment']}\n\n"
        send_whatsapp_message(user_id, message.strip())

    for time_str in time_strs:
        try:
            hour, minute = map(int, time_str.split(":"))
            job_id = f"{user_id}_{time_str}"
            scheduler.add_job(send_news, CronTrigger(hour=hour, minute=minute), id=job_id, replace_existing=True)
        except ValueError:
            print("❌ Invalid time format:", time_str)

def send_news(user_id):
    categories = user_sessions.get(user_id, {}).get("categories", [])
    if not categories:
        return
    articles = fetch_rss_news(categories)
    emoji_heading = " | ".join(f"{CATEGORY_EMOJIS[cat]} {cat.capitalize()}" for cat in categories)
    news_msg = f"🗞️ *Today's News * ({emoji_heading})\n\n"
    for i, article in enumerate(articles[:10], 1):
        result = summarize_text(article["summary"])
        summary = result["summary"]
        sentiment = result["sentiment"]
        news_msg += f"{i}. *{article['title']}*\n🔗 {article['link']}\n💬 {summary}\n{sentiment}\n\n"
    send_whatsapp_message(user_id, news_msg.strip())

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Incoming:", data)

    try:
        sender = data.get("senderData", {}).get("chatId")
        message_info = data.get("messageData", {})
        chat_id = message_info.get("chatId")

        if chat_id not in prev_msg:
            prev_msg[chat_id] = ""

        message = message_info.get("textMessageData", {}).get("textMessage", "") or \
                  message_info.get("extendedTextMessageData", {}).get("text", "")
        message = message.strip()

        if message.lower() == "/menu":
            user_sessions[sender] = {"step": "category", "categories": [], "times": []}
            cat_msg = "\n".join([f"{i+1}. {emoji} {cat.capitalize()}" for i, (cat, emoji) in enumerate(CATEGORY_EMOJIS.items())])
            send_whatsapp_message(sender, 
                f"📂 *Choose your news categories (reply with numbers):*\n{cat_msg}\n\n📝 Example: 1,3,5")
            return "ok", 200

        if sender not in user_sessions or user_sessions[sender]["step"] is None:
            return "ok", 200

        session = user_sessions[sender]

        if session["step"] == "category":
            if message.lower() == "/done":
                if not session["categories"]:
                    send_whatsapp_message(sender, "⚠️ Please select at least one category first.")
                    return "ok", 200
                session["step"] = 'time_next'
                send_news(sender)
                send_whatsapp_message(sender, "📬 News sent! Want daily updates? Type /selecttime to schedule.")
                return "ok", 200
            else:
                try:
                    nums = [int(x) for x in message.replace(" ", "").split(",") if x.isdigit()]
                    selected = [list(CATEGORY_EMOJIS.keys())[i-1] for i in nums if 1 <= i <= len(CATEGORY_EMOJIS)]
                    session["categories"].extend(selected)
                    session["categories"] = list(set(session["categories"]))
                    if selected and message.lower() not in ["/menu", "/done", "/selecttime", "/exit"]:
                        prev_msg[chat_id] = "choose cat"
                        send_whatsapp_message(sender, "✅type /done when finished")
                except:
                    send_whatsapp_message(sender, "⚠️ Invalid input. Use numbers like: 1, 2, 3.")
            return "ok", 200

        if message.lower() == "/selecttime":
            session["step"] = "time"
            send_whatsapp_message(sender, "⏰ Please send preferred times in 24-hour format (HH:MM).\n📝 Example: 08:00, 20:00")
            return "ok", 200

        if session["step"] == "time":
            if not (":" in message and all(c.strip().isdigit() for c in message.replace(":", "").replace(",", ""))):
                return "ok", 200
            try:
                time_strs = [t.strip() for t in message.split(",")]
                for t in time_strs:
                    datetime.strptime(t, "%H:%M")
                session["times"] = time_strs
                session["step"] = None
                schedule_news_delivery(sender, time_strs)
                send_whatsapp_message(sender, "✅ Times saved! You'll get news daily.\nType /exit to pause or /menu to change categories.")
                session.pop("time_warning_sent", None)
            except Exception as e:
                if not session.get("time_warning_sent"):
                    send_whatsapp_message(sender, "⚠️ Invalid time format! Use HH:MM (e.g., 07:00, 20:00)")
                    session["time_warning_sent"] = True
            return "ok", 200

        if message.lower() == "/exit":
            session["step"] = None
            send_whatsapp_message(sender, "👋 Exiting news bot flow. You'll still receive scheduled updates.\nType /menu to restart.")
            return "ok", 200

        return "ok", 200

    except Exception as e:
        print("❌ Webhook error:", e)
        return "error", 500

if __name__ == "__main__":
    app.run(port=5000, debug=False)
