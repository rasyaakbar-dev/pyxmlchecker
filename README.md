# pyxmlcheck

A simple Python script to check if an HTML or XML file is well-formed XML.

> This tool checks well-formedness only, not schema validation. HTML files are treated as XML, which may lead to expected failures for non-XHTML HTML

## Requirements

- Python `3.x`
- No external dependencies (_I think_)

## Usage

```bash
python xml_checker.py <filename>
```

## Features

- Evaluates well-formedness of XML using standard Python libraries.
- Safely handles and substitutes `<!DOCTYPE html>` lines for validation purposes without modifying the original file.
- Provides a clear readout of success or failure (plus reasons for parsing failures).

## License

Distributed under the **MIT** License. See [LICENSE](LICENSE) for details.
