import argparse
import sys
from core import NovaCodeCore, update_project

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('command', nargs='?')
    args = parser.parse_args()

    if args.update:
        update_project()
        sys.exit(0)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    core = NovaCodeCore(offline=args.offline)

    # placeholder handling
    if args.command == 'models':
        print("models: placeholder for model command")
    elif args.command == 'chat':
        print("chat: placeholder for chat command")
    else:
        print(f'unknown command: {args.command}')

if __name__ == '__main__':
    main()