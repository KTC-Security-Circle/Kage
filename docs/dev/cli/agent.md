# Agent コマンド

`agent` グループは OneLiner (一言コメント) を生成し、必要に応じてタスクとして保存するためのユーティリティです。

## 概要

| コマンド    | 説明                       | 主なオプション                              |
| ----------- | -------------------------- | ------------------------------------------- |
| `run`       | 一言コメント生成して表示   | `--provider`, `--model`, `-i/--interactive` |
| `save-task` | 生成した一言をタスクへ保存 | `--status`, `--provider`, `--model`, `-i`   |

## プロバイダー / モデル指定

`--provider`:

- `fake`: モック応答 (ネットワーク不要)
- `google`: Gemini API (環境変数 `GOOGLE_API_KEY` 必須)
- `openvino`: ローカル OpenVINO 実行 (HuggingFace モデルを事前ダウンロード)

`--model` の指定ルール:

- `openvino` の場合: Enum 名 (例: `QWEN_3_8B_INT4`) か Enum の値 (`OpenVINO/Qwen3-8B-int4-cw-ov`)
- `google` の場合: 任意の Gemini モデル文字列 (例: `gemini-1.5-flash-latest`)
- `fake` の場合: 指定不要 (無視される)
- `--model` のみ指定したとき: OpenVINO Enum 名/値に一致すれば `openvino` 推定、そうでなければ `google` として扱う

## デフォルト値 / 初期挙動

| 項目               | 既定値   | 説明                                                                                                               |
| ------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ |
| provider           | (未指定) | CLI で未指定の場合は設定 (config) に委譲。設定未定義なら内部の OneLinerService 実装が安全パス (FAKE など) を利用。 |
| model              | (未指定) | provider=google 時は設定側 one_liner モデル。provider=openvino で設定が無い場合は明示指定推奨。                    |
| status (save-task) | inbox    | 不正値は自動で INBOX フォールバック。                                                                              |
| interactive        | false    | `-i/--interactive` を付けた場合のみ対話フロー。                                                                    |
| task counts        | 自動集計 | 対話モードで「スキップ = 自動」「No = 手動入力」。                                                                 |

補足:

- `--model` のみ指定: OpenVINO Enum 名/値に一致 → provider=openvino。非一致 → provider=google。
- provider=fake 時は model を無視。
- `save-task` の title は生成テキスト先頭 60 文字を使用。
- 生成失敗時はフォールバック文言 (`今日も一日、お疲れさまです。`) を表示する実装方針。

## 例

```bash
# 最も簡単 (設定デフォルト)
poe cli agent run

# FAKE プロバイダーで生成
poe cli agent run --provider fake

# Google + モデル指定
poe cli agent run --provider google --model gemini-1.5-flash-latest

# モデルのみ指定 (google と推定)
poe cli agent run --model gemini-1.5-flash-exp

# OpenVINO (Enum 名指定)
poe cli agent run --provider openvino --model QWEN_3_8B_INT4

# OpenVINO (Enum 値指定)
poe cli agent run --provider openvino --model OpenVINO/Mistral-7B-Instruct-v0.3-int4-cw-ov

# 生成してタスク保存 (INBOX)
poe cli agent save-task

# ステータス指定で保存
poe cli agent save-task --status todo
```

## 対話モード (-i)

`-i/--interactive` を付与すると以下の順序でプロンプトが表示されます:

1. Provider 選択 (fake / google / openvino)
2. 選択したプロバイダーに応じたモデル選択 / 入力
3. その選択を適用するか確認 (No で設定デフォルト使用)
4. タスク件数を自動集計で取得するか確認
5. 手動入力を選んだ場合: today/completed/overdue の件数入力

```bash
poe cli agent run -i
```

## エラーとフォールバック

| 状態                    | 挙動                                           |
| ----------------------- | ---------------------------------------------- |
| OpenVINO で不正なモデル | CLI が `BadParameter` で警告                   |
| Google API KEY 未設定   | 例外ログ後、デフォルトメッセージ               |
| 生成失敗 (その他)       | デフォルト文言: `今日も一日、お疲れさまです。` |

## 返却表示

`run` 実行後は Rich Panel で一言と経過秒数が表示されます。`save-task` は追加で作成されたタスクタイトルを表示します。

### 出力メタ情報 (埋め込み形式)

Panel 本文の末尾に dim スタイルで以下のメタデータ行が埋め込まれます (例: `elapsed=0.42s | provider=fake | counts(t=0,c=3,o=1)`).

- `provider=<value>`: 実際に使用したプロバイダー (`fake` / `google` / `openvino`)
- `model=<name>`: 指定または設定から解決されたモデル (OpenVINO は Enum 名、Google は文字列、fake は表示なし)
- `counts(t=<today>,c=<completed>,o=<overdue>)`: コンテキストに渡されたタスク件数

表示例:

```text
こんにちは！私は Kage AI です。

[dim]elapsed=1.08s | provider=google | model=gemini-2.0-flash | counts(t=2,c=5,o=1)[/dim]
```

補足:

- FAKE かつ件数が自動集計された場合でも counts(...) は表示されます。
- モデル未指定 (FAKE など) では `model=...` 部分は省略されます。
- 長すぎる場合は端末の横幅に依存して折り返されることがあります。
- `elapsed=...s` は常に先頭に配置されます。

---

開発者向け詳細は `logic/services/one_liner_service.py` と `agents/task_agents/one_liner/` を参照してください。
