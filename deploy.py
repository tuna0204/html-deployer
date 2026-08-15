#!/usr/bin/env python3
"""Copy an AI-created HTML file into docs/ and deploy it to GitHub Pages."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo


def args_parser() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="完成済みHTMLをGitHub Pagesへ簡単デプロイ")
    p.add_argument("html", type=Path, help="AIに作ってもらったHTMLファイル")
    p.add_argument("--name", default="index.html", help="公開ファイル名（既定: index.html）")
    p.add_argument("--remote", default="origin", help="Git remote名（既定: origin）")
    p.add_argument("--branch", default="main", help="Push先ブランチ（既定: main）")
    p.add_argument("--message", help="コミットメッセージ（省略時は日時を自動挿入）")
    p.add_argument("--no-push", action="store_true", help="docsへのコピーだけ行う")
    return p.parse_args()


def validate_html(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"HTMLが見つかりません: {path}")
    if path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("入力ファイルは.htmlまたは.htmにしてください。")
    text = path.read_text(encoding="utf-8-sig")
    if not re.search(r"<html(?:\s|>)", text, re.I) or not re.search(r"<body(?:\s|>)", text, re.I):
        raise ValueError("完全なHTMLではありません。<html>と<body>を含めてください。")
    return text


def safe_name(name: str) -> str:
    p = Path(name)
    if p.name != name or name in {"", ".", ".."}:
        raise ValueError("--nameにはディレクトリを含まないファイル名を指定してください。")
    if p.suffix.lower() != ".html":
        raise ValueError("--nameの拡張子は.htmlにしてください。")
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.html", name):
        raise ValueError("--nameには英数字、ピリオド、ハイフン、アンダースコアのみ使用できます。")
    return name


def repository() -> tuple[Repo, Path]:
    try:
        repo = Repo(Path.cwd(), search_parent_directories=True)
    except InvalidGitRepositoryError as e:
        raise RuntimeError("Gitリポジトリ内で実行してください。") from e
    if repo.bare or not repo.working_tree_dir:
        raise RuntimeError("通常のローカルGitリポジトリ内で実行してください。")
    return repo, Path(repo.working_tree_dir).resolve()


def deploy() -> int:
    args = args_parser()
    source = args.html.expanduser().resolve()
    html = validate_html(source)
    name = safe_name(args.name)
    repo, root = repository()

    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    target = docs / name
    target.write_text(html, encoding="utf-8")
    print(f"[OK] 配置: {target}")

    if args.no_push:
        print("[OK] --no-push指定のため、Git操作は省略しました。")
        return 0

    rel = target.relative_to(root).as_posix()
    repo.index.add([rel])
    if not repo.index.diff("HEAD"):
        print("[OK] 前回と同じ内容のため、commit/pushは不要です。")
        return 0

    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    message = args.message or f"docs: Deploy HTML at {now}"
    commit = repo.index.commit(message)

    if args.remote not in [r.name for r in repo.remotes]:
        raise RuntimeError(f"remote '{args.remote}' がありません。git remote -v を確認してください。")

    print(f"[Git] {commit.hexsha[:8]} を {args.remote}/{args.branch} へPush中...")
    result = repo.remote(args.remote).push(refspec=f"HEAD:{args.branch}")
    errors = [x.summary for x in result if x.flags & x.ERROR]
    if errors:
        raise RuntimeError("Push失敗: " + "; ".join(errors))
    print("[OK] デプロイ用Pushが完了しました。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(deploy())
    except KeyboardInterrupt:
        print("中断しました。", file=sys.stderr)
        sys.exit(130)
    except (OSError, ValueError, RuntimeError, GitCommandError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
