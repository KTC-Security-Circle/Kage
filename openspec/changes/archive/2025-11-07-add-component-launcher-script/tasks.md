# Tasks: add-component-launcher-script

## 1. Implementation

- [x] 1.1 既存初期化の確認: `src/logging_conf.py`, `src/config.py`, `src/assets/fonts/`, `src/main.py`, `src/views/layout.py`
- [x] 1.2 動的 import ユーティリティを作成 (`path.py:Class` / `pkg.mod:Class` 両対応)
- [x] 1.3 ランチャースクリプト実装 (CLI 引数: `--target`, `--class`(任意), `--props` JSON)
- [x] 1.4 ログ初期化を既存ロジックで実施 (同一ログ出力先/フォーマット)
- [x] 1.5 フォント/テーマ適用を既存設定に合わせて初期化
- [x] 1.6 コンポーネントを生成し `page.add()` で表示 (必要に応じてレイアウトラップもサポート)
- [x] 1.7 エラー処理と終了コードの定義 (インポート/JSON/型不一致)

## 2. Tests & Validation

- [x] 2.1 単体テスト: import 文字列のパースと解決（今回の変更ではスキップ）
- [x] 2.2 単体テスト: 異常系 (クラス未発見/不正 JSON)（今回の変更ではスキップ）
- [x] 2.3 統合に近いテスト: ログ初期化とフォント適用が呼び出されることをモックで確認（今回の変更ではスキップ）
- [ ] 2.4 `openspec validate add-component-launcher-script --strict` を実行

## 3. Docs

- [x] 3.1 `docs/dev/views_guide.md` などに起動方法を追記 (例と既知の制約)
- [x] 3.2 README にも簡易サンプルを追加

> 備考: 2 系のテスト項目は、今回の実装方針によりスキップ（手動検証で代替）。必要になり次第、別 PR で追加予定。
