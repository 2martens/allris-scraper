import argparse

from twomartens.allrisscraper import internal
from twomartens.allrisscraper import public


def main():
    parser = argparse.ArgumentParser(description="Scrape the ALLRis website")
    subparsers = parser.add_subparsers(help="sub-command help", required=True)
    oparl_parser = subparsers.add_parser("oparl", help="scrapes the public website")
    oparl_parser.add_argument("--include-organizations", action="store_true", dest="include_organizations")
    oparl_parser.add_argument("--include-meetings", action="store_true", dest="include_meetings")
    oparl_parser.set_defaults(function=public.main)
    internal_parser = subparsers.add_parser("internal", help="scrapes the internal website")
    internal_parser.set_defaults(function=internal.main)
    
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
