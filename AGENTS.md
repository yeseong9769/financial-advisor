# AGENTS.md — Financial Advisor

## Project Type

 개인 금융 비서 AI 에이전트. Investment Portfolio Analysis Agent.
 OpenCode multi-agent system — no build, no tests, no package manager.
 Just agent definitions, Python analysis scripts, and an MCP config.

## Project Purpose

 개인 투자자를 위한 AI 기반 금융 비서.
 사용자의 투자 포트폴리오를 분석하고, 시장 데이터를 조회하며, 자산 재배분(리밸런싱) 추천을 제공합니다.
 Excel/CSV 파일로 포트폴리오 데이터를 입력받고, Alpha Vantage MCP로 시장 데이터를 조회합니다.

## Entry Points

- **Primary agent**: `agents/finance-advisor.md` — orchestrates other agents, handles user-facing questions
- **Subagents**: `agents/portfolio-analyzer.md`, `agents/market-researcher.md`, `agents/rebalancing-engine.md`, `agents/stock-analyzer.md`
- **Skill**: `skills/financial-analyst/SKILL.md` — financial modeling toolkit with Python scripts
- **Config**: `opencode.json.example` — Alpha Vantage MCP 설정 템플릿 (사용자 환경에 맞게 복사해서 사용)

## Data Input Conventions

- **파일 경로**: 특정 경로나 파일명을 지정하지 않음. 사용자가 대화 중 전달하는 파일을 사용
- **지원 형식**: Excel (.xlsx, .xls), CSV (.csv)
- **입력 방식**: 사용자로부터 파일 경로를 대화형으로 입력받음
- 파일 전달 시: "포트폴리오 파일이 여기 있습니다: /path/to/file.xlsx" 와 같이 전달
- **작업 디렉토리**: `{WORKSPACE}` (opencode 실행 위치 기준)

## API Key Management

### Alpha Vantage API Key

 Alpha Vantage API 키는 **Shell 환경변수**로 관리합니다.

**설정 방법**:

1. `.bashrc` 또는 `.zshrc`에 환경변수 등록:
   ```bash
   export ALPHAVANTAGE_API_KEY="your_api_key_here"
   ```

2. `opencode.json.example`을 `opencode.json`으로 복사:
   ```bash
   cp opencode.json.example opencode.json
   ```

**MCP 설정** (`opencode.json.example` 참고):
```json
{
  "mcp": {
    "alphavantage": {
      "type": "remote",
      "url": "https://mcp.alphavantage.co/mcp?apikey={env:ALPHAVANTAGE_API_KEY}"
    }
  }
}
```

**주의**:
- API 키는 `.bashrc` 또는 `.zshrc`에 등록하여 영구 설정 권장
- `opencode.json`은 Git에 포함되지 않습니다. `opencode.json.example`을 템플릿으로 사용하세요.
- `opencode.json`에는 API 키를 하드코딩하지 마세요

### Alpha Vantage MCP Usage

 Alpha Vantage MCP는 **반드시 `alphavantage*` 툴을 직접 호출**해야 합니다.
 이는 `tools:` front matter에 `alphavantage*: true`로 등록되어 있습니다.
 서버는 원격이며 설치하지 마세요.

**사용 예시**:
```
TIME_SERIES_DAILY with {"symbol": "AAPL", "outputsize": "compact"}
```

 Alpha Vantage MCP 툴 목록 확인:
 1. `alphavantage_TOOL_LIST` — 사용 가능한 툴 이름/설명 조회
 2. `alphavantage_TOOL_GET(tool_name)` — 특정 툴의 파라미터 스키마 조회
 3. `alphavantage_TOOL_CALL(tool_name, arguments)` — 툴 실행

## Skills

Only one skill: `financial-analyst`. Load with `skill(name="financial-analyst")`.

It bundles 5 Python scripts in `skills/financial-analyst/scripts/`:
- `ratio_calculator.py` — 재무 비율 계산
- `dcf_valuation.py` — DCF Valuation
- `budget_variance_analyzer.py` — 예산 분기 분석
- `forecast_builder.py` — 매출/현금흐름 예측
- `rebalancing_calculator.py` — 포트폴리오 리밸런싱 계산

## File & Output Conventions

- **Default: print to screen only.** Do not write intermediate files to disk.
- **PDF only on explicit request** (keywords: "PDF로", "PDF 생성", "리포트 파일로", "인쇄용").
- PDF workflow: generate in `/tmp/`, convert with `pandoc` + `xelatex`, move to current directory, clean up `/tmp/`.
- Temporary data: keep in memory or `/tmp/`, delete after use.

## When to Delegate

Follow the agent routing defined in the primary agent:
- Portfolio stats → `@portfolio-analyzer`
- Market data/research → `@market-researcher`
- Rebalancing → `@rebalancing-engine`
- Individual stock deep-dive or PDF report → `@stock-analyzer`

## Language

User-facing output is **Korean** for most agents.
 internal reasoning and analysis summaries can remain in English unless the user context is Korean.
