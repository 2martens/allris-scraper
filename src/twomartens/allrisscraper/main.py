import argparse

from twomartens.allrisscraper import internal
from twomartens.allrisscraper import public


def main():
    parser = argparse.ArgumentParser(description="Scrape the ALLRis website")
    parser.add_argument("mode", choices=["oparl", "internal"], help="which mode should be used")
    args = parser.parse_args()
    
    if args.mode == "oparl":
        public.main()
    else:
        internal.main()
