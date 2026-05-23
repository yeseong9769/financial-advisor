#!/usr/bin/env python3
"""
HTML to PDF converter using WeasyPrint.

Usage:
    echo '{"html": "<h1>Hello</h1>", "output_path": "out.pdf"}' | python html_to_pdf.py --stdin
    python html_to_pdf.py --html "<h1>Hello</h1>" --output out.pdf
"""

import argparse, json, sys

try:
    from weasyprint import HTML as WeasyHTML
except ImportError:
    print("Error: weasyprint is required. Run: pip install weasyprint", file=sys.stderr)
    sys.exit(1)


def convert(html: str, output_path: str) -> None:
    """Render HTML string to PDF file via WeasyPrint."""
    WeasyHTML(string=html).write_pdf(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HTML to PDF")
    parser.add_argument("--html", help="HTML content")
    parser.add_argument("--output", "-o", help="Output PDF path")
    parser.add_argument("--stdin", action="store_true", help="Read params from stdin as JSON")

    args = parser.parse_args()

    if args.stdin:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)
        html = data.get("html", args.html)
        output_path = data.get("output_path", args.output)
    else:
        html = args.html
        output_path = args.output

    if not html:
        print("Error: 'html' is required", file=sys.stderr)
        sys.exit(1)
    if not output_path:
        print("Error: 'output_path' is required", file=sys.stderr)
        sys.exit(1)

    convert(html, output_path)
    print(f"OK: {output_path}")


if __name__ == "__main__":
    main()