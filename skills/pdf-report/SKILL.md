---
name: pdf-report
description: Generate PDF reports from HTML with Korean font support. Use when the user asks for a PDF report, PDF, or to generate a document from analysis results.
license: MIT
compatibility: opencode
metadata:
  audience: financial advisor
  category: document-generation
---

# PDF Report Generator

## Overview

Converts HTML reports to PDF using WeasyPrint. Supports full CSS styling including Korean fonts.

## When to Use

- User says "PDF", "리포트", "리포트 만들어줘", "보고서 PDF로"
- Deep mode analysis that needs a deliverable file
- Any request to save analysis results as a PDF document

## Usage

```bash
echo '{"html": "<!DOCTYPE html>...", "output_path": "report.pdf"}' | python skills/pdf-report/scripts/html_to_pdf.py --stdin
```

The agent composes HTML freely — no fixed template. Just include Korean font in CSS:

```html
<style>body { font-family: 'Noto Sans CJK KR', sans-serif; }</style>
```

## Tips

- Use `<div style="page-break-before: always;"></div>` for page breaks
- Inline CSS only (no external files)
- Test with `--stdin` first, pipe HTML directly