# 下位互換のためのエイリアス・利便性モジュール
"""用語管理関連モデルの便利インポート

このモジュールは、models.__init__.pyに定義されている用語関連モデルへの
ショートカット・エイリアスを提供します。

メインの定義は models.__init__.py にあり、
このファイルは下位互換性と利便性のために用意されています。
"""

from models import (
    Synonym,
    SynonymBase,
    SynonymCreate,
    SynonymRead,
    SynonymUpdate,
    Term,
    TermBase,
    TermCreate,
    TermRead,
    TermStatus,
    TermUpdate,
)

# 下位互換のためのエイリアス
Terminology = Term
TerminologyStatus = TermStatus

__all__ = [
    # 用語関連
    "Term",
    "TermBase",
    "TermCreate",
    "TermRead",
    "TermStatus",
    "TermUpdate",
    # 同義語関連
    "Synonym",
    "SynonymBase",
    "SynonymCreate",
    "SynonymRead",
    "SynonymUpdate",
    # 下位互換エイリアス
    "Terminology",
    "TerminologyStatus",
]
