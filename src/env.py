"""envファイルや設定ファイルを作成し、管理するモジュール。

このモジュールは、.envファイルの作成や環境変数の管理を行います。
FletアプリケーションやAI関連の設定値を.envファイルに記述し、必要な環境変数が揃っているかをチェックします。
"""

import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from loguru import logger

# --- Flet app settings ---
FLET_VARIABLES = [
    "FLET_SECRET_KEY",
]
# --- AI settings ---
AI_VARIABLES = ["GOOGLE_API_KEY", "LANGSMITH_API_KEY", "LANGSMITH_TRACING"]
ALL_REQUIRED_VARS = FLET_VARIABLES + AI_VARIABLES

# --- .env file content ---
ENV_TEMPLATE = """# environment variables


## Flet variables
{FLET_VARIABLES}


## AI variables
{AI_VARIABLES}
"""


def setup_environment(env_path_str: str = ".env") -> None:
    """環境変数を設定し、.envファイルを作成または更新します。

    Args:
        env_path_str (str, optional): .envファイルのパス。 Defaults to ".env".
    """
    env_path = Path(env_path_str)

    if not env_path.exists():
        create_env_from_template(env_path)

    ensure_keys_in_env_file(env_path)

    load_dotenv(dotenv_path=env_path)
    logger.debug(f"環境変数をロードしました: {env_path}")

    check_env_variables()


def create_env_from_template(env_path: Path) -> None:
    """`.env`ファイルをテンプレートから作成します。

    Args:
        env_path (Path): 作成する.envファイルのパス。
    """
    flet_vars_str = "\n".join([f"{var}=" for var in FLET_VARIABLES])
    ai_vars_str = "\n".join([f"{var}=" for var in AI_VARIABLES])
    content = ENV_TEMPLATE.format(
        FLET_VARIABLES=flet_vars_str,
        AI_VARIABLES=ai_vars_str,
    )

    with env_path.open("w") as f:
        f.write(content)
    logger.info(f".envファイルを作成しました: {env_path}")
    logger.info("必要な情報を.envファイルに記入してください。")


def ensure_keys_in_env_file(env_path: Path) -> None:
    """.envファイルに必要な環境変数のキーが存在することを確認します。

    Args:
        env_path (Path): .envファイルのパス。
    """
    existing_vars = dotenv_values(env_path)

    missing_vars = [var for var in ALL_REQUIRED_VARS if var not in existing_vars]

    if missing_vars:
        logger.warning(f"下記のキーが.envファイルに存在しなかったため追記します: {missing_vars}")
        with env_path.open("a") as f:
            for var in missing_vars:
                f.write(f"{var}=\n")


def check_env_variables() -> None:
    """環境変数の存在を確認し、設定されていない場合は警告を出力します。

    必要な環境変数が設定されているかをチェックし、設定されていない場合は警告を出力します。
    """
    for var in ALL_REQUIRED_VARS:
        if not os.getenv(var):
            logger.warning(f"環境変数が設定されていません: {var}")


# def create_env_file() -> None:
#     """`.env`ファイルを作成し、必要な環境変数を設定します。

#     .envファイルが存在しない場合はデフォルトの環境変数を設定して作成し、存在する場合は何もしません。
#     また、環境変数の読み込みとチェックも行います。

#     Args:
#         なし

#     Returns:
#         None: 戻り値はありません。
#     """
#     if not env_path.exists():
#         with env_path.open("w") as f:
#             f.write(
#                 ENV_TEMPLATE.format(
#                     FLET_VARIABLES="\n".join([f"{var}=" for var in FLET_VARIABLES]),
#                     AI_VARIABLES="\n".join([f"{var}=" for var in AI_VARIABLES]),
#                 )
#             )
#         logger.debug(f".envファイルを作成しました: {env_path}")

#     load_dotenv()
#     check_env_variables()
#     # .envファイルが存在しない場合、デフォルトの環境変数を設定して作成します。
#     if not env_path.exists():
#         with env_path.open("w") as f:
#             f.write(
#                 ENV_TEMPLATE.format(
#                     FLET_VARIABLES="\n".join([f"{var}=" for var in FLET_VARIABLES]),
#                     AI_VARIABLES="\n".join([f"{var}=" for var in AI_VARIABLES]),
#                 )
#             )
#         logger.debug(f".envファイルを作成しました: {env_path}")

#     load_dotenv()
#     check_env_variables()


# def check_env_variables() -> None:
#     """環境変数の存在を確認する関数

#     必要な環境変数が設定されているかをチェックし、設定されていない場合は警告を出力します。
#     """
#     required_vars = FLET_VARIABLES + AI_VARIABLES

#     # .envファイルに環境変数のキーが書き込まれているかチェック
#     with env_path.open("r") as f:
#         content = f.read()
#         for var in required_vars:
#             if f"{var}=" not in content:
#                 # 追記して警告を出力
#                 with env_path.open("a") as append_file:
#                     append_file.write(f"{var}=\n")
#                 logger.warning(f".envファイルに環境変数が見つかりませんでした: {var}。追記しました。")

#     for var in required_vars:
#         if not os.getenv(var):
#             logger.warning(f"環境変数が設定されていません: {var}")
