# Sitemap Automatic Generation Tool

ウェブサイトを再帰的に巡回し、全ページのリスト（URL、タイトル、ステータス）を抽出するツールです。

## 特徴
- **再帰的クローリング:** 内部リンクを自動で辿り、全ページを抽出します。
- **クエリパラメータの集約 (デフォルト):** 同一パスでパラメータのみが異なるURLを重複としてフィルタリングします（ページング等の重複回避）。
- **負荷対策:** リクエスト間の待機時間を設け（デフォルト1〜3秒）、シングルスレッドで動作します。
- **ドメイン制御:** 同一ドメインおよび許可されたサブドメインのみを巡回します。
- **レポート出力:** CSVおよびExcel形式での出力に対応しています。
- **巡回方式の選択:** DFS（深さ優先・デフォルト）または BFS（幅優先）を `--traversal` で指定可能です。
- **Cookie 認証:** Netscape 形式の `cookies.txt`（[Get cookies.txt LOCALLY](https://github.com/kairi003/Get-cookies.txt-LOCALLY) 等）を `--cookies` で読み込み、要ログインページに対応します。

## 動作要件
- Python 3.9+
- [uv](https://astral.sh/uv/)

## インストールと実行

```bash
# 依存関係のインストール
uv sync

# 実行
uv run main.py [開始URL] [オプション]
```

### オプション
- `--subdomains sub1.example.com sub2.example.com`: 許可するサブドメインの指定
- `--output filename`: 出力ファイル名の指定（デフォルト: ドメイン名）
- `--excel`: Excel形式でも出力する
- `--max-depth N`: 最大巡回深度の指定
- `--delay-min N`, `--delay-max N`: リクエスト間の最小/最大待機時間（秒）
- `--include-params`: クエリパラメータが異なるURLもすべて含める（デフォルトはフィルタされる）
- `--traversal dfs|bfs`: 巡回方式の指定（デフォルト: `dfs`）。`bfs` は開始URLからの最短リンク数に近い深度で巡回します
- `--cookies FILE`: Netscape 形式の Cookie ファイル（Get cookies.txt LOCALLY のエクスポート等）

### Cookie ファイルの取り扱い

`cookies.txt` はログインセッションを含むため、リポジトリには含めません。`.gitignore` で除外済みです。プロジェクトルートなど任意のパスに置き、`--cookies` でパスを指定してください。

```bash
# 例: ルートに cookies.txt を置く場合
uv run main.py https://example.com/mypage --cookies ./cookies.txt
```

## ライセンス
MIT