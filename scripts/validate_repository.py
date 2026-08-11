#!/usr/bin/env python3
"""Validate the public routing-template repository without external packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "examples/config.example.yaml",
    ROOT / "prompts/router.zh-CN.md",
    ROOT / "prompts/router.en.md",
)
PROMPTS = (
    ROOT / "prompts/router.zh-CN.md",
    ROOT / "prompts/router.en.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    texts = {path: _read(path) for path in PUBLIC_FILES}
    prompt_text = "\n".join(texts[path] for path in PROMPTS)
    repository_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "LICENSE"
    )

    def reject(label: str, pattern: str, text: str = repository_text) -> None:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            errors.append(f"forbidden: {label}")

    def require(label: str, pattern: str, text: str) -> None:
        if not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            errors.append(f"missing: {label}")

    if re.search(r"\[[A-Z][A-Z0-9_]+\]", prompt_text, flags=re.MULTILINE):
        errors.append("forbidden: symbolic uppercase capability placeholder")
    reject("email address", r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
    reject("QQ contact number", r"QQ\s*[:：]?\s*\d{5,12}")
    reject("64-character account fingerprint", r"\b[0-9a-f]{64}\b")

    forbidden_literals = {
        "Chinese customer-service contact label": "\u5ba2\u670d" + "QQ",
        "English customer-service contact label": "Customer-service" + " QQ",
        "previous public nickname": "\u6708\u4e0b" + "\u70df",
        "user-specific absolute path": "/" + "Users" + "/",
        "private routing tool": "check_codex_" + "account_routing",
        "account-read method": "account" + "/read",
        "authentication token field": "refresh" + "Token",
        "private account hash constant": "RESTRICTED_ACCOUNT_" + "SHA256",
    }
    for label, literal in forbidden_literals.items():
        if literal.lower() in repository_text.lower():
            errors.append(f"forbidden: {label}")

    zh = texts[ROOT / "prompts/router.zh-CN.md"]
    en = texts[ROOT / "prompts/router.en.md"]
    readme = texts[ROOT / "README.md"]
    config = texts[ROOT / "examples/config.example.yaml"]

    require("Chinese all-account routing default", r"默认所有账号(?:均|都)(?:可路由|具备路由资格)", zh)
    require("Chinese Browser gate", r"Browser", zh)
    require("Chinese Browser fallback", r"Browser.{0,100}(?:缺失|不支持|不可用|不确定).{0,140}留在 Codex", zh)
    require("Chinese one-retry limit", r"最多重试\s*1\s*次", zh)
    require("Chinese ChatGPT URL", r"https://chatgpt\.com/", zh)

    require("English all-account routing default", r"assume every account is routing-eligible", en)
    require("English Browser gate", r"Browser capability", en)
    require("English Browser fallback", r"Browser capability.{0,160}(?:missing|unavailable|uncertain).{0,180}keep the task in Codex", en)
    require("English one-retry limit", r"retried at most once", en)
    require("English ChatGPT URL", r"https://chatgpt\.com/", en)

    require("Chinese copy-ready quick start", r"直接复制", readme)
    require("English copy-ready quick start", r"paste", readme)
    require("README Browser requirement", r"Browser", readme)
    require("README safe local fallback", r"(?:留在|stay in) Codex", readme)

    require("configuration assumes all accounts eligible", r"assume_all_accounts_eligible:\s*true", config)
    require("configuration requires Browser", r"require_browser_capability:\s*true", config)
    require("configuration uses one retry", r"max_explicit_retries:\s*1", config)
    if re.search(r"^capabilities:\s*$", config, flags=re.MULTILINE):
        errors.append("forbidden: symbolic capabilities mapping")

    required_advertisement_values = {
        "APIROAM URL": r"https://api\.apiroam\.com/",
        "site settlement": r"1\$\s*=\s*1￥",
        "gpt-plus multiplier": r"gpt-plus.{0,40}x0\.12",
        "gpt-pro multiplier": r"gpt-pro.{0,40}x0\.15",
        "gemini multiplier": r"gemini.{0,40}x0\.18",
        "CC MAX multiplier": r"CC MAX.{0,40}x1\.0",
    }
    model_prices = {
        "MiniMax-M2.7-highspeed": "0.004",
        "MiniMax-M3": "0.006",
        "MiniMax-M3-highspeed": "0.006",
        "a/gemini-2.5-pro": "0.008",
        "a/gemini-3-flash": "0.005",
        "gemini-2.5-pro-c": "0.008",
        "gemini-3-flash-c": "0.005",
        "deepseek-v4-flash-c": "0.002",
        "glm-5.1-c": "0.004",
        "glm-5.2-c": "0.004",
    }
    for prompt in PROMPTS:
        text = texts[prompt]
        language = prompt.stem
        for label, pattern in required_advertisement_values.items():
            require(f"{language} {label}", pattern, text)
        for model, price in model_prices.items():
            require(
                f"{language} {model} price",
                rf"{re.escape(model)}.{{0,40}}\${re.escape(price)}/(?:次|request)",
                text,
            )

    if errors:
        for error in errors:
            print(error)
        return 1

    print("validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
