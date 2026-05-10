import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("FILE_NOT_FOUND")
        sys.exit(2)
    
    total_lines = len(text.splitlines())
    non_empty_lines = sum(1 for line in text.splitlines() if line.strip())
    characters = len(text)
    
    print(f"TOTAL_LINES={total_lines}")
    print(f"NON_EMPTY_LINES={non_empty_lines}")
    print(f"CHARACTERS={characters}")

if __name__ == "__main__":
    main()
