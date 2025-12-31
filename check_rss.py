import feedparser

# 確認したいRSSのURL
url = "https://www.technologyreview.com/feed/"

print(f"Fetching RSS from: {url}...\n")
feed = feedparser.parse(url)

print(f"Title: {feed.feed.get('title', 'No Title')}")
print(f"Entries: {len(feed.entries)}\n")

print("-" * 50)
for i, entry in enumerate(feed.entries, 1):
    print(f"[{i}] {entry.title}")
    # print(f"    Link: {entry.link}") # URLも見たい場合はコメントアウトを外す
    print(f"    Summary: {entry.summary[:100]}...") # 要約も見たい場合はコメントアウトを外す
print("-" * 50)
