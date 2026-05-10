# NewCoin Model Routing Recommendation

Status: discovery only. No Hermes behavior changed.

## Recommended Worker Tiers

- Basic/simple worker: `qwen3-32b`
- Coding/build worker: `qwen3-coder-plus`
- Complex reasoning worker: `kimi-k2`
- Vision/image worker: `qwen3-vl-plus`
- Source-verified research worker: `qwen3-32b` plus source-locked-research workflow
- Private Gmail/YouTube route: `openrouter/deepseek-chat-reserved-route-later`

## Safety Rules

- NewCoin may handle ordinary tasks, coding, documents, research, webapps, skills, and dashboards.
- NewCoin must not receive Gmail content, YouTube analytics/account data, OAuth tokens, API keys, passwords, or private credentials.
- Source-verified research must use saved raw sources, line-numbered quotes, and quote audit.
- Destructive actions still require confirmation.

## Candidate Models Found

### claude-haiku-4-5-20251001
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-haiku-4-5-20251001-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### claude-opus-4-5-20251101
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-5-20251101-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### claude-opus-4-5-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-5-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-6
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-6-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-6-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-opus-4-6-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### claude-opus-4-7
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4-5-20250929
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4-5-20250929-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### claude-sonnet-4-6
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4-6-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4-6-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4-6-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### claude-sonnet-4.5-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### claude-sonnet-4.5-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-ocr
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-ocr-2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-r1
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### deepseek-v3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-v3.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-v3.2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-v3.2-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### deepseek-v4-flash
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### deepseek-v4-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-1-5-pro-256k
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-1-5-pro-32k
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-1-6-250615
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-1-6-251015
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-1-6-flash-250615
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-1-6-flash-250828
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-1-6-thinking-250615
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### doubao-seed-1-6-thinking-250715
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### doubao-seed-1-6-vision-250815
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### doubao-seed-1-8-251228
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-2-0-code-preview-260215
- coding: True
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts

### doubao-seed-2-0-lite-260215
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seed-2-0-pro-260215
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-1-0-pro-250528
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-1-5-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-1-5-pro-10s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-1-5-pro-12s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-2-0_10s_720p
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-2-0_15s_720p
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedance-2-0_5s_720p
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedream-4-0-250828
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedream-4-5-251128
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### doubao-seedream-5-0-260128
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### flux-2-flex
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### flux-2-max
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### flux-2-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-flash
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro-128-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro-c3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro-c4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-2.5-pro-c5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-128-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-flash-preview-c5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-image-preview
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3-pro-image-preview-1k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3-pro-image-preview-2k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3-pro-image-preview-4k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3-pro-preview
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-128-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-c5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3-pro-preview-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3-pro-preview-thinking-c
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3-pro-preview-thinking-c1
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3-pro-preview-thinking-c2
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3-pro-preview-thinking-c3
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3-pro-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3.1-flash-image-preview
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3.1-flash-image-preview-1k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3.1-flash-image-preview-2k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3.1-flash-image-preview-4k
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gemini-3.1-flash-lite-preview-c2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-flash-lite-preview-c5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-128-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-c2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-c3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-c4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-c5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gemini-3.1-pro-preview-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gemini-3.1-pro-preview-thinking-c2
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### glm-4.6
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### glm-4.7
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### glm-5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### glm-5-turbo
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### glm-5.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-4o
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5-mini
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gpt-5.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.1-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### gpt-5.2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.3-codex
- coding: True
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts

### gpt-5.3-codex-spark
- coding: True
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts

### gpt-5.4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.4-high
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.4-low
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.4-medium
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.4-xhigh
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.5-high
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.5-low
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.5-medium
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-5.5-xhigh
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### gpt-image-1
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gpt-image-1.5
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### gpt-image-2
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### grok-4
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### grok-4-1-fast-non-reasoning
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### grok-4-1-fast-reasoning
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### grok-4.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### grok-4.1-c
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### grok-4.1-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### grok-4.2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### grok-code-fast-1
- coding: True
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts

### grok-imagine-0.9
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-4.0
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-4.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-4.5
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-4.6
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-5.0
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.0
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.0-10s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.0-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.0-pro-10s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.5-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.5-pro-10s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### jimeng-video-3.5-pro-12s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### kimi-k2
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### kimi-k2-250905
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### kimi-k2-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### kimi-k2.5
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### kimi-k2.6
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### kimi-k2.6-code-preview
- coding: True
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts, complex reasoning/planning/debugging

### mimo-v2-flash
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### mimo-v2-omni
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### mimo-v2-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### minimax-hailuo-02
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2.1
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2.5
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2.5-highspeed
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2.7
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### minimax-m2.7-highspeed
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen-image
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### qwen-image-2
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### qwen-image-edit
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis

### qwen3-235b-a22b
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3-235b-a22b-instruct-2507
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3-235b-a22b-thinking-2507
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3-32b
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: True
- recommended use: basic chat/research/summarization

### qwen3-coder-480b
- coding: True
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts, complex reasoning/planning/debugging

### qwen3-coder-plus
- coding: True
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: coding/build/webapp/scripts, complex reasoning/planning/debugging

### qwen3-max
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3-max-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3-vl-235b-a22b
- coding: False
- reasoning: True
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging, image/screenshot/receipt/UI analysis

### qwen3-vl-embedding-2b
- coding: False
- reasoning: False
- vision: True
- embedding: True
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis, embedding/search only
- notes: Not suitable as a normal chat worker.

### qwen3-vl-embedding-8b
- coding: False
- reasoning: False
- vision: True
- embedding: True
- reranker: False
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis, embedding/search only
- notes: Not suitable as a normal chat worker.

### qwen3-vl-plus
- coding: False
- reasoning: True
- vision: True
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging, image/screenshot/receipt/UI analysis

### qwen3-vl-reranker-2b
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: True
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis, reranking/search only
- notes: Not suitable as a normal chat worker.

### qwen3-vl-reranker-8b
- coding: False
- reasoning: False
- vision: True
- embedding: False
- reranker: True
- likely cheap/basic: False
- recommended use: image/screenshot/receipt/UI analysis, reranking/search only
- notes: Not suitable as a normal chat worker.

### qwen3.5-397b-a17b
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3.5-plus
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: True
- recommended use: complex reasoning/planning/debugging, basic chat/research/summarization

### qwen3.5-plus-thinking
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: True
- recommended use: complex reasoning/planning/debugging, basic chat/research/summarization

### qwen3.6-max-preview
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: complex reasoning/planning/debugging

### qwen3.6-plus
- coding: False
- reasoning: True
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: True
- recommended use: complex reasoning/planning/debugging, basic chat/research/summarization

### sora-2
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### sora-2-12s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### sora-2-8s
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### sora-2-hd
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### sora-2-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### veo3
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### veo3-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### veo3.1
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### veo3.1-4k
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing

### veo3.1-pro
- coding: False
- reasoning: False
- vision: False
- embedding: False
- reranker: False
- likely cheap/basic: False
- recommended use: general candidate; needs testing
