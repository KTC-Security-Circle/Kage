#!/bin/bash


uv tool install poethepoet

uv sync --frozen

# Devcontainer環境下ではvenvの置き場所が違うのでシンボリックリンクを貼る
ln -sfn /home/vscode/.venv /workspace/.venv

uv run pre-commit install
