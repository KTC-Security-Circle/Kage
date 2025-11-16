"""アプリ設定モデル定義モジュール。

[AI GENERATED] Pydantic v2 を用いてアプリケーション設定の不変モデルを定義する。`ConfigManager` が YAML との変換を行う。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Final, Literal

from dotenv import dotenv_values, load_dotenv
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from agents.agent_conf import HuggingFaceModel, LLMProvider  # [AI GENERATED] Enum によるバリデーション

# テーマ定数
AVAILABLE_THEMES: Final[list[tuple[str, str]]] = [
    ("light", "ライト"),
    ("dark", "ダーク"),
]


class WindowSettings(BaseModel):
    """ウィンドウ表示に関する設定。

    サイズと位置は整数 2 要素のリストで保持する。
    """

    model_config = ConfigDict(frozen=True)

    size: list[int] = Field(
        default=[1280, 720],
        description="""起動時のウィンドウサイズ。[幅, 高さ] のリスト。""",
    )
    position: list[int] = Field(
        default=[100, 100],
        description="起動時のウィンドウ位置。[X, Y] のリスト。",
    )


class EditableWindowSettings(BaseModel):
    """編集可能なウィンドウ設定。

    不変モデルとの差異: frozen=False。
    """

    model_config = ConfigDict(frozen=False)

    size: list[int] = Field(
        default=[1280, 720],
        description="""起動時のウィンドウサイズ。[幅, 高さ] のリスト。""",
    )
    position: list[int] = Field(
        default=[100, 100],
        description="起動時のウィンドウ位置。[X, Y] のリスト。",
    )


class UserSettings(BaseModel):
    """ユーザー固有の UI/動作設定。"""

    model_config = ConfigDict(frozen=True)

    last_login_user: str | None = Field(
        default=None,
        description="最後にログインしたユーザー名 (未ログインは null)。",
    )
    theme: str = Field(
        default="light",
        description="UI テーマ。'light' または 'dark'。",
    )
    user_name: str = Field(
        default="",
        description="アプリ内で表示/プロンプトに利用する利用者の表示名。空なら匿名扱い。",
    )


class EditableUserSettings(BaseModel):
    """編集可能なユーザー設定。"""

    model_config = ConfigDict(frozen=False)

    last_login_user: str | None = Field(
        default=None,
        description="最後にログインしたユーザー名 (未ログインは null)。",
    )
    theme: str = Field(
        default="light",
        description="UI テーマ。'light' または 'dark'。",
    )
    user_name: str = Field(
        default="",
        description="アプリ内で表示/プロンプトに利用する利用者の表示名。",
    )


class HuggingFaceAgentModels(BaseModel):
    """HuggingFace/OPENVINO 系で利用するエージェント別モデル名設定。"""

    model_config = ConfigDict(frozen=True)

    one_liner: HuggingFaceModel | None = Field(
        default=None,
        description="one_liner エージェント用 HuggingFaceModel Enum。None ならデフォルト内部値。",
    )


class GeminiAgentModels(BaseModel):
    """Gemini(google) 用モデル名設定。将来 Enum 化予定。"""

    model_config = ConfigDict(frozen=True)

    one_liner: str | None = Field(
        default=None,
        description="one_liner エージェント用 Gemini モデル名。None ならライブラリ既定。",
    )


class AgentRuntimeSettings(BaseModel):
    """LLM 実行時設定。"""

    model_config = ConfigDict(frozen=True)

    model: str | None = Field(default=None, description="LLMモデル名。None の場合は内部既定を使用。")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="LLM温度 (0.0〜1.0)")
    debug_mode: bool = Field(default=False, description="詳細ログやデバッグモードを有効にする")


class AgentsSettings(BaseModel):
    """エージェント全体設定 (互換性考慮せず再構築)。"""

    model_config = ConfigDict(frozen=True)

    provider: LLMProvider = Field(
        default=LLMProvider.FAKE,
        description="全エージェント共通で使用する LLM プロバイダ。",
    )
    runtime: AgentRuntimeSettings = Field(default_factory=AgentRuntimeSettings, description="LLM 実行時設定")
    huggingface: HuggingFaceAgentModels | EditableHuggingFaceAgentModels = Field(
        default_factory=HuggingFaceAgentModels, description="HuggingFace/OPENVINO 系モデル設定"
    )
    gemini: GeminiAgentModels | EditableGeminiAgentModels = Field(
        default_factory=GeminiAgentModels, description="Gemini モデル設定"
    )

    def get_model_name(self, agent_key: str) -> HuggingFaceModel | str | None:  # [AI GENERATED]
        """現在の provider に応じて該当エージェントのモデル名 (Enum/str/None) を返す。

        Args:
            agent_key (str): エージェント識別子 (例: 'one_liner')

        Returns:
            HuggingFaceModel | str | None: モデル名。未指定時は None。
        """
        if self.provider in (LLMProvider.OPENVINO,):
            return getattr(self.huggingface, agent_key, None)
        if self.provider == LLMProvider.GOOGLE:
            return getattr(self.gemini, agent_key, None)
        return None

    # editable -> frozen 変換受け入れ (settings.manager の round-trip 用) [AI GENERATED]
    @field_validator("huggingface", mode="before")
    @classmethod
    def _from_editable_hf(
        cls, v: HuggingFaceAgentModels | EditableHuggingFaceAgentModels | dict[str, Any] | None
    ) -> HuggingFaceAgentModels | dict[str, Any] | None:
        if isinstance(v, EditableHuggingFaceAgentModels) and not isinstance(v, HuggingFaceAgentModels):
            return HuggingFaceAgentModels.model_validate(v.model_dump())
        return v

    @field_validator("gemini", mode="before")
    @classmethod
    def _from_editable_gemini(
        cls, v: GeminiAgentModels | EditableGeminiAgentModels | dict[str, Any] | None
    ) -> GeminiAgentModels | dict[str, Any] | None:
        if isinstance(v, EditableGeminiAgentModels) and not isinstance(v, GeminiAgentModels):
            return GeminiAgentModels.model_validate(v.model_dump())
        return v

    @field_validator("runtime", mode="before")
    @classmethod
    def _from_editable_runtime(
        cls, v: AgentRuntimeSettings | EditableAgentRuntimeSettings | dict[str, Any] | None
    ) -> AgentRuntimeSettings | dict[str, Any] | None:
        if isinstance(v, EditableAgentRuntimeSettings) and not isinstance(v, AgentRuntimeSettings):
            return AgentRuntimeSettings.model_validate(v.model_dump())
        return v


class EditableHuggingFaceAgentModels(BaseModel):
    model_config = ConfigDict(frozen=False)
    one_liner: HuggingFaceModel | None = Field(default=None)


class EditableGeminiAgentModels(BaseModel):
    model_config = ConfigDict(frozen=False)
    one_liner: str | None = Field(default=None)


class EditableAgentRuntimeSettings(BaseModel):
    model_config = ConfigDict(frozen=False)

    model: str | None = Field(default=None)
    temperature: float = Field(default=0.2)
    debug_mode: bool = Field(default=False)


class EditableAgentsSettings(BaseModel):
    """編集可能: provider とプロバイダ別モデル設定。"""

    model_config = ConfigDict(frozen=False)

    provider: LLMProvider = Field(default=LLMProvider.FAKE)
    runtime: EditableAgentRuntimeSettings | AgentRuntimeSettings = Field(default_factory=EditableAgentRuntimeSettings)
    huggingface: EditableHuggingFaceAgentModels | HuggingFaceAgentModels = Field(
        default_factory=EditableHuggingFaceAgentModels
    )
    gemini: EditableGeminiAgentModels | GeminiAgentModels = Field(default_factory=EditableGeminiAgentModels)

    def get_model_name(self, agent_key: str) -> HuggingFaceModel | str | None:  # [AI GENERATED]
        if self.provider in (LLMProvider.OPENVINO,):
            hf = self.huggingface
            return getattr(hf, agent_key, None)
        if self.provider == LLMProvider.GOOGLE:
            gm = self.gemini
            return getattr(gm, agent_key, None)
        return None

    # --- converters (before validators) ---
    @field_validator("huggingface", mode="before")  # [AI GENERATED]
    @classmethod
    def _convert_huggingface(
        cls, v: EditableHuggingFaceAgentModels | HuggingFaceAgentModels | dict[str, Any] | None
    ) -> EditableHuggingFaceAgentModels | dict[str, Any] | None:
        if isinstance(v, HuggingFaceAgentModels) and not isinstance(v, EditableHuggingFaceAgentModels):
            # frozen -> editable へコピー
            return EditableHuggingFaceAgentModels.model_validate(v.model_dump())
        return v

    @field_validator("gemini", mode="before")  # [AI GENERATED]
    @classmethod
    def _convert_gemini(
        cls, v: EditableGeminiAgentModels | GeminiAgentModels | dict[str, Any] | None
    ) -> EditableGeminiAgentModels | dict[str, Any] | None:
        if isinstance(v, GeminiAgentModels) and not isinstance(v, EditableGeminiAgentModels):
            return EditableGeminiAgentModels.model_validate(v.model_dump())
        return v

    @field_validator("runtime", mode="before")
    @classmethod
    def _convert_runtime(
        cls, v: EditableAgentRuntimeSettings | AgentRuntimeSettings | dict[str, Any] | None
    ) -> EditableAgentRuntimeSettings | dict[str, Any] | None:
        if isinstance(v, AgentRuntimeSettings) and not isinstance(v, EditableAgentRuntimeSettings):
            return EditableAgentRuntimeSettings.model_validate(v.model_dump())
        return v


class DatabaseSettings(BaseModel):
    """データベース接続に関する設定。"""

    model_config = ConfigDict(frozen=True)

    # 既存の SQLite 利用を想定し最低限のフィールドのみ。将来拡張時は別モデルへ分離。
    url: str = Field(
        default="sqlite:///storage/data/tasks.db",
        description="接続 URL。既定はアプリ内 SQLite ファイル。",
    )


class EditableDatabaseSettings(BaseModel):
    """編集可能なデータベース設定。"""

    model_config = ConfigDict(frozen=False)

    url: str = Field(
        default="sqlite:///storage/data/tasks.db",
        description="接続 URL。既定はアプリ内 SQLite ファイル。",
    )


class AppSettings(BaseModel):
    """アプリケーション全体の設定ルートモデル。

    このファイルは初回起動時に YAML として生成され、以後編集はコンテキストマネージャ経由で行う。
    """

    model_config = ConfigDict(frozen=True)

    window: WindowSettings = Field(default_factory=WindowSettings, description="ウィンドウ関連設定。")
    user: UserSettings = Field(default_factory=UserSettings, description="ユーザー関連設定。")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings, description="データベース設定。")
    agents: AgentsSettings = Field(default_factory=AgentsSettings, description="エージェント関連設定。")

    # one_liner_provider は agents.one_liner_provider をそのまま利用 (Enum 化後は単純委譲不要)


class EditableAppSettings(BaseModel):
    """編集可能なアプリケーション設定。"""

    model_config = ConfigDict(frozen=False)

    window: EditableWindowSettings = Field(default_factory=EditableWindowSettings, description="ウィンドウ関連設定。")
    user: EditableUserSettings = Field(default_factory=EditableUserSettings, description="ユーザー関連設定。")
    database: EditableDatabaseSettings = Field(
        default_factory=EditableDatabaseSettings, description="データベース設定。"
    )
    agents: EditableAgentsSettings = Field(default_factory=EditableAgentsSettings, description="エージェント関連設定。")

    # Editable も単純参照で十分 (直接 editable.agents.one_liner_provider を編集)


# -- 環境変数 --------------------------------

EnvVarType = Literal["str", "bool"]


@dataclass(frozen=True)
class EnvVarDef:  # [AI GENERATED]
    """環境変数定義メタデータ。

    Attributes:
        key: 環境変数名
        type: 変数種別 ("str" | "bool")
        category: 分類 (例: "flet", "ai", "db")
        default: .env 生成時のデフォルト文字列 (None なら空)
        comment: 行末コメント
    """

    key: str
    type: EnvVarType
    category: str
    default: str | None = None
    comment: str | None = None


ENV_VARS: Final[list[EnvVarDef]] = [
    EnvVarDef("FLET_SECRET_KEY", "str", "flet"),
    EnvVarDef("GOOGLE_API_KEY", "str", "ai"),
    EnvVarDef("LANGSMITH_API_KEY", "str", "ai"),
    EnvVarDef("LANGSMITH_TRACING", "bool", "ai", default="false", comment="false/true"),
    EnvVarDef("KAGE_USE_LLM_ONE_LINER", "bool", "ai", default="false", comment="false/true"),
    EnvVarDef("HUGGINGFACEHUB_API_TOKEN", "str", "ai"),
    EnvVarDef("DATABASE_URL", "str", "db"),
]

ENV_FLET_KEYS: Final[list[str]] = [v.key for v in ENV_VARS if v.category == "flet"]
ENV_AI_KEYS: Final[list[str]] = [v.key for v in ENV_VARS if v.category == "ai"]
ENV_DB_KEYS: Final[list[str]] = [v.key for v in ENV_VARS if v.category == "db"]
ENV_SETTINGS_KEYS: Final[list[str]] = [v.key for v in ENV_VARS]
ENV_BOOL_KEYS: Final[set[str]] = {v.key for v in ENV_VARS if v.type == "bool"}


class EnvSettings(BaseSettings):
    """環境変数設定モデル。

    空文字列 (="") が .env に存在する場合、Pydantic の bool 変換で ValidationError になるため
    事前バリデータで None に変換して未設定扱いにする。
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # キャッシュ管理 (単一インスタンスを再利用)
    _cached: ClassVar[EnvSettings | None] = None  # [AI GENERATED] インスタンスキャッシュ
    _initialized: ClassVar[bool] = False  # [AI GENERATED] init_environment 実行済みフラグ

    flet_secret_key: str | None = Field(default=None, alias="FLET_SECRET_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_tracing: bool | None = Field(default=None, alias="LANGSMITH_TRACING")
    kage_use_llm_one_liner: bool | None = Field(default=None, alias="KAGE_USE_LLM_ONE_LINER")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    @field_validator("langsmith_tracing", "kage_use_llm_one_liner", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v: object) -> object:  # [AI GENERATED] 空文字を未設定扱いに変換
        if isinstance(v, str):
            raw = v
            # インラインコメントが含まれる場合 (' # ' 区切り) はコメント除去
            if "#" in raw:
                # 例: 'false  # false/true' -> 'false'
                raw = raw.split("#", 1)[0]
            raw = raw.strip()
            if raw == "":
                return None
            return raw  # bool 変換は pydantic に委ねる
        return v

    # --- utilities -------------------------------------
    @classmethod
    def init_environment(cls, env_path: str | Path = ".env") -> None:
        """環境ファイルの作成/不足キー追記/ロード/警告出力をまとめて実行。

        Args:
            env_path (str | Path): .env ファイルパス
        """
        env_path = Path(env_path)
        if not env_path.exists():
            cls._create_env_file(env_path)
        cls._ensure_keys(env_path)
        load_dotenv(env_path)
        logger.debug(f"環境変数をロードしました: {env_path}")
        cls._initialized = True  # [AI GENERATED] 初期化完了フラグ
        cls._cached = None  # [AI GENERATED] 再ロード時に再評価させる
        cls._warn_unset()

    @classmethod
    def get(cls) -> EnvSettings:  # [AI GENERATED] 環境設定インスタンス取得
        """キャッシュされた `EnvSettings` インスタンスを返す。

        init_environment が未呼び出しの場合は自動的に呼び出した上で生成する。
        Returns:
            EnvSettings: 環境設定インスタンス
        """
        if cls._cached is None:
            if not cls._initialized:
                cls.init_environment()
            cls._cached = cls()
        return cls._cached

    @classmethod
    def _create_env_file(cls, env_path: Path) -> None:
        """.env ファイルを作成し、必要な環境変数のキーを定義する。

        Args:
            env_path (Path): .env ファイルのパス
        """
        sections: dict[str, list[str]] = {}
        for var in ENV_VARS:
            sections.setdefault(var.category, []).append(cls._format_env_line(var))  # [AI GENERATED] 共通化
        lines: list[str] = ["# environment variables", ""]
        for category, vars_lines in sections.items():
            lines.append(f"## {category} variables")
            lines.extend(vars_lines)
            lines.append("")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info(f".envファイルを作成しました: {env_path}")

    @classmethod
    def _ensure_keys(cls, env_path: Path) -> None:
        """.env ファイルに必要な環境変数のキーが存在することを確認し、不足している場合は追記する。

        Args:
            env_path (Path): .env ファイルのパス
        """
        existing = dotenv_values(env_path)
        missing_defs = [v for v in ENV_VARS if v.key not in existing]
        if not missing_defs:
            return
        with env_path.open("a", encoding="utf-8") as f:
            for var in missing_defs:
                f.write(cls._format_env_line(var) + "\n")  # [AI GENERATED] 共通化
        logger.warning(f".env に不足キーを追記しました: {[v.key for v in missing_defs]}")

    @classmethod
    def _warn_unset(cls) -> None:
        """環境変数が未設定の場合の警告を出力する。"""
        inst = cls.get()
        for var in ENV_VARS:
            value = getattr(inst, var.key.lower()) if hasattr(inst, var.key.lower()) else None
            if value in (None, ""):
                logger.warning(f"環境変数が設定されていません: {var.key}")

    @staticmethod
    def _format_env_line(var: EnvVarDef) -> str:
        """EnvVarDef から .env 用の1行を生成する。

        Args:
            var (EnvVarDef): 変換対象

        Returns:
            str: FOO=bar 形式 (コメント含む)
        """
        default_part = var.default if var.default is not None else ""
        comment_part = f"  # {var.comment}" if var.comment else ""
        return f"{var.key}={default_part}{comment_part}"


__all__ = [
    "WindowSettings",
    "UserSettings",
    "DatabaseSettings",
    "AppSettings",
    "EditableWindowSettings",
    "EditableUserSettings",
    "EditableDatabaseSettings",
    "EditableAppSettings",
    "AgentsSettings",
    "EditableAgentsSettings",
    "EnvSettings",
]
