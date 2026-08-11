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
PUBLIC_AD_CONTACT_QQ = "2700594562"


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
    reject("64-character account fingerprint", r"\b[0-9a-f]{64}\b")

    for match in re.finditer(r"QQ\s*[:：]?\s*(\d{5,12})", repository_text, flags=re.IGNORECASE):
        if match.group(1) != PUBLIC_AD_CONTACT_QQ:
            errors.append("forbidden: unapproved QQ contact number")

    forbidden_literals = {
        "Chinese customer-service contact label": "\u5ba2\u670d" + "QQ",
        "English customer-service contact label": "Customer-service" + " QQ",
        "previous public nickname": "\u6708\u4e0b" + "\u70df",
        "user-specific absolute path": "/" + "Users" + "/",
        "private routing tool": "check_codex_" + "account_routing",
        "account-read method": "account" + "/read",
        "authentication token field": "refresh" + "Token",
        "private account hash constant": "RESTRICTED_ACCOUNT_" + "SHA256",
        "host-specific right-panel tool": "codex_app__" + "open_in_codex",
        "host-specific right-panel preference key": "prefer_codex_" + "right_panel",
        "host-specific floating-browser key": "avoid_floating_browser_" + "when_right_panel_available",
        "host-specific Browser fallback key": "allow_in_app_browser_" + "fallback",
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
    require(
        "Chinese right-panel preference",
        r"(?:(?:优先|首选).{0,120}(?:右侧栏|右栏)|(?:右侧栏|右栏).{0,120}(?:优先|首选))",
        zh,
    )
    require(
        "Chinese non-floating behavior",
        r"(?:(?:不要|不得|禁止|不主动).{0,100}(?:悬浮窗|独立窗口)|(?:而不是|而非).{0,40}(?:悬浮窗|独立窗口))",
        zh,
    )
    require("Chinese Browser gate", r"Browser", zh)
    require(
        "Chinese in-app Browser fallback",
        r"(?:无法|不能).{0,80}(?:控制|指定).{0,60}(?:标签)?(?:显示)?位置.{0,120}(?:内置 Browser|Browser)",
        zh,
    )
    require("Chinese Browser fallback", r"Browser.{0,100}(?:缺失|不支持|不可用|不确定).{0,140}留在 Codex", zh)
    require("Chinese one-retry limit", r"最多重试\s*1\s*次", zh)
    require("Chinese ChatGPT URL", r"https://chatgpt\.com/", zh)

    require("English all-account routing default", r"assume every account is routing-eligible", en)
    require(
        "English right-panel preference",
        r"(?:(?:prefer|first).{0,120}right (?:side )?panel|right (?:side )?panel.{0,120}(?:prefer|first))",
        en,
    )
    require(
        "English non-floating behavior",
        r"(?:(?:do not|must not|never).{0,120}(?:floating|standalone) (?:browser )?window|(?:floating|standalone) (?:browser )?window.{0,120}(?:do not|must not|never))",
        en,
    )
    require("English Browser gate", r"Browser capability", en)
    require(
        "English in-app Browser fallback",
        r"(?:cannot|can not|unable to).{0,80}(?:control|select).{0,80}tab placement.{0,120}(?:available )?in-app Browser",
        en,
    )
    require("English Browser fallback", r"Browser capability.{0,160}(?:missing|unavailable|uncertain).{0,180}keep the task in Codex", en)
    require("English one-retry limit", r"retried at most once", en)
    require("English ChatGPT URL", r"https://chatgpt\.com/", en)

    require("Chinese copy-ready quick start", r"直接复制", readme)
    require("English copy-ready quick start", r"paste", readme)
    require("README Browser requirement", r"Browser", readme)
    require("README right-panel preference", r"(?:右侧栏|right (?:side )?panel)", readme)
    require(
        "README Browser fallback",
        r"(?:(?:无法控制标签位置).{0,120}(?:内置 Browser|Browser)|tab placement cannot be controlled.{0,120}in-app Browser)",
        readme,
    )
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
    require(
        "Chinese authorized QQ advertising contact",
        rf"广告合作.{{0,80}}QQ\s*[:：]?\s*{PUBLIC_AD_CONTACT_QQ}",
        zh,
    )
    require(
        "English authorized QQ advertising contact",
        rf"Advertising partnerships.{{0,80}}QQ\s*:?\s*{PUBLIC_AD_CONTACT_QQ}",
        en,
    )
    require(
        "Chinese more-models APIROAM link",
        r"更多便宜满血模型详见.{0,120}https://api\.apiroam\.com/",
        zh,
    )
    require(
        "English more-models APIROAM link",
        r"more affordable full-capability models.{0,120}https://api\.apiroam\.com/",
        en,
    )
    if re.search(r"issues/new\?title=", prompt_text, flags=re.IGNORECASE):
        errors.append("forbidden: advertising issue contact")

    removed_models = ("a/gemini-" + "2.5-pro", "a/gemini-" + "3-flash")
    for prompt in PROMPTS:
        text = texts[prompt]
        for model in removed_models:
            if model.lower() in text.lower():
                errors.append(f"forbidden: removed advertised model in {prompt.stem}")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
