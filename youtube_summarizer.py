import os
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 配置 API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 配置 Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials_dict = eval(os.environ.get("GOOGLE_CREDENTIALS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict, scope
)
client = gspread.authorize(creds)
sheet = client.open("Your_Sheet_Name").sheet1  # 替换为你的 Google Sheets 表格名称


def get_latest_video():
  # Low Level 频道的 RSS 地址
  rss_url = (
      "https://www.youtube.com/feeds/videos.xml?channel_id=UC6biysICWOJ-C3P4Tyeggzg"
  )
  feed = feedparser.parse(rss_url)
  if not feed.entries:
    return None
  latest = feed.entries[0]
  return {
      "id": latest.get("yt_videoid"),
      "title": latest.title,
      "link": latest.link,
      "published": latest.published,
  }


def summarize_transcript(video_id):
  try:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([item["text"] for item in transcript_list])

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = (
        "你是一个资深漏洞研究员。请阅读以下YouTube视频的字幕，并用中文提炼出：\n"
        "1. 核心主题与背景\n"
        "2. 关键技术点、工具或逆向细节\n"
        "3. 实操结论与核心价值\n\n"
        f"字幕内容：\n{text[:15000]}"
    )
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    return f"获取或分析字幕失败: {str(e)}"


if __name__ == "__main__":
  video = get_latest_video()
  if video:
    # 利用 Google Sheets 已有记录进行去重，免去本地维护 JSON 文件的麻烦
    existing_records = sheet.get_all_records()
    processed_ids = [str(r.get("Video ID", "")) for r in existing_records]

    if video["id"] not in processed_ids:
      print(f"发现新视频: {video['title']}")
      summary = summarize_transcript(video["id"])
      sheet.append_row(
          [video["published"], video["title"], summary, video["link"], video["id"]]
      )
      print("已成功写入 Google Sheets！")
    else:
      print("没有新视频需要处理。")
