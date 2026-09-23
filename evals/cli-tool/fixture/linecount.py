import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    with open(args.file, encoding="utf-8") as f:
        print(sum(1 for _ in f))
