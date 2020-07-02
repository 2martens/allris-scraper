import configparser

from twomartens.allrisscraper.definitions import CONFIG_PROPS


def initialize_config(config_file: str) -> bool:
    try:
        with open(config_file, "r"):
            # if we reach this branch then the file exists and everything is fine
            return True
    except FileNotFoundError:
        with open(config_file, "w") as file:
            parser = configparser.ConfigParser()
            for section in CONFIG_PROPS:
                parser[section] = {}
                for option in CONFIG_PROPS[section]:
                    default = CONFIG_PROPS[section][option]
                    parser[section][option] = default

            parser.write(file)
            return False
