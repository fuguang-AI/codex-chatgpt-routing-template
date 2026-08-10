# Codex–ChatGPT Routing Template

A privacy-conscious bilingual prompt template for deciding whether work should stay in Codex, move to the ChatGPT web interface, or be split between them.

一套注重隐私的中英文提示词模板，用于自动判断任务应留在 Codex、转交 ChatGPT 网页端，还是拆分后分别处理。

> [!IMPORTANT]
> This repository contains policy text and symbolic configuration only. It does not provide browser automation, authentication, or account-entitlement checks. Your host environment must implement those capabilities, and you must verify current product behavior before use.

## Why this exists / 项目目标

Some tasks benefit from a local coding agent with file, terminal, application, or server access. Other tasks—such as public research, synthesis, translation, and long-form writing—may be better handled in a general ChatGPT session. This template adds a routing gate before substantive work begins, minimizes data disclosure, and prevents both agents from doing the same work twice.

部分任务必须访问本地文件、终端、应用或服务器；公开资料研究、综合整理、翻译与长篇写作则可能更适合普通 ChatGPT 会话。本模板在实质工作开始前执行路由判断，并通过最小披露和单一执行规则避免隐私泄露与重复消耗。

## Routing model / 路由模型

```mermaid
flowchart TD
    A["New task / 新任务"] --> B{"Needs local or private context? / 需要本地或私有上下文？"}
    B -- "Yes / 是" --> C["Keep in Codex / 留在 Codex"]
    B -- "No / 否" --> D{"Independently web-suitable? / 可独立交给网页端？"}
    D -- "No / 否" --> C
    D -- "Yes / 是" --> E{"Eligibility check passes? / 资格检查通过？"}
    E -- "No or unknown / 否或不确定" --> C
    E -- "Yes / 是" --> F["Send minimal sanitized handoff / 提交最小脱敏移交包"]
    F --> G["Stop duplicate local work / 停止本地重复执行"]
    G --> H["Retrieve once, validate, integrate / 一次性取回、验证并整合"]
```

## Repository contents / 仓库内容

- [Chinese prompt / 中文提示词](prompts/router.zh-CN.md)
- [English prompt / 英文提示词](prompts/router.en.md)
- [Configuration example / 配置示例](examples/config.example.yaml)
- [Security policy / 安全说明](SECURITY.md)
- [MIT License](LICENSE)

## Quick start / 快速开始

1. Choose the prompt language and add it to your Codex custom instructions or project policy.
2. Copy `examples/config.example.yaml` into your own private configuration location.
3. Map each symbolic capability name to a tool your host actually provides.
4. Implement the eligibility check as a strict boolean. Treat errors, absence, and uncertainty as `false`.
5. Test with non-sensitive sample tasks before using the router with real work.

1. 选择中文或英文提示词，将其加入 Codex 自定义指令或项目策略。
2. 把 `examples/config.example.yaml` 复制到您自己的私有配置位置。
3. 将配置中的符号能力名称映射到宿主环境真实提供的工具。
4. 将资格检查实现为严格布尔值；报错、缺失或不确定一律按 `false` 处理。
5. 先用无敏感信息的示例任务测试，再用于真实工作。

The capability names in the example are identifiers, not callable commands. Never put secrets in the YAML file.

配置示例中的能力名称只是标识符，不是可直接执行的命令。切勿把秘密写入 YAML 文件。

## Example decisions / 判断示例

| Request | Route | Reason |
|---|---|---|
| Summarize public reports without private context | ChatGPT web, if eligible | Independent public-information work |
| Fix and test code in a local repository | Codex | Requires local files and execution |
| Research public alternatives, then modify private code | Split | Public research can be handed off; implementation stays local |
| Analyze an unpublished dataset | Codex | Private data must not be disclosed |

## Safety defaults / 安全默认值

- Local-only when eligibility is false, unavailable, or uncertain.
- Send only the minimum sanitized context required for the delegated task.
- Never send credentials, session data, personal information, unpublished material, or complete private code.
- After a handoff, do not repeat the same research or writing locally.
- Sign-in, account switching, verification, payment, private-file upload, and public publishing require explicit user confirmation.
- A queued web task is not a failure; one explicit retry is allowed by default, then the workflow stops and reports the problem.

## Limitations / 局限

- A prompt cannot create missing browser-control or account-check capabilities.
- ChatGPT and Codex interfaces, product rules, models, and usage accounting can change. Verify them from official sources before relying on a route.
- Automatic classification can be wrong. Keep human confirmation for sensitive or consequential actions.
- This template is an operational starting point, not a security boundary or compliance certification.

## License and trademarks

Released under the [MIT License](LICENSE). This community project is not affiliated with or endorsed by OpenAI. Codex, ChatGPT, and OpenAI are trademarks of their respective owner.

