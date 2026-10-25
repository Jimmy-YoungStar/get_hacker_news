import os
import feedparser
import gspread
from openai import OpenAI

# 1. 初始化 AI 客户端 (以 OpenAI 为例，密钥从环境变量读取)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 2. 连接 Google Sheets (通过环境变量里的服务账号 JSON)
# 在 GitHub Actions 中，我们可以把 JSON 内容存入 Secrets
gc = gspread.service_account(filename="credentials.json")
sh = gc.open("My IT Daily News")  # 你的 Google Sheet 表格名称
worksheet = sh.sheet1


def fetch_hacker_news():
  print("正在抓取 Hacker News...")
  feed = feedparser.parse("https://news.ycombinator.com/rss")
  articles = []
  for entry in feed.entries[:5]:  # 为了省 Token，先取前 5 条
    articles.append({"title": entry.title, "link": entry.link})
  return articles


def summarize_with_ai(articles):
  print("正在呼叫 AI 进行总结与分类...")
  # 把文章打包成文本让 AI 处理
  prompt = f"""
    以下是今天 Hacker News 上的热门文章列表：
    {articles}
    
    请帮我逐条进行以下处理：
    1. 将英文标题翻译并精炼为通顺的中文总结（一句话）。
    2. 打一个技术标签（如：后端、AI、前端、安全、开源、系统）。
    
    请严格以 JSON 格式返回一个列表，包含字段：title (中文总结), category (标签), link (原链接)。
    不要包含其他多余废话。
    """

  response = client.chat.completions.create(
      model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
  )

  # 简化处理：实际代码中可以用 json.loads 解析 AI 返回的结果
  return response.choices[0].message.content


def save_to_sheets(ai_result):
  print("正在写入 Google Sheets...")
  # 假设我们把解析后的数据追加到表格末尾
  # worksheet.append_row([日期, 标题, 分类, 链接])
  # 实际操作时，把 AI 返回的数据逐行 append 进去
  worksheet.append_row(["2026-10-26", ai_result, "AI 综合", "https://..."])
  print("写入完成！")


if __name__ == "__main__":
  raw_data = fetch_hacker_news()
  processed_data = summarize_with_ai(raw_data)
  save_to_sheets(processed_data)
