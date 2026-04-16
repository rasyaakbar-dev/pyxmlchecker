# pyxmlcheck

A professional Python tool to check if an HTML or XML file is well-formed XML.

> [!NOTE]
> This tool checks **well-formedness** (structural integrity) only, not schema validation. HTML files are treated as XML, which ensures they follow strict XML rules (e.g., closed tags, nested properly).

## Features

- **Detailed Error Reporting**: Unlike standard parsers that stop at the first error, this tool identifies multiple structural issues in a single pass.
- **Color-Coded Output**: High-visibility terminal output using ANSI colors (Success in Green, Errors in Red, Info in Yellow).
- **Smart DOCTYPE Handling**: Automatically substitutes standard `<!DOCTYPE html>` declarations with an XHTML transitional DOCTYPE during evaluation to handle common HTML entities (like `&nbsp;`) without modifying your original file.
- **Professional Intonation**: Clean, monotone, and professional output suitable for CI/CD pipelines or local development.

## Requirements

- Python `3.x`
- `lxml` library (`pip install lxml`)

## Installation

```bash
pip install lxml
```

## Usage

```bash
python xml_checker.py <filename>
```

### Example Failure Output

```text
Testing for well-formedness: test/01_bad.xml ...

Error: Found 2 error(s) in test/01_bad.xml.
  1. Line 10, Column 8: Opening and ending tag mismatch: author line 9 and book
  2. Line 10, Column 8: Premature end of data in tag book line 7

=======================================
Disclaimer: This program replaced file 'test/01_bad.xml's
<!DOCTYPE ...> line with a special html5
DOCTYPE line while evaluating. The original
file has not been changed. It's possible
this program might be inaccurate if the
original file had a non-html5 DOCTYPE line.
=======================================
```

## License

Distributed under the **MIT** License. See [LICENSE](LICENSE) for details.
