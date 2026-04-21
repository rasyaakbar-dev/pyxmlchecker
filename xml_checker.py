import argparse
import re
import sys
from lxml import etree

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
        return xhtml_doctype + content


def validate_xml_well_formedness(fname: str) -> None:
    """Checks if the provided file is well-formed XML and reports every error if not."""
    print(f"\nTesting for well-formedness: {fname} ...\n")

    xml_string = read_and_inject_doctype(fname)

    try:
        parser = etree.XMLParser(recover=True)
        etree.fromstring(xml_string.encode('utf-8'), parser)

        errors = parser.error_log
        if errors:
            print(f"{RED}Error: Found {len(errors)} error(s) in {fname}.{RESET}")
            for i, error in enumerate(errors, 1):
                print(
                    f"  {i}. Line {error.line}, Column {error.column}: {error.message}")
            print_disclaimer(fname)
            sys.exit(1)
        else:
            print(f"{GREEN}Success: {fname} is well-formed XML.{RESET}")
            print_disclaimer(fname)
    except Exception as err:
        print(f"{RED}Error: {err}{RESET}")
        print_disclaimer(fname)
        sys.exit(1)


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
