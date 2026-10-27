import feedparser
import gspread
from youtube_transcript_api import YouTubeTranscriptApi
# 伪代码逻辑示例：
# 1. 解析 RSS 获取最新视频
rss_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC6biysICWOJ-C3P4Tyeggzg"
feed = feedparser.parse(rss_url)
latest_entry = feed.entries[0]
video_id = latest_entry.yt_videoid

# 2. 检查是否已处理过
if not is_already_processed(video_id):
  # 3. 获取字幕
  transcript = YouTubeTranscriptApi.get_transcript(video_id)
  text_content = " ".join([item["text"] for item in transcript])

  # 4. 调用 Gemini API 生成摘要
  summary = call_gemini_api(text_content)

  # 5. 写入 Google Sheets 或 Obsidian
  append_to_google_sheets(
      latest_entry.title, summary, latest_entry.link, latest_entry.published
  )
  mark_as_processed(video_id)
