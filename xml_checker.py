import argparse
import re
import sys
from lxml import etree
from pathlib import Path

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_xhtml_doctype_prepender() -> str:
    """Returns a DOCTYPE string that defines common HTML entities for XML parsing."""
    return (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
        '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" [\n'
        '<!ENTITY nbsp \' \'>\n'
        '<!ENTITY reg  \'®\'>\n'
        '<!ENTITY copy \'©\'>\n'
        '<!ENTITY trade \'™\'>\n'
        ']>\n'
    )


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


def abort_on_crazy_doctype(doctype_line: str) -> None:
    """Aborts the script with an error message when an invalid DOCTYPE is found."""
    print(f"\n{RED}Error: This file's doctype line is invalid: {doctype_line.strip()}")
    print("The XML Checker program works only on doctypes that:")
    print('    Begin with "<!doctype", case irrelevant')
    print('    Have exactly one ">" character')
    print('    That ">" character is at the end')
    print("This error might not indicate mal-formed XML,")
    print("It might just mean that the XML Checker program")
    print("can't be run on this file with its current")
    print(f"<!DOCTYPE line.{RESET}\n")
    sys.exit(1)


def is_eligible_line(line: str) -> bool:
    """Checks if the line should be included in the modified XML string."""
    stripped_line = line.strip()
    
    # If it's not an HTML doctype, it's eligible to be included
    if not re.match(r'<!doctype\s+html', stripped_line, re.IGNORECASE):
        return True
    
    # It is an HTML doctype. We validate it before skipping.
    if stripped_line.count('>') != 1 or not stripped_line.endswith('>'):
        abort_on_crazy_doctype(line)
        
    # Skip the valid HTML doctype line
    return False


def read_and_prepare_xml(fname: str) -> str:
    """Reads the file and replaces HTML DOCTYPE with XHTML DOCTYPE."""
    try:
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"{RED}Error: File '{fname}' not found.{RESET}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"{RED}Error: Could not read file '{fname}': {e}{RESET}", file=sys.stderr)
        sys.exit(1)
    
    valid_lines = [line for line in lines if is_eligible_line(line)]
    return get_xhtml_doctype_prepender() + "".join(valid_lines)


def check_xml_compliance(fname: str) -> None:
    """Checks if the provided file is well-formed XML and reports every error if not."""
    print(f"\nTesting for well-formedness: {fname} ...\n")
    
    xml_string = read_and_prepare_xml(fname)
    
    try:
        parser = etree.XMLParser(recover=True)
        etree.fromstring(xml_string.encode('utf-8'), parser)
        
        errors = parser.error_log
        if errors:
            print(f"{RED}Error: Found {len(errors)} error(s) in {fname}.{RESET}")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. Line {error.line}, Column {error.column}: {error.message}")
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
    check_xml_compliance(args.filename)


if __name__ == "__main__":
    main()
