from collector import NewsCollector
from notifier import EmailNotifier
from summarizer import NewsSummarizer
import json
import os
from dotenv import load_dotenv

# .envファイルがあれば読み込む
load_dotenv()

def main():
    # コレクターの初期化
    collector = NewsCollector()
    
    # ニュース収集実行
    print("ニュース収集を開始します...")
    articles = collector.collect_news()
    
    print(f"\n収集完了: {len(articles)} 件の記事が見つかりました。")

    # AI要約の実行
    if articles:
        print("\nAI要約を開始します...")
        summarizer = NewsSummarizer()
        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] Summarizing: {article['title']}...")
            ai_summary = summarizer.summarize(article['title'], article['summary'])
            article['summary'] = ai_summary # 要約を上書き

    # 結果を表示（デバッグ用）
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    Source: {article['source']}")
        print(f"    Keyword: {article.get('matched_keyword')}")
        print(f"    URL: {article['url']}")

    # メール送信
    print("\nメール送信処理を開始します...")
    notifier = EmailNotifier(collector.config)
    notifier.send_daily_summary(articles)

if __name__ == "__main__":
    main()
