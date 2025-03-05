# UQUIX Payloads Configuration Guide

*UQUIX by default uses `uquix/configs/random_payloads.txt` to pick one random payload per request (if `--random-payload`).
*This simple guide will help you to configure your own payloads.
*Payloads in `uquix/configs/random_payloads.txt` are for http smuggling.
*You can set your own payloads file by `--payloads-file` option.
*To allow UQUIX to pick one random payload per request from `uquix/configs/random_payloads.txt` then use `--random-payload`.

### Payloads Separation

**Payloads are separated by `\n===\n`. so do NOT forget to separate each payload with `\n===\n`

### Special Syntax

**You can include a special syntax in every payload, there're two special syntax can be used:

    - `METHOD`: when you include a `METHOD` in the payload so `METHOD` will be replaced with current HTTPs request method.
    - `example.com`: when you include a `example.com` in the payload so `example.com` will be replaced with current target address (NOT the full URL)

### Payloads Specific HTTPs Method

**If you want only to include payloads in a specific requests with specific HTTPs methods then use `--data-methods`.


################################################################
- By: Abd Almoen Arafa (0.1Arafa)
- WARNING: Please ask for PERMISSIONS before testing any web server
