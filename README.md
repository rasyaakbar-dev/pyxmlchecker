# pyxmlcheck

## Description

**[`pyxmlcheck`](pyxmlcheck)** is a developer-centric CLI tool designed to validate the well-formedness of XML and HTML files. Unlike standard parsers that halt at the first encountered error, `pyxmlcheck` leverages `lxml`'s recovery mode to scan the entire document, reporting all structural issues (e.g., mismatched or unclosed tags) in a single pass.

A key feature of this tool is its intelligent DOCTYPE handling. Many HTML files contain entities (like `&nbsp;`, `&copy;`) that standard XML parsers fail to recognize, leading to false-positive errors. `pyxmlcheck` solves this by seamlessly injecting a custom XHTML DOCTYPE with these entity definitions directly into the in-memory string before parsing, without mutating the original file or altering the reported error line numbers.

## Requirements

- Python 3.6+
- `lxml`

## Installation

Clone the repository and install the required dependency using `pip`:

```bash
# Clone the repository
git clone https://github.com/rasyaakbar-dev/pyxmlchecker.git
cd pyxmlchecker

# Install requirements
pip install lxml
```

## Usage

Run the script directly via Python, passing the target file as an argument:

```bash
python xml_checker.py <filename>
```

### Example

```bash
$ python3 xml_checker.py index.html

Testing for well-formedness: index.html ...

Error: Found 2 error(s) in index.html.
  1. Line 45, Column 8: Opening and ending tag mismatch: p line 42 and div
  2. Line 89, Column 1: Premature end of data in tag html line 1
```

## How It Works

From a technical standpoint, `pyxmlcheck` performs the following workflow:

1. **File Ingestion**: Reads the target file into a UTF-8 encoded string.
2. **Intelligent DOCTYPE Substitution**:
   - Uses a regular expression (`r'<!DOCTYPE[^>]*>'`) to locate any existing DOCTYPE declaration.
   - If found, it is replaced with a comprehensive XHTML DOCTYPE containing common HTML entity definitions.
   - **Line Number Preservation**: Crucially, the script counts the newlines in the original DOCTYPE and appends them to the injected single-line DOCTYPE. This guarantees that the line numbers reported by the parser perfectly match the original file.
   - If no DOCTYPE is found, it prepends the custom DOCTYPE on the very first line without a trailing newline.
3. **Parsing and Error Recovery**: Passes the modified string to `lxml.etree.XMLParser(recover=True)`. This allows the parser to construct as much of the DOM as possible while accumulating an `error_log` of all structural violations.
4. **Reporting**: Iterates through the `error_log` and outputs color-coded, exact line-and-column error messages to the console.

## Contributing

Contributions are welcome! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

## Security

If you discover a security vulnerability, please follow the instructions in [`SECURITY.md`](SECURITY.md).

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
