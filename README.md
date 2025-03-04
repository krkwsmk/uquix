# UQUIX -> Unexpected Creepy Cruel Requests  
*Pronounced "You-kwix"*

**Ultimate Request Manipulation Toolkit for Uncovering Missed & Hidden Vulnerabilities**  
*Automate Unlimited Complex Header Attacks - Find What Others Miss*

![Logo](UQUIX_logo.png)

UQUIX is out-of-the-box CLI-based ultra-fast Python advanced tool designed to help bug hunters by automating complex header manipulation scenarios that are impossible to perform manually at scale. UQUIX also comes with lightweight & ultra-fast subdomain enumeration mode via DNS brute-force to help identify additional attack surfaces. UQUIX solves seven critical problems:

1. **No Limitation**: Test any vulnerability through complete header/payload manipulating control.
2. **Time Efficiency**: Execute thousands header/payload variations per target.
3. **Protocol Depth**: Discover vulnerabilities hidden in obscure header combinations.
4. **Human Limitation**: Automate tedious testing that manual testers skip.
5. **Custom Analysis**: Define your own vulnerability detection logic.
6. **Out-of-the-box Power**: Manipulate headers/values/payloads/positions/repetitions/... instantly.
7. **Multi-Vector Attacks**: Test multiple attack vectors per request.

## Overview

Traditional vulnerability testing by trying every possible method/header/payload variation using tools like Burp Repeater can be extremely time-consuming. UQUIX streamlines this process perfectly with out-of-the-box power by allowing you to:

- **Full Request Manipulating:** Manipulate every aspect of HTTPs requests (methods, headers, payloads, timeouts, redirects, etc...).
- **Cruel Headers:** Create complex header combinations using your own JSON rules.
- **Intelligent Randomization:** Randomize headers/values/payloads/positions/repetitions/... using your own JSON rules.
- **Out-of-the-box Power**: manipulate headers/values/payloads/positions/repetitions/... using your own JSON rules.
- **Comprehensive Testing**: Probe servers with every possible scenario to uncover hidden vulnerabilities.
- **Smart Analysis:** Detect vulnerabilities using custom AND/OR response analysis logic.
- **Real-Time Analytics:** Show a live progress tracking with detailed request/response analytics.
- **Discover Missed Vulnerabilities**: Find error leaks, info disclosure, parsing flaws, dos, overflow, bypasses, smuggling and more much that manual tests miss.
- **Advanced Automation**: Test complex header permutations no human would manually attempt.
- **Detailed Output**: UQUIX will give you a detailed output so you don't miss any information about requests/responses.
- **Ultra-Speed**: UQUIX is fully asynchronous so don't worry about the speed.
- **Ultra-Fast Subdomain Discovery:** Perform lightweight & ultra-fast subdomain enumeration to identify additional attack surfaces.

UQUIX has advanced fully customizable features ensure that you won’t miss any potential bugs/vulns, increasing your chances to uncover hidden vulnerabilities based on server behavior.

## Why UQUIX?

| Manual Testing Limitations          | UQUIX Advantages                        |
|-------------------------------------|-----------------------------------------|
| Time-consuming configs              | Out-of-the-box attack profiles          |
| Limited header combinations         | Unlimited permutations/second           |
| Missed edge cases                   | Automated anomaly detection             |
| Single-vector attack                | Simultaneous multi-vulnerability scans  |
| Partial protocol coverage           | Full HTTPs stack manipulation           |

## Configurations

1. **Number of Requests Variations Per URL `--random-headers`**:
    *`--random-headers` is the number of times to send the same request but with random headers variations based on headers rules file, and with random payload~
    from payloads file if `--random-payload`. The default value for `--random-headers` is `3`.
    NOTE: If `--random-headers` is `0`, so only headers that has `"isalways": true` rule will be sent.

2. **Headers:**
    `configs/headers_rules.json` defines how UQUIX generates headers per request. Each header has rules for randomization, repetition and positioning.
    *Read `docs/headers_rules_guide.md` to learn how to modify your own headers and rules. Learn to use UQUIX efficiently ;)

3. **Payloads:**
    `configs/random_payloads.txt` by default contain payloads for HTTP Smuggling, each payload separated by '\n===\n'.
    UQUIX will pick one random payload per request if `--random-payload` and current HTTPs method in `--data-methods`.
    *Read `docs/random_payloads_guide.md` to learn how to customize your own payloads. Learn to use UQUIX efficiently ;)

4. **Analyzing:**
    *Read `docs/analysis_guide.md` to learn how to customize your own vulnerabilities detection logics. Learn to use UQUIX efficiently ;)


## Usage Examples
    
    **To use request manipulator mode use `Response-Xplore`:**
        - *Run with default configs:*
            - `uquix response-xplore urls.txt`
        - *Example of detailed configs:*
            - `uquix response-xplore urls.txt --add-http --add-https --concurrent-requests 1000 --methods all --data-methods post,put --random-agents --random-headers 10 --headers-rules-file 'my_hdrs_rules.json' --random-payload --payloads-file 'my_plds.txt' --ignore-cookies --no-ssl --dns-servers-file resolvers.txt --enable-rotate --dns-retries 0 --req-retries 2 --retries-delay 2 --exp-backoff --dns-timeout 0.5 --req-timeout 6 --ttl-dns-cache 5 --max-redirects-http 3 --max-redirects-https 5 --final-url --less-400 --min-content 50 --max-content 10000 --no-title --analyze-by '(RES_HDRS and RES_HDRS_SIZE) or STATUS or CONTENT or DURATION' --output-file 'output/tested_urls.txt' --output-sorted 'output/sorted_tested_urls.txt' --output-analyze 'output/detected_vulns.txt' --html-dir 'output/html_tested_urls' --no-history`
    
    **To use subdomain enumeration via DNS brute-force mode use `Subs-Xplore`:**
        - *Run with default configs on single target:*
            - `uquix subs-xplore subslist.txt --target-domain example.com`
        - *Run with default configs on mutli targets:*
            - `uquix subs-xplore subslist.txt --target-domains target_domains.txt`
        - *Example of detailed configs:*
            - `uquix subs-xplore subslist.txt --target-domains target_domains.txt --concurrent-queries 2000 --show-records --timeout 2 --retries 0 --enable-rotate --dns-servers-file resolvers.txt --output-file newsubs_with_A_CNAME.txt --silence`

## Example Screenshot

![Logo](UQUIX_example.png)

## Requirements
    
    **[Python 3.9+]

## Installation

**Clone & Install:**

   ```bash

    git clone https://github.com/0Arafa/uquix.git && cd uquix && pip install -e . && uquix --help

   ```

## Support Me <3

**If you liked the project and you want to encourage me, you can support me through:**
- BTC: bc1q3yp6hkx570fl3sp6undnl28dvvg4scwyz823u0
- ETH: 0xbfE929a54576bA503c9076BA3B813afb82fa4b04
- USDT (ERC-20): 0xbfE929a54576bA503c9076BA3B813afb82fa4b04
- USDT (BEP-20): 0xbfE929a54576bA503c9076BA3B813afb82fa4b04
- BNB (BEP-20): 0xbfE929a54576bA503c9076BA3B813afb82fa4b04
- USDT (TRC-20): TBa5yB3bLyfZSgxeD1Croue6na2RGcurcY
- TRX: TBa5yB3bLyfZSgxeD1Croue6na2RGcurcY
- LTC: LTwiigKAUPmTFJZJ6R3qcZagVh4dgqRjxM

################################################################
# By: Abd Almoen Arafa (0.1Arafa)                              #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################
