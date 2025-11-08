# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../", editable = true }
# ///
"""Flet コンポーネント単体起動用ランチャー（簡潔版）。

ポリシー（本ランチャーの挙動）:
- ターゲットは "path/to/mod.py:Class" または "pkg.mod:Class" のみを受け付ける。
- Class は flet.ft.Control のサブクラスかつ `@classmethod def preview(cls, ...)` を必須とする。
- preview の内部でインスタンス生成に必要な引数を組み立てる前提とし、外部からの props 指定は不可。
- レイアウトでの簡易ラップはデフォルトで有効。`--no-wrap` または `-nw` 指定時のみ無効化。

戻り値や例外は CLI としての終了コードに反映する。
"""

from __future__ import annotations

import argparse
import inspect
import sys
from contextlib import suppress
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


class InvalidTargetError(ValueError):
    """ターゲット指定が不正な場合の例外。"""

    def __init__(self, reason: str) -> None:
        super().__init__(f"無効なターゲット指定: {reason}")


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


def parse_target(target: str) -> TargetSpec:
    """ターゲット表現をパースして `TargetSpec` を返す。

    Args:
        target: "path/to/mod.py[:Attr]" または "pkg.mod[:Attr]" 形式の文字列。

    Returns:
        TargetSpec: 解釈結果。

    Raises:
        ValueError: 入力が空など不正な場合。
    """
    if not target:
        msg = "target が空です"
        raise InvalidTargetError(msg)

    mod_part, _, attr_part = target.partition(":")
    attr = attr_part or None

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


def _is_control_subclass(obj: object) -> bool:
    try:
        import flet as ft

        return inspect.isclass(obj) and issubclass(obj, (ft.Control,))
    except Exception:
        return False


def build_control_from_preview(target_obj: object, page: ft.Page) -> ft.Control:
    """`ft.Control` サブクラスかつ `@classmethod preview` を持つクラスのみを受理して起動する。

    - 条件を満たさない場合は例外を送出する。
    - preview メソッドは `page` 引数を受け取る場合と受け取らない場合の両方を許容する。
    """
    import flet as ft

    if not _is_control_subclass(target_obj) or not inspect.isclass(target_obj):
        msg = "ターゲットは ft.Control のサブクラスである必要があります"
        raise ControlTypeError(msg)

    cls: type = target_obj  # type: ignore[assignment]

    # classmethod `preview` を強制
    try:
        static_attr = inspect.getattr_static(cls, "preview")
    except AttributeError as exc:
        msg = "preview classmethod が見つかりません"
        raise ControlTypeError(msg) from exc

    if not isinstance(static_attr, classmethod):
        msg = "preview は @classmethod で定義してください"
        raise ControlTypeError(msg)

    # バウンドメソッドを取得
    preview_fn = cls.preview
    if not callable(preview_fn):
        msg = "preview は呼び出し可能である必要があります"
        raise ControlTypeError(msg)

    # page を渡すかどうかをシグネチャで判定
    try:
        sig = inspect.signature(preview_fn)
        kwargs: dict[str, Any] = {"page": page} if "page" in sig.parameters else {}
        built = preview_fn(**kwargs)
    except TypeError as exc:
        msg = f"preview 呼び出しに失敗しました: {exc}"
        raise ControlTypeError(msg) from exc

    if not isinstance(built, ft.Control):
        msg = "preview の戻り値が ft.Control ではありません"
        raise ControlTypeError(msg)
    return built


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


def _wrap_with_layout_if_needed(control: ft.Control, *, wrap: bool) -> ft.Control:
    """シンプルなラッパーで Control を View 相当に包む。

    以前の `views.layout.get_layout` は廃止されたため、最小の View 風コンテナで包む。
    本格的な全体レイアウトを表示したい場合は、`views.layout:build_layout` を直接ターゲットに指定し、
    `--props '{"route":"/"}'` のように引数を渡してください。
    """
    if not wrap:
        return control
    try:
        import flet as ft

        return ft.View(route="/", controls=[ft.Container(content=control, expand=True, padding=16)])
    except Exception as exc:
        from loguru import logger

        logger.warning(f"簡易ラップに失敗しました。素のコンポーネントを表示します: {exc}")
        return control


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="component-launcher", add_help=True)
    parser.add_argument("--target", required=True, help="'path/to/mod.py:Class' または 'pkg.mod:Class'")
    parser.add_argument(
        "--no-wrap",
        "-nw",
        dest="no_wrap",
        action="store_true",
        help="簡易レイアウトでのラップを無効化",
    )
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
    spec = _safe_parse_target(args.target)
    if spec is None:
        return ExitCode.INVALID_ARGS
    module, attr_name = _safe_import(spec)
    if module is None:
        return ExitCode.IMPORT_FAILED
    target_obj = _get_target_object(module, attr_name)
    if target_obj is None:
        return ExitCode.ATTR_NOT_FOUND
    wrap_layout = not bool(getattr(args, "no_wrap", False))
    return _run_flet(target_obj, wrap_layout=wrap_layout)


# --- helpers (main を単純化) -----------------------------------------


def _init_logger() -> None:
    try:
        from logging_conf import setup_logger

        setup_logger()
    except Exception:
        # 最低限のスタンドアロンログ
        logger.warning("ロガー初期化に失敗しました (fallback)")


def _safe_parse_target(target: str) -> TargetSpec | None:
    try:
        return parse_target(target)
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
    if not attr_name:
        logger.error("Class を 'module:Class' 形式で指定してください")
        return None
    if not hasattr(module, attr_name):
        logger.error(f"属性が見つかりません: {attr_name}")
        return None
    return getattr(module, attr_name)


def _run_flet(target_obj: object, *, wrap_layout: bool) -> int:
    def _flet_main(page: ft.Page) -> None:
        _apply_common_page_settings(page)
        control = build_control_from_preview(target_obj, page)
        control_or_view = _wrap_with_layout_if_needed(control, wrap=wrap_layout)

        # View は page.add ではなく page.views へ追加し、update を明示
        # Control は通常通り add して update。
        try:
            import flet as ft

            if isinstance(control_or_view, ft.View):
                # 既存スタックを置き換え（単体表示用途）
                with suppress(Exception):
                    # [AI GENERATED] 一部環境で clear 未実装でも致命ではないため握りつぶす
                    page.views.clear()
                page.views.append(control_or_view)
                page.update()
            else:
                page.add(control_or_view)
                page.update()
        finally:
            logger.info("コンポーネントを起動しました")

    try:
        import flet as ft

        ft.app(target=_flet_main, assets_dir=str(SRC_DIR / "assets"), view=ft.AppView.WEB_BROWSER, port=8000)
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
