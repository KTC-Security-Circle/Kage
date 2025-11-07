# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../", editable = true }
# ///
"""Flet コンポーネント単体起動用ランチャー。

最小要件:
- 動的 import: "path/to/mod.py:Attr" または "pkg.mod:Attr"
- CLI: --target (必須), --class (任意), --props JSON (任意), --wrap-layout (任意)
- 既存設定再利用: ログ設定、テーマ適用、フォント設定
- インターフェイス: 以下のいずれか
  - Attr が ft.Control/ft.UserControl のサブクラス: インスタンス化
  - Attr が create_control(page, **props) 互換の callable: 呼び出し結果を使用

戻り値や例外は CLI としての終了コードに反映する。
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:  # 型チェック用のみにインポート
    from types import ModuleType

    import flet as ft
# src を import 解決パスへ追加（ファイルパス指定時に必要）
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 直下 import はテスト負荷を上げるため避け、必要箇所で局所 import する


# --- Exit codes ----------------------------------------------------
class ExitCode:
    OK = 0
    INVALID_ARGS = 2
    IMPORT_FAILED = 3
    ATTR_NOT_FOUND = 4
    TYPE_MISMATCH = 5
    RUNTIME_ERROR = 6
    JSON_ERROR = 7


class InvalidTargetError(ValueError):
    """ターゲット指定が不正な場合の例外。"""

    def __init__(self, reason: str) -> None:
        super().__init__(f"無効なターゲット指定: {reason}")


class InvalidPropsError(ValueError):
    """--props の指定が不正な場合の例外。"""

    def __init__(self, reason: str) -> None:
        super().__init__(f"--props の指定が不正です: {reason}")


class ControlTypeError(TypeError):
    """Control 生成に関する型不一致。"""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Control 型エラー: {reason}")


@dataclass(frozen=True)
class TargetSpec:
    """解決済みターゲット情報。"""

    is_file: bool
    module: str | Path
    attr: str | None


def parse_target(target: str, explicit_class: str | None = None) -> TargetSpec:
    """ターゲット表現をパースして `TargetSpec` を返す。

    Args:
        target: "path/to/mod.py[:Attr]" または "pkg.mod[:Attr]" 形式の文字列。
        explicit_class: --class による明示指定 (省略可)。指定時は優先。

    Returns:
        TargetSpec: 解釈結果。

    Raises:
        ValueError: 入力が空など不正な場合。
    """
    if not target:
        msg = "target が空です"
        raise InvalidTargetError(msg)

    mod_part, _, attr_part = target.partition(":")
    attr = explicit_class or (attr_part or None)

    is_file = mod_part.endswith((".py", ".pyw"))
    if is_file:
        path = Path(mod_part)
        return TargetSpec(is_file=True, module=path, attr=attr)
    return TargetSpec(is_file=False, module=mod_part, attr=attr)


def _import_from_file(path: Path) -> ModuleType:
    spec = spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        msg = f"spec を取得できませんでした: {path}"
        raise ImportError(msg)
    module = module_from_spec(spec)
    # type: ignore[assignment]
    loader = spec.loader
    loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def resolve_target(spec: TargetSpec) -> tuple[ModuleType, str | None]:
    """モジュールを import して属性名を返す。

    Returns:
        (module, attr_name)

    Raises:
        ImportError: import に失敗した場合。
    """
    module: ModuleType = _import_from_file(Path(spec.module)) if spec.is_file else import_module(str(spec.module))
    return module, spec.attr


def parse_props(props_json: str | None) -> dict[str, Any]:
    """JSON 文字列から dict を生成する。空や None は {}。

    Raises:
        ValueError: JSON デコード失敗時。
    """
    if not props_json:
        return {}
    try:
        val = json.loads(props_json)
    except json.JSONDecodeError as exc:
        msg = f"JSON デコードに失敗しました: {exc}"
        raise InvalidPropsError(msg) from exc
    if not isinstance(val, dict):
        msg = "JSON オブジェクトを指定してください"
        raise InvalidPropsError(msg)
    return {str(k): v for k, v in val.items()}


def _is_control_subclass(obj: object) -> bool:
    try:
        import flet as ft

        return inspect.isclass(obj) and issubclass(obj, (ft.Control,))
    except Exception:
        return False


def _is_factory_callable(obj: object) -> bool:
    return callable(obj)


def build_control(target_obj: object, page: ft.Page, props: dict[str, Any]) -> ft.Control:
    """ターゲットオブジェクトから Flet Control を生成する。

    優先順位:
    1) target_obj が ft.Control のサブクラス: target_obj(**props)
    2) target_obj が callable: target_obj(page=page, **props)

    Raises:
        TypeError: インターフェイス不一致。
    """
    import flet as ft

    # クラス定義ならそのままインスタンス化
    if _is_control_subclass(target_obj):
        instance = target_obj(**props)  # type: ignore[misc]
        if not isinstance(instance, ft.Control):
            msg = "生成物が ft.Control ではありません"
            raise ControlTypeError(msg)
        return instance

    # ファクトリ関数なら page を渡して生成
    if _is_factory_callable(target_obj):
        instance = target_obj(page=page, **props)  # type: ignore[misc]
        if not isinstance(instance, ft.Control):
            msg = "ファクトリの戻り値が ft.Control ではありません"
            raise ControlTypeError(msg)
        return instance

    # いずれにも該当しない
    msg = "サポートされていないターゲットタイプです"
    raise ControlTypeError(msg)


def _apply_common_page_settings(page: ft.Page) -> None:
    """既存アプリの設定/フォント/テーマを最小限適用する。"""
    # 設定ファイルの読み込みとテーマ適用
    try:
        from settings.manager import apply_page_settings, get_config_manager

        get_config_manager()
        apply_page_settings(page)
    except Exception as exc:  # 失敗しても続行
        from loguru import logger

        logger.warning(f"設定適用に失敗しました (続行します): {exc}")

    # 既定フォントとテーマ (main.py に揃える)
    try:
        import flet as ft

        page.padding = 0
        page.fonts = {
            "default": "/fonts/BIZ_UDGothic/BIZUDGothic-Regular.ttf",
            "bold": "/fonts/BIZ_UDGothic/BIZUDGothic-Bold.ttf",
        }
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.GREY_700,
            page_transitions=ft.PageTransitionsTheme(
                windows=ft.PageTransitionTheme.NONE,
                linux=ft.PageTransitionTheme.NONE,
                macos=ft.PageTransitionTheme.NONE,
                ios=ft.PageTransitionTheme.NONE,
                android=ft.PageTransitionTheme.NONE,
            ),
            font_family="default",
        )
    except Exception as exc:
        from loguru import logger

        logger.warning(f"フォント/テーマ設定に失敗しました (続行します): {exc}")


def _wrap_with_layout_if_needed(page: ft.Page, control: ft.Control, *, wrap: bool) -> ft.Control | ft.View:
    if not wrap:
        return control
    try:
        from views.layout import get_layout

        return get_layout(page, control)
    except Exception as exc:
        from loguru import logger

        logger.warning(f"レイアウトのラップに失敗しました。素のコンポーネントを表示します: {exc}")
        return control


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="component-launcher", add_help=True)
    parser.add_argument("--target", required=True, help="'path/to/mod.py:Attr' または 'pkg.mod:Attr'")
    parser.add_argument("--class", dest="class_name", required=False, help="ターゲット属性名を明示指定")
    parser.add_argument("--props", required=False, help="コンストラクタ/ファクトリに渡す JSON")
    parser.add_argument("--wrap-layout", action="store_true", help="共通レイアウトでラップして表示")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """エントリポイント。

    Args:
        argv: コマンドライン引数リスト (テスト用に差し替え可能)

    Returns:
        終了コード (0 = 成功, その他 = 失敗理由)
    """
    args = _parse_args(argv)
    _init_logger()
    spec = _safe_parse_target(args.target, args.class_name)
    if spec is None:
        return ExitCode.INVALID_ARGS
    module, attr_name = _safe_import(spec)
    if module is None:
        return ExitCode.IMPORT_FAILED
    target_obj = _get_target_object(module, attr_name)
    if target_obj is None:
        return ExitCode.ATTR_NOT_FOUND
    props = _safe_parse_props(args.props)
    if props is None:
        return ExitCode.JSON_ERROR
    return _run_flet(target_obj, props, wrap_layout=args.wrap_layout)


# --- helpers (main を単純化) -----------------------------------------


def _init_logger() -> None:
    try:
        from logging_conf import setup_logger

        setup_logger()
    except Exception:
        # 最低限のスタンドアロンログ
        logger.warning("ロガー初期化に失敗しました (fallback)")


def _safe_parse_target(target: str, class_name: str | None) -> TargetSpec | None:
    try:
        return parse_target(target, class_name)
    except Exception as exc:
        logger.error(str(exc))
        return None


def _safe_import(spec: TargetSpec) -> tuple[ModuleType | None, str | None]:
    try:
        return resolve_target(spec)
    except Exception as exc:
        logger.exception(f"ターゲットの import に失敗しました: {spec.module}")
        logger.error(str(exc))
        return None, None


def _get_target_object(module: ModuleType, attr_name: str | None) -> object | None:
    if attr_name:
        if not hasattr(module, attr_name):
            logger.error(f"属性が見つかりません: {attr_name}")
            return None
        return getattr(module, attr_name)
    if hasattr(module, "create_control"):
        return module.create_control  # type: ignore[attr-defined]
    logger.error("属性が未指定で、create_control も見つかりません")
    return None


def _safe_parse_props(props_json: str | None) -> dict[str, Any] | None:
    try:
        return parse_props(props_json)
    except InvalidPropsError as exc:
        logger.error(str(exc))
        return None


def _run_flet(target_obj: object, props: dict[str, Any], *, wrap_layout: bool) -> int:
    def _flet_main(page: ft.Page) -> None:
        _apply_common_page_settings(page)
        control = build_control(target_obj, page, props)
        control_or_view = _wrap_with_layout_if_needed(page, control, wrap=wrap_layout)
        page.add(control_or_view)
        logger.info("コンポーネントを起動しました")

    try:
        import flet as ft

        ft.app(target=_flet_main, assets_dir=str(SRC_DIR / "assets"))
    except TypeError as exc:
        logger.error(f"インターフェイス不一致: {exc}")
        return ExitCode.TYPE_MISMATCH
    except Exception as exc:  # 実行時エラー
        logger.exception(f"起動中にエラー: {exc}")
        return ExitCode.RUNTIME_ERROR
    else:
        return ExitCode.OK


if __name__ == "__main__":
    sys.exit(main())
