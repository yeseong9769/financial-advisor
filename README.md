# Financial Advisor — OpenCode Multi-Agent System

개인 투자자를 위한 AI 기반 금융 비서. 포트폴리오 분석, 시장 데이터 조회, 자산 재배분(리밸런싱) 추천을 제공합니다.

## Quick Install

```bash
git clone https://github.com/yeseong9769/financial-advisor.git
cd financial-advisor
bash install.sh
```

설치 시 전역(`~/.config/opencode/`) 또는 프로젝트(`.opencode/`)를 선택할 수 있습니다.

### 전역 설치 (권장)
```bash
bash install.sh -g
```
모든 프로젝트에서 `@finance-advisor` 사용 가능.

### 프로젝트 설치
```bash
cd my-portfolio-project
bash /path/to/financial-advisor/install.sh -p
```
현재 프로젝트에서만 사용.

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- Alpha Vantage API key ([get one free](https://www.alphavantage.co/support/#api-key))
- Python 3.x

## Usage

```bash
opencode
```
```
포트폴리오 분석해줘
자산 재배분 제안해줘
AAPL 현재가 알려줘
@stock-analyzer TSLA 심층 분석해줘
```

## Features

| Task | Agent |
|------|-------|
| Portfolio statistics | `@portfolio-analyzer` |
| Market data/research | `@market-researcher` |
| Rebalancing | `@rebalancing-engine` |
| Stock deep-dive / PDF | `@stock-analyzer` |

## Architecture

```
financial-advisor/
├── install.sh              ← 설치 도구
├── AGENTS.md               ← 프로젝트 개발 규칙
├── opencode.json.example   ← MCP config template
├── requirements.txt        ← Python 의존성 (openpyxl)
├── agents/                 ← OpenCode agent 정의
│   ├── finance-advisor.md
│   ├── portfolio-analyzer.md
│   ├── market-researcher.md
│   ├── rebalancing-engine.md
│   └── stock-analyzer.md
└── skills/financial-analyst/
    ├── SKILL.md
    └── scripts/
        ├── ratio_calculator.py
        ├── dcf_valuation.py
        └── rebalancing_calculator.py
```

## License

MIT
