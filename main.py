import os
import feedparser
from google import genai
import gspread


def main():
  print("正在初始化 Gemini 客户端...")
  api_key = os.environ.get("GOOGLE_API_KEY")
  if not api_key:
    raise ValueError(
        "未找到 GOOGLE_API_KEY 环境变量，请检查 GitHub Secrets 配置！"
    )

  # 使用官方最新的 google-genai 客户端
  client = genai.Client(api_key=api_key)

  print("正在连接 Google Sheets...")
  gc = gspread.service_account(filename="credentials.json")
  sh = gc.open("My IT Daily News")
  worksheet = sh.sheet1

  print("正在抓取 Hacker News...")
  feed = feedparser.parse("https://news.ycombinator.com/rss")
  articles = []
  for entry in feed.entries[:5]:
    articles.append({"title": entry.title, "link": entry.link})

  print("正在呼叫 Gemini AI 进行总结与分类...")
  prompt = f"""
    以下是今天 Hacker News 上的热门文章列表：
    {articles}
    
    请帮我逐条进行以下处理：
    1. 将英文标题翻译并精炼为通顺的中文总结（一句话）。
    2. 打一个技术标签（如：后端、AI、前端、安全、开源、系统）。
    
    请按清晰的文本格式返回结果。
    """

  # 调用新版 SDK 生成内容
  response = client.models.generate_content(
      model="gemini-1.5-flash", contents=prompt
  )
  ai_result = response.text

  print("正在写入 Google Sheets...")
  worksheet.append_row(
      ["2026-10-26", ai_result, "Gemini 自动总结", "https://news.ycombinator.com/"]
  )
  print("全部流程执行完成！")


if __name__ == "__main__":
  main()
