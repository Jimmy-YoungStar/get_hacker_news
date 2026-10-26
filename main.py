import os
import feedparser
import google.generativeai as genai
import gspread

# 必须加上这一句，把系统的环境变量取出来配给 SDK
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

gc = gspread.service_account(filename="credentials.json")
sh = gc.open("My IT Daily News")
worksheet = sh.sheet1


def fetch_hacker_news():
  print("正在抓取 Hacker News...")
  feed = feedparser.parse("https://news.ycombinator.com/rss")
  articles = []
  for entry in feed.entries[:5]:
    articles.append({"title": entry.title, "link": entry.link})
  return articles


def summarize_with_ai(articles):
  print("正在呼叫 Gemini AI 进行总结与分类...")
  prompt = f"""
    以下是今天 Hacker News 上的热门文章列表：
    {articles}
    
    请帮我逐条进行以下处理：
    1. 将英文标题翻译并精炼为通顺的中文总结（一句话）。
    2. 打一个技术标签（如：后端、AI、前端、安全、开源、系统）。
    
    请按清晰的文本格式返回结果，方便后续写入表格。
    """

  # 调用 Gemini 生成内容
  response = model.generate_content(prompt)
  return response.text


def save_to_sheets(ai_result):
  print("正在写入 Google Sheets...")
  worksheet.append_row(["2026-10-26", ai_result, "Gemini 自动总结", "https://..."])
  print("写入完成！")


if __name__ == "__main__":
  raw_data = fetch_hacker_news()
  processed_data = summarize_with_ai(raw_data)
  save_to_sheets(processed_data)
