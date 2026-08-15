# Simple HTML Deployer

AIに作ってもらった完成済みHTMLを、1コマンドでGitHub Pagesへ公開するための小さなツールです。OpenAI APIやAPIキーは一切使いません。

## 流れ

1. AIに「単一の完全なHTMLファイルを作って」と依頼する
2. 返された内容を `article.html` などのUTF-8ファイルとして保存する
3. 次を実行する

```bash
python deploy.py article.html
```

ツールが `docs/index.html` にコピーし、生成ファイルだけをcommitして `origin/main` へPushします。

## 前提環境

- Python 3.10以上
- Git
- GitHubアカウントと対象リポジトリへのPush権限
- 初回のみGitHub Pagesの公開元を `main` / `/docs` に設定
- GitHubへの認証済み環境

OpenAI API、`.env`、PDF解析ライブラリは不要です。

## セットアップ

このファイル一式をGitHubリポジトリ直下に置きます。

```text
repository/
├── .git/
├── deploy.py
├── requirements.txt
├── .gitignore
└── docs/
```

仮想環境を作ってGitPythonを導入します。

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

GitHub CLIを使う場合は、初回に認証します。

```bash
gh auth login
```

またはSSHキー、Git Credential Manager、Personal Access Tokenなどで、通常の `git push` が成功する状態にしてください。

## 初回Git設定

新しいフォルダーから始める場合:

```bash
git init
git branch -M main
git remote add origin https://github.com/YOUR_NAME/YOUR_REPOSITORY.git
git config user.name "YOUR NAME"
git config user.email "you@example.com"
git add deploy.py requirements.txt README.md .gitignore
git commit -m "chore: initialize HTML deployer"
git push -u origin main
```

## GitHub Pages設定

GitHubで対象リポジトリを開き、以下を設定します。

1. **Settings**
2. **Pages**
3. **Source**: `Deploy from a branch`
4. **Branch**: `main`
5. **Folder**: `/docs`
6. **Save**

設定後、通常は次の形式で公開されます。

```text
https://YOUR_NAME.github.io/YOUR_REPOSITORY/
```

## 使い方

### トップページとして公開

```bash
python deploy.py path/to/generated.html
```

配置先は `docs/index.html` です。

### 別ページとして公開

```bash
python deploy.py path/to/generated.html --name article_20260815.html
```

公開パスは通常、次のようになります。

```text
https://YOUR_NAME.github.io/YOUR_REPOSITORY/article_20260815.html
```

### コピーだけして、まだPushしない

```bash
python deploy.py path/to/generated.html --no-push
```

### コミットメッセージを指定

```bash
python deploy.py path/to/generated.html --message "docs: publish translated report"
```

### リモート名やブランチが異なる場合

```bash
python deploy.py path/to/generated.html --remote upstream --branch pages
```

## AIへ渡す依頼文の例

```text
添付PDFを日本語に翻訳・要約し、単一の完全なHTMLファイルとして作成してください。
HTMLは <!doctype html> から始め、外部ビルド不要にしてください。
Tailwind CSSはCDN形式を使い、モバイルとPCに対応させてください。
冒頭に3行要約、続いて目次、詳細コンテンツを配置してください。
回答は説明やMarkdownコードフェンスを付けず、HTMLだけにしてください。
```

AIからMarkdownコードフェンス付きで返された場合は、` ```html ` と最後の ` ``` ` を除いて保存してください。

## 安全上の注意

- GitHub Pagesに置いた内容は公開情報として扱ってください。
- 個人情報、秘密情報、社内限定資料は公開しないでください。
- 翻訳・要約の内容を公開前に人が確認してください。
- HTML内の外部スクリプトやリンクが信頼できるものか確認してください。
- このツールは入力HTMLに `<html>` と `<body>` があるかを確認しますが、内容の安全性までは判定しません。
