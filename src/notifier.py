import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    def __init__(self, config):
        self.config = config
        # 環境変数からGmail設定を取得
        self.gmail_user = os.environ.get('GMAIL_USER')
        self.gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if not self.gmail_user or not self.gmail_password:
            print("Warning: GMAIL_USER or GMAIL_APP_PASSWORD environment variable is not set.")

    def send_daily_summary(self, articles):
        """収集した記事リストをメールで送信する"""
        if not articles:
            print("No articles to send.")
            return

        if not self.gmail_user or not self.gmail_password:
            print("Skipping email send (No Credentials). Printing content instead.")
            print(self._generate_email_body(articles))
            return

        # メールの作成
        msg = MIMEMultipart("alternative")
        msg['Subject'] = f"{self.config['email']['subject_prefix']} Daily Summary - {len(articles)} articles"
        msg['From'] = self.gmail_user
        
        # 宛先がリストならカンマ区切りにする、文字列ならそのまま
        to_emails = self.config['email']['to_email']
        if isinstance(to_emails, list):
            msg['To'] = ", ".join(to_emails)
        else:
            msg['To'] = to_emails

        # 本文の作成（テキスト版とHTML版）
        text_body = self._generate_email_body(articles)
        html_body = self._generate_html_body(articles)

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            # GmailのSMTPサーバーに接続
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            print(f"Email sent successfully to {self.config['email']['to_email']}!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def _generate_email_body(self, articles):
        """テキスト形式のメール本文（デバッグ用）"""
        lines = ["Here is your daily tech news summary:\n"]
        for article in articles:
            lines.append(f"- {article['title']}")
            lines.append(f"  {article['url']}")
            lines.append("")
        return "\n".join(lines)

    def _generate_html_body(self, articles):
        """HTML形式のメール本文"""
        html = "<h2>Daily Tech News Summary</h2><ul>"
        for article in articles:
            html += f"<li>"
            html += f"<strong><a href='{article['url']}'>{article['title']}</a></strong>"
            html += f"<br/><small>Source: {article['source']} | Keyword: {article.get('matched_keyword', 'N/A')}</small>"
            if article.get('summary'):
                # 改行を<br>に変換して表示（文字数制限なし）
                summary_html = article['summary'].replace('\n', '<br/>')
                html += f"<p>{summary_html}</p>"
            html += "</li>"
        html += "</ul>"
        return html
