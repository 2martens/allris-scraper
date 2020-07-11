# -*- coding: utf-8 -*-

#   Copyright 2020 Jim Martens
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import calendar

ABBREVIATIONS = {
    "Altona":        {
        "Haupt": "HA",
    },
    "Bergedorf":     {
        "Haupt": "HA",
    },
    "Eimsbüttel":    {
        "Haupt":      "HA",
        "Kerngebiet": "KGA",
        "RaLNS":      "RaLoNiS",
        "HKS":        "HaKuS",
        "GNUVWD":     "GNUVWDi",
        "SAIBGGSG":   "SR",
        "AS":         "StaPla",
        "AU":         "Uni"
    },
    "Hamburg-Mitte": {
        "Haupt":         "HA",
        "Stadtplanungs": "StaPla"
    },
    "Hamburg-Nord":  {
        "Haupt": "HA",
    },
    "Harburg":       {
        "Haupt": "HA",
    },
    "Wandsbek":      {
        "Haupt": "HA",
    }
}

BASE_LINKS = {
    "Altona":        "https://sitzungsdienst-altona.hamburg.de/ri",
    "Bergedorf":     "https://sitzungsdienst-bergedorf.hamburg.de/ri",
    "Eimsbüttel":    "https://sitzungsdienst-eimsbuettel.hamburg.de/ri",
    "Hamburg-Mitte": "https://sitzungsdienst-hamburg-mitte.hamburg.de/ri",
    "Hamburg-Nord":  "https://sitzungsdienst-hamburg-nord.hamburg.de/ri",
    "Harburg":       "https://sitzungsdienst-harburg.hamburg.de/ri",
    "Wandsbek":      "https://sitzungsdienst-wandsbek.hamburg.de/ri",
}

PUBLIC_BASE_LINKS = {
    "Altona":        "https://sitzungsdienst-altona.hamburg.de/bi",
    "Bergedorf":     "https://sitzungsdienst-bergedorf.hamburg.de/bi",
    "Eimsbüttel":    "https://sitzungsdienst-eimsbuettel.hamburg.de/bi",
    "Hamburg-Mitte": "https://sitzungsdienst-hamburg-mitte.hamburg.de/bi",
    "Hamburg-Nord":  "https://sitzungsdienst-hamburg-nord.hamburg.de/bi",
    "Harburg":       "https://sitzungsdienst-harburg.hamburg.de/bi",
    "Wandsbek":      "https://sitzungsdienst-wandsbek.hamburg.de/bi",
}

ALLRIS_LOGIN: str = "https://2martens.de/allris-eimsbüttel"
ALLRIS_OPEN: str = "https://2martens.de/bezirk-eimsbüttel"
CONFIG_PROPS = {
    "Default": {
        "district":      "Eimsbüttel",
        "username":      "max.mustermann@eimsbuettel.de",
        "password":      "SehrSicheresPasswort",
        "pdflocation":   "/Pfad/zum/Ablegen/der/PDFs/",
        "jsonLocation":  "/Pfad/zum/Ablegen/der/jsons/",
        "firefoxBinary": "/Pfad/zur/firefox.exe",
        "geckodriver":   "/Pfad/zum/geckodriver"
    }
}

MONTHS = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}
