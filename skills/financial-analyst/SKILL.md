---
name: financial-analyst
description: 포트폴리오 분석을 위한 Python 계산 스크립트 모음
license: MIT
compatibility: opencode
metadata:
  audience: financial analysts
  category: finance
  purpose: investment portfolio analysis
  version: 3.0
---

# Financial Analyst Skill

LLM이 직접 분석/판단하고, 정밀 계산이 필요한 경우에만 아래 스크립트를 사용합니다.

## Tools

### 1. Ratio Calculator (`scripts/ratio_calculator.py`)
재무 비율 계산. stdin 입력 → stdout 출력.

```bash
echo '{"income_statement": {...}, "balance_sheet": {...}}' | python scripts/ratio_calculator.py --stdin
```

### 2. DCF Valuation (`scripts/dcf_valuation.py`)
DCF 기업가치 평가 + 민감도 분석.

```bash
echo '{"historical_data": {...}, "assumptions": {...}}' | python scripts/dcf_valuation.py --stdin
```

### 3. Rebalancing Calculator (`scripts/rebalancing_calculator.py`)
리밸런싱 정밀 수치 계산.

```bash
echo '{"assets": [...], "target_weights": {...}}' | python scripts/rebalancing_calculator.py --stdin
```

## Principles
- 모든 스크립트는 stdin/stdout 기반 (파일 생성 금지)
- LLM이 대부분의 분석을 직접 수행, 스크립트는 보조 도구
