#!/usr/bin/env python3
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Input file path')
    parser.add_argument('--phrase', required=True, help='Phrase to search for')
    parser.add_argument('--ignore-case', action='store_true', help='Case-insensitive search')
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print("FILE_NOT_FOUND")
        return 2

    found = False
    line_number = 0
    search_phrase = args.phrase
    if args.ignore_case:
        search_phrase = search_phrase.lower()

    with open(args.file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line_number += 1
            stripped_line = line.rstrip('\n')
            check_line = stripped_line.lower() if args.ignore_case else stripped_line
            if search_phrase in check_line:
                print(f"LINE {line_number}: {stripped_line}")
                found = True

    if not found:
        print("NOT_FOUND")
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
