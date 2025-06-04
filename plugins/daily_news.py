from apscheduler.triggers.interval import IntervalTrigger
from config import API_KEY, NEWS_CHANNEL
import requests

def start_scheduler(app):
    app.scheduler.add_job(send_daily_news, IntervalTrigger(minutes=1), args=[app])

async def send_daily_news(app):
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("status") != "ok":
            return

        articles = data.get("articles", [])[:5]
        if not articles:
            return

        text = "📰 <b>Top News Headlines:</b>\n\n"
        for article in articles:
            title = article.get("title")
            url = article.get("url")
            if title and url:
                text += f"• <a href='{url}'>{title}</a>\n\n"

        await app.send_message(chat_id=NEWS_CHANNEL, text=text, disable_web_page_preview=True)

    except Exception as e:
        print(f"Error sending news: {e}")
