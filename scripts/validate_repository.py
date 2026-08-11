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
        "payment QR code": "收" + "款码",
        "appreciation QR code": "赞" + "赏码",
        "tipping request": "打" + "赏",
        "WeChat Pay": "微" + "信支付",
        "Alipay": "支" + "付宝",
        "public giving appeal": "don" + "at",
        "public gratuity appeal": "tip" + " jar",
    }
    for label, literal in forbidden_literals.items():
        if literal.lower() in repository_text.lower():
            errors.append(f"forbidden: {label}")

    zh = texts[ROOT / "prompts/router.zh-CN.md"]
    en = texts[ROOT / "prompts/router.en.md"]
    readme = texts[ROOT / "README.md"]
    config = texts[ROOT / "examples/config.example.yaml"]

    require("Chinese all-account routing default", r"默认所有账号(?:均|都)(?:可路由|具备路由资格)", zh)
    require("Chinese Codex right-panel tool", r"codex_app__open_in_codex", zh)
    require("Chinese right placement", r"placement.{0,30}right", zh)
    require("Chinese right-panel preference", r"(?:右侧栏|右栏).{0,120}(?:优先|首选)", zh)
    require(
        "Chinese non-floating behavior",
        r"(?:(?:不要|不得|禁止).{0,100}(?:悬浮窗|独立窗口)|(?:悬浮窗|独立窗口).{0,100}(?:不要|不得|禁止))",
        zh,
    )
    require("Chinese Browser gate", r"Browser", zh)
    require(
        "Chinese in-app Browser fallback",
        r"(?:失败|不可用|缺失).{0,180}(?:(?:回退|兜底).{0,120}(?:内置浏览器|Browser)|(?:内置浏览器|Browser).{0,120}(?:回退|兜底))",
        zh,
    )
    require("Chinese Browser fallback", r"Browser.{0,100}(?:缺失|不支持|不可用|不确定).{0,140}留在 Codex", zh)
    require("Chinese one-retry limit", r"最多重试\s*1\s*次", zh)
    require("Chinese ChatGPT URL", r"https://chatgpt\.com/", zh)

    require("English all-account routing default", r"assume every account is routing-eligible", en)
    require("English Codex right-panel tool", r"codex_app__open_in_codex", en)
    require("English right placement", r"placement.{0,30}right", en)
    require("English right-panel preference", r"right (?:side )?panel.{0,120}(?:prefer|first)", en)
    require(
        "English non-floating behavior",
        r"(?:(?:do not|must not|never).{0,120}(?:floating|standalone) (?:browser )?window|(?:floating|standalone) (?:browser )?window.{0,120}(?:do not|must not|never))",
        en,
    )
    require("English Browser gate", r"Browser capability", en)
    require("English in-app Browser fallback", r"(?:fails|unavailable|missing).{0,180}in-app Browser.{0,120}(?:fall back|fallback)", en)
    require("English Browser fallback", r"Browser capability.{0,160}(?:missing|unavailable|uncertain).{0,180}keep the task in Codex", en)
    require("English one-retry limit", r"retried at most once", en)
    require("English ChatGPT URL", r"https://chatgpt\.com/", en)

    require("Chinese copy-ready quick start", r"直接复制", readme)
    require("English copy-ready quick start", r"paste", readme)
    require("README Browser requirement", r"Browser", readme)
    require("README Codex right-panel tool", r"codex_app__open_in_codex", readme)
    require("README right-panel preference", r"(?:右侧栏|right (?:side )?panel)", readme)
    require("README Browser fallback", r"(?:回退|fallback).{0,100}(?:内置浏览器|Browser)", readme)
    require("README safe local fallback", r"(?:留在|stay in) Codex", readme)

    require("configuration assumes all accounts eligible", r"assume_all_accounts_eligible:\s*true", config)
    require("configuration prefers Codex right panel", r"prefer_codex_right_panel:\s*true", config)
    require(
        "configuration avoids floating Browser",
        r"avoid_floating_browser_when_right_panel_available:\s*true",
        config,
    )
    require("configuration allows in-app Browser fallback", r"allow_in_app_browser_fallback:\s*true", config)
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

    require("Chinese advertisement heading", r"实测稳定、便宜、快速的 API 聚合站点", zh)
    require("English advertisement heading", r"Field-Tested, Stable, Affordable, and Fast API Hub", en)
    require("Chinese advertising partnerships", r"广告位招商", zh)
    require("English advertising partnerships", r"Advertising Partnerships", en)
    require("Chinese advertising issue contact", r"issues/new\?title=.*(?:%E3%80%90|广告合作)", zh)
    require("English advertising issue contact", r"issues/new\?title=.*Advertising", en)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
