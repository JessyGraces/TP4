"""
Simple Unicode Encoding Tool
"""

import sys
import argparse

UTF8 = 'utf-8'
UTF16 = 'utf-16'
UTF32 = 'utf-32'
UTF16_LE = 'utf-16LE'
UTF16_BE = 'utf-16BE'
UTF32_LE = 'utf-32LE'
UTF32_BE = 'utf-32BE'

VALID_ENCODINGS = [UTF8, UTF16, UTF32, UTF16_LE, UTF16_BE, UTF32_LE, UTF32_BE]


def detect_bom(filepath):
    """Detect encoding from BOM (Byte Order Mark)"""
    with open(filepath, 'rb') as f:
        bom = f.read(4)

    if bom.startswith(b'\xff\xfe\x00\x00'):
        return UTF32_LE
    elif bom.startswith(b'\x00\x00\xfe\xff'):
        return UTF32_BE
    elif bom.startswith(b'\xff\xfe'):
        return UTF16_LE
    elif bom.startswith(b'\xfe\xff'):
        return UTF16_BE

    return UTF8


def detect(filepath):
    """Detect file encoding"""
    bom_encoding = detect_bom(filepath)
    return bom_encoding


def exec_convert(input_file, output_file, from_encoding: str, to_encoding: str):
    from_encoding = from_encoding.strip().upper()
    to_encoding = to_encoding.strip().upper()

    with open(input_file, 'r', encoding=from_encoding) as f:
        content = f.read()
        with open(output_file, 'w', encoding=to_encoding) as out:
            out.write(content)


def convert(input_file, output_file, from_encoding, to_encoding):
    """Convert file between encodings"""
    try:
        exec_convert(input_file, output_file, from_encoding, to_encoding)
    except Exception as e:
        return False, f"Error: {e}"

    return True, f"Converted {input_file} from {from_encoding} to {to_encoding}"


def main():
    parser = argparse.ArgumentParser(
        description='Simple Unicode Encoding Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  encoder detect file.txt
  encoder convert input.txt output.txt -f utf-8 -t utf-16
  encoder list
'''
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect file encoding')
    detect_parser.add_argument('file', help='File to check')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert encoding')
    convert_parser.add_argument('input', help='Input file')
    convert_parser.add_argument('output', help='Output file')
    convert_parser.add_argument('-f', '--from', dest='from_enc', default='utf-8',
                                help='Source encoding (default: utf-8)')
    convert_parser.add_argument('-t', '--to', dest='to_enc', default='utf-8',
                                help='Target encoding (default: utf-8)')

    # List command
    list_parser = subparsers.add_parser('list', help='List supported encodings')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == 'detect':
        encoding = detect(args.file)
        print(encoding)
        return 0

    if args.command == 'convert':
        success, msg = convert(
            args.input,
            args.output,
            args.from_enc,
            args.to_enc
        )
        print(msg, file=sys.stderr if not success else sys.stdout)
        return 0 if success else 1

    if args.command == 'list':
        print("Supported encodings:")
        for enc in VALID_ENCODINGS:
            print(f"  {enc}")
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
