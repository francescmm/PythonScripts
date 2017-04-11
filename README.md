# PythonScripts

In this repository you can find general scripts I've made just to learn Python.

1. **bopi-checker**: This script lets us know if a text is found in today's BOPI (Spain). The BOPI is the official bulletin for the industrial property. Is the document that communicates the administrative acts of the different types of industrial properties.
  Usage: bopi-checker.py -d <startDate format dd-MM-yyyy> -w <words separated by comma> -r
  The usage of the date is an option. If any date is provided it executes the current day.
  If the user sets the '-r' param, it means that from the date provided, the script will download all BOPI, associated images and if words are provided, it will look at the BOPI for these words.
