# Tech News Collector

GCPを活用して、毎日技術ニュースを収集・蓄積し、メールで通知するシステム。

## 概要 (Draft)

### 1. 目的
毎日決まった時間に技術ニュースを自動で収集し、データベースに蓄積するとともに、要約などをメールで受け取る。

### 2. アーキテクチャ詳細

コストと開発のしやすさを重視した構成です。

```mermaid
graph TD
    Scheduler[Cloud Scheduler] -->|毎日 8:00 AM| Function[Cloud Functions (Python)]
    
    subgraph "Cloud Functions 処理"
        Function -->|1. 収集| RSS[RSS / Web APIs]
        Function -->|2. 要約| Gemini[Vertex AI (Gemini 1.5 Flash)]
        Function -->|3. 保存| DB[(Firestore)]
        Function -->|4. 送信| Mail[SendGrid / Gmail]
    end
    
    DB -->|重複チェック| Function
    Mail -->|HTMLメール| User((User))
```

#### 各コンポーネントの役割

1.  **Cloud Scheduler**
    *   **役割**: 定期実行のトリガー。
    *   **設定**: Cron形式で `0 8 * * *` (毎日朝8時) など。
    *   **ターゲット**: Cloud Functions の HTTP エンドポイントを叩く。

2.  **Cloud Functions (第2世代)**
    *   **役割**: メインの処理ロジック。
    *   **ランタイム**: Python 3.11
    *   **処理内容**:
        *   `feedparser` 等でRSS/APIから記事を取得。
        *   Firestore を確認し、すでに通知済みの記事はスキップ（重複排除）。
        *   Vertex AI (Gemini) に記事本文またはタイトルを投げ、3行要約を生成。
        *   Firestore に結果を保存。
        *   メール本文（HTML）を生成し送信。

3.  **Google Cloud Firestore**
    *   **役割**: データの蓄積、重複防止。
    *   **コレクション設計**: `articles` コレクション
        *   `id`: URLのハッシュ値など (重複防止用)
        *   `title`: 記事タイトル
        *   `url`: 記事URL
        *   `summary`: AIによる要約
        *   `published_at`: 記事公開日
        *   `created_at`: 収集日時
        *   `tags`: カテゴリタグ (AIで付与)

4.  **Vertex AI (Gemini 1.5 Flash)**
    *   **役割**: コンテンツの理解。
    *   **モデル**: `gemini-1.5-flash` (高速・安価で要約タスクに最適)
    *   **プロンプト例**: 「以下の技術記事のタイトルと冒頭文から、エンジニア向けに要約を3点の箇条書きで作成してください。」

5.  **メール配信 (SendGrid 推奨)**
    *   **役割**: ユーザーへの通知。
    *   **理由**: 確実に届く、HTMLメールが作りやすい、ログが見れる。
    *   **代替案**: Gmail SMTP (設定は楽だが、セキュリティ制限に引っかかることがある)。

### 3. 処理フロー
1. Cloud Scheduler が Cloud Functions をトリガー
2. 指定されたソースからニュースを取得
3. (オプション) LLM (Geminiなど) で要約・フィルタリング
4. データベースに保存 (重複チェック含む)
5. メール本文を作成し送信

## 検討事項
- ニュースソースはどこにするか？
- AIによる要約は必要か？
- メールの配信サービスは何を使うか？

## コスト試算 (個人開発レベル)

GCPの無料枠 (Free Tier) をうまく使えば、**ほぼ0円** で運用可能です。

| サービス | 想定使用量 | 無料枠 / コスト感 | 判定 |
| --- | --- | --- | --- |
| **Cloud Scheduler** | 月30回実行 | 月3ジョブまで無料 | **¥0** |
| **Cloud Functions** | 1日数分の処理 | 月200万回呼び出し、40万GB秒メモリなど | **¥0** |
| **Firestore** | 毎日数十件保存 | 1GB保存、1日2万書き込みまで無料 | **¥0** |
| **Vertex AI (Gemini)** | ニュース要約 | 入力/出力文字数による (Gemini 1.5 Flash等は非常に安価) | **数円〜数十円/月** (または無料枠) |
| **SendGrid** | 毎日1通送信 | 1日100通まで無料 | **¥0** |

※ 注意: 完全に無料を保証するものではなく、設定ミスや大量アクセスで課金される可能性はあります。予算アラートの設定を推奨します。
