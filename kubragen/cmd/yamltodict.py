import argparse
import pprint
import sys

import yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yaml to dict')
    parser.add_argument('filename')
    args = parser.parse_args()

    if args.filename == '-':
        data = list(yaml.load_all(sys.stdin, Loader=yaml.FullLoader))
    else:
        with open(args.filename, 'r', encoding='utf-8') as f:
            data = list(yaml.load_all(f, Loader=yaml.FullLoader))

    if len(data) > 0:
        if len(data) > 1:
            pprint.pprint(data, sort_dicts=False)
        else:
            pprint.pprint(data[0], sort_dicts=False)
