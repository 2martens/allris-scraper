# ALLRIS Scraper

![Apache Licence 2.0](https://img.shields.io/pypi/l/twomartens.allrisscraper)
![Supports Python 3.7 and 3.8](https://img.shields.io/pypi/pyversions/twomartens.allrisscraper)
![version 0.1.2](https://img.shields.io/pypi/v/twomartens.allrisscraper)

This scraper requires your username and password and performs the following tasks for you:

- login
- download of all agendas and motions related to upcoming meetings of committees and plenary sessions
  - Only considers meetings where you already have been invited formally through ALLRIS.

**IMPORTANT:** As of now only the Hamburg district of Eimsbüttel is supported.

## Requirements

- Python 3.7+
- Firefox installed
- [geckodriver binary][0] in PATH

[0]: https://github.com/mozilla/geckodriver/releases

## Initial setup
1. Install ALLRIS scraper ``pip install twomartens.allrisscraper`` (you need Python 3.7+)
2. Run ALLRIS scraper a first time ``tm-allrisscraper`` (creates config ini in your current working directory)
3. Fill out the config file with your login credentials and an absolute path on your system to store PDFs of files

## Usage after initial setup

Run ALLRIS scraper: ``tm-allrisscraper`` (takes a few seconds to finish)

In the specified location for download you will find the following structure:

- ``YYYY-MM-DD_Abbreviation of committee or plenary session/`` (one directory for each meeting)
- files inside the directory 
  ``Einladung.pdf`` (contains invitation), ``Mappe.pdf`` (contains all motions in one document), and ``Tagesordnung.pdf`` (agenda)
