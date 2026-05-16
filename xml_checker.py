import argparse
import re
import sys
import xml.parsers.expat

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_injected_xhtml_doctype() -> str:
    """Returns a single-line DOCTYPE string that defines common HTML entities for XML parsing."""
    return '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" [<!ENTITY nbsp \' \'><!ENTITY reg \'®\'><!ENTITY copy \'©\'><!ENTITY trade \'™\'>]>'


def print_disclaimer(fname: str) -> None:
    """Prints a disclaimer explaining the DOCTYPE substitution."""
    print(f"\n{YELLOW}=======================================")
    print(f"Disclaimer: This program replaced file '{fname}'s")
    print("<!DOCTYPE ...> line with a special html5")
    print("DOCTYPE line while evaluating. The original")
    print("file has not been changed. It's possible")
    print("this program might be inaccurate if the")
    print("original file had a non-html5 DOCTYPE line.")
    print(f"======================================={RESET}\n")


def read_and_inject_doctype(fname: str) -> str:
    """Reads the file and replaces or injects HTML DOCTYPE with XHTML DOCTYPE without altering line numbers."""
    try:
        with open(fname, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"{RED}Error: File '{fname}' not found.{RESET}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"{RED}Error: Could not read file '{fname}': {e}{RESET}",
              file=sys.stderr)
        sys.exit(1)

    xhtml_doctype = get_injected_xhtml_doctype()
    match = re.search(r'<!DOCTYPE[^>]*>', content, re.IGNORECASE)

    if match:
        original_doctype = match.group(0)
        newlines_to_keep = '\n' * original_doctype.count('\n')
        return content[:match.start()] + xhtml_doctype + newlines_to_keep + content[match.end():]
    else:
        # Insert DOCTYPE after any XML declaration (<?xml ... ?>)
        xml_decl = re.search(r'<\?xml[^?]*\?>', content, re.IGNORECASE)
        if xml_decl:
            insert_pos = xml_decl.end()
            return content[:insert_pos] + '\n' + xhtml_doctype + content[insert_pos:]
        return xhtml_doctype + content


def _collect_errors(xml_string: str) -> list[dict[str, object]]:
    """Collect multiple XML well-formedness errors using incremental expat re-parsing.

    On each error, records it, then creates a fresh parser and feeds the
    remaining content (from after the error line) to discover additional errors.
    A DOCTYPE header is re-injected for entity resolution on each re-parse.
    """
    lines = xml_string.split('\n')
    total_lines = len(lines)
    errors: list[dict[str, object]] = []
    line_offset = 0  # how many original lines we've consumed from the top
    doctype = get_injected_xhtml_doctype()

    # Current content to parse — initially the full (already DOCTYPE-injected) string
    current_bytes = xml_string.encode('utf-8')

    while current_bytes:
        parser = xml.parsers.expat.ParserCreate()
        try:
            parser.Parse(current_bytes, True)
            break  # remaining content is well-formed
        except xml.parsers.expat.ExpatError as e:
            # Compute the actual line number in the original document.
            # When re-parsing, we prepend a single-line DOCTYPE, so the
            # content starts at reported line 2. On the first pass the
            # string already has its DOCTYPE so no adjustment is needed.
            if line_offset == 0:
                actual_line = e.lineno
            else:
                # We prepended 1 DOCTYPE line, so content starts at line 2
                actual_line = line_offset + (e.lineno - 1)

            errors.append({
                'line': actual_line,
                'column': e.offset,
                'message': xml.parsers.expat.ErrorString(e.code),
            })

            # Advance past the error line
            if line_offset == 0:
                error_end = e.lineno
            else:
                error_end = line_offset + (e.lineno - 1)

            if error_end >= total_lines:
                break  # no more content

            line_offset = error_end
            remaining_lines = lines[line_offset:]
            remaining_str = doctype + '\n' + '\n'.join(remaining_lines)
            current_bytes = remaining_str.encode('utf-8')

    return errors


def validate_xml_well_formedness(fname: str) -> None:
    """Checks if the provided file is well-formed XML and reports every error if not."""
    print(f"\nTesting for well-formedness: {fname} ...\n")

    xml_string = read_and_inject_doctype(fname)
    errors = _collect_errors(xml_string)

    if errors:
        # Deduplicate errors by (line, column, message)
        seen = set()
        unique_errors: list[dict[str, object]] = []
        for e in errors:
            key = (e['line'], e['column'], e['message'])
            if key not in seen:
                seen.add(key)
                unique_errors.append(e)

        print(f"{RED}Error: Found {len(unique_errors)} error(s) in {fname}.{RESET}")
        for i, error in enumerate(unique_errors, 1):
            print(
                f"  {i}. Line {error['line']}, Column {error['column']}: {error['message']}")
        print_disclaimer(fname)
        sys.exit(1)
    else:
        print(f"{GREEN}Success: {fname} is well-formed XML.{RESET}")
        print_disclaimer(fname)


def main() -> None:
    """Main entry point for the XML checker."""
    parser = argparse.ArgumentParser(
        description="Check if an HTML/XML file is well-formed XML by ensuring proper tags."
    )
    parser.add_argument("filename", help="The path to the file to check")

    args = parser.parse_args()
    validate_xml_well_formedness(args.filename)


if __name__ == "__main__":
    main()
