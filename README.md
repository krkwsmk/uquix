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

## Help Section (Available Options)

<details>
<summary><b>📚 Full Help Documentation (Click to Expand)</b></summary>

### Command
```bash
uquix --help
```

**Modes Description:**
   - Response-Xplore: *Sends Unexpected Fully Customizable Requests to Test Server Responses.
   - Subs-Xplore: *Subdomain Enumeration by Resolving Subdomains for a Domain(s) via DNS Brute-force.

**options:**
  - -h, --help            *show this help message and exit

**Basic Arguments:**
  - mode                  *Mode ['Response-Xplore', 'Subs-Xplore']. Choose only one mode.
                          Choose 'Response-Xplore' to manipulate HTTPs requests or 'Subs-Xplore' for subdomain enumeration via DNS brute-force.
  - file                  *Path to the URLs file (ex, '/path/to/urls.txt') for 'Response-Xplore' mode.
                          Path to the subdomains file (ex, '/path/to/subs.txt') for 'Subs-Xplore' mode.

**Subs-Xplore Options:**
  - --target-domain         *Target domain to resolve subdomains for, without a protocol (ex, 'example.com')
  - --target-domains-file   *Path to file name that contain target domains without a protocol to resolve subdomains for (ex, 'domains.txt')
  - --concurrent-queries    *Number of concurrent DNS queries (default: 600)
  - --show-records          *Show 'A' and 'CNAME' records of discovered subdomains (default: False)
  - --show-only-a           *Show only 'A' records of discovered subdomains (default: False)
  - --show-only-cname       *Show only 'CNAME' records of discovered subdomains (default: False)

**DNS Options:**
  - --dns-servers        *Custom DNS servers for resolving hostnames, as string comma-separated or as list (ex1, '8.8.8.8,8.8.4.4'.ex2, "['8.8.8.8', '1.1.1.1']")
  - --dns-servers-file   *Path to a file name containing custom DNS servers for resolving hostnames, one per line (ex, 'resolvers.txt')
  - --udp-port           *The UDP port to use for DNS queries (default: 53)
  - --tcp-port           *The TCP port to use for DNS queries (default: 53)
  - --flags              *Custom flags for DNS queries (default: 0)
  - --socket-sbs         *Size of the send buffer for sockets, in bytes (default: system-defined)
  - --socket-rbs         *Size of the receive buffer for sockets, in bytes (default: system-defined)
  - --enable-rotate      *Enable DNS server rotation, useful for load balancing (default: False)
  - --bind-ip-dns        *The local IP to bind for DNS queries (ex, '192.168.1.16')
  - --net-dev            *The network device (interface) to use for DNS queries (ex, 'eth0')
  - --resolvconf         *Path to a custom resolv.conf file for DNS configuration (default: '/etc/resolv.conf')

**Timeout & Connection:**
  - --timeout                  *Overall timeout for HTTPs request and timeout for DNS query, in seconds (default: 10.0)
  - --dns-timeout              *Timeout for DNS query, in seconds (ex, 5.0)
  - --req-timeout              *Overall timeout for HTTPs request, in seconds (ex, 10.0)
  - --connect-timeout          *Timeout for finding and connecting to the server, including DNS lookup and the initial TCP handshake,
                               or timeout for waiting for a free connection from the pool if pool connection limits are exceeded, in seconds (default: unlimited)
  - --sock-connect-timeout     *Timeout for TCP handshake, in seconds (default: unlimited)
  - --sock-read-timeout        *Timeout for waiting for the server to send back data, in seconds (default: unlimited)
  - --keepalive-timeout        *Timeout for idle keep-alive connections, in seconds (default: 30.0)
  - --concurrent-requests      *Number of concurrent HTTPs requests (default: 100)
  - --max-connections          *Limit the maximum number of concurrent connections, to unlimit it pass 'unlimited' (default: 100)
  - --per-host-connections     *Limit the number of connections per host (default: unlimited)
  - --no-dns-cache             *Disable DNS caching (default: False)
  - --ttl-dns-cache            *Time To Live (TTL) for DNS cache entries, in seconds (default: 10)

**Retry & Backoff:**
  - --retries                 *HTTPs request retries, and DNS query retries (default: 1)
  - --dns-retries             *DNS query retries (ex, 2)
  - --req-retries             *HTTPs request retries (ex, 3)
  - --retries-delay           *Set a delay number between retries for HTTPs requests, in seconds (default: 0.0)
  - --exp-backoff             *Exponential Backoff, wait longer after each retry for HTTPs requests, '--retries-delay' option is required (default: False)

**HTTPs Request:**
  - --random-agents           *Use random user-agent for every HTTPs request (default: False)
  - --random-headers          *Number of times to send the same request but with random headers based on headers rules file, and with random payload from payloads file if
                              '--random-payload' (default: 3)
                              NOTE: If 0, only headers that has '"isalways": true' rule will be sent
  - --headers-rules-file      *Path to JSON file name that contain headers with its rules (default: 'uquix/configs/headers_rules.json')
  - --custom-headers          *Add JSON-formatted headers (ex, '{"header1": "value1", "header2": "value2"}')
  - --file-custom-headers     *Path to file name that contain headers to add, headers must be JSON-formatted (ex, 'headers.txt')
  - --no-403headers           *Skip headers that has 'is403' rule is true (default: False)
  - --methods                 *HTTPs request methods, comma-separated (default: GET,POST,PUT,HEAD,DELETE)
  - --add-http                *Add 'http://' to all URLs (default: False)
  - --add-https               *Add 'https://' to all URLs (default: False)
  - --ports PORTS             *Ports to append to ALL URLs, comma-separated (ex, 80,443) (default: None)
  - --ports-http              *Ports to append to HTTP URLs, comma-separated (default: 80)
  - --ports-https             *Ports to append to HTTPS URLs, comma-separated (default: 443)
  - --real-url                *Show the actual request url instead of as it given from the file (default: False)
  - --final-url               *Show the final request url instead of as it given from the file, after following any redirects (default: False)
  - --params                  *Specify query parameters to append to ALL URLs, JSON-formatted (ex, '{"param1":"value1","param2":"value2"}')
  - --buffer-size             *Set the size of the read buffer, in bytes (default: 65536)
  - --disable-redirect        *Disable ALL requests to follow redirects (default: False)
  - --disable-redirect-http   *Disable only HTTP requests to follow redirects (default: False)
  - --disable-redirect-https  *Disable only HTTPS requests to follow redirects (default: False)
  - --max-redirects           *Limit the number of maximum redirects to follow for ALL requests (default: 10)
  - --max-redirects-http      *Limit the number of maximum redirects to follow for only HTTP requests (ex, 5)
  - --max-redirects-https     *Limit the number of maximum redirects to follow for only HTTPS requests (ex, 5)
  - --no-ujson                *Use JSON instead of UltraJSON (ujson) (default: False)

**Data/Payload:**
  - --random-payload     *Enable to select one random payload for each request from 'uquix/configs/random_payloads.txt' (default: False)
  - --payloads-file      *Path to file name that contain payloads, one random payload will be picked randomly for each request, payloads must separated by '\n===\n', if
                         '--random-payload' (default: 'uquix/configs/random_payloads.txt')
  - --data-methods       *Specify the request methods will include data/payload in request, comma-separated (ex, 'post,put,patch') (default: '--methods')
  - --data               *Send data/payload in the request body to ALL requests (ex, 'anykey=anyvalue&anything=anythingtoo')
  - --file-data          *Path to file name that contain data/payload to send in the request body to ALL requests (ex, '/path/to/anydata.bin')
  - --json-data          *Send JSON-formatted data/payload in the request body to ALL requests (ex, '{"key": "value", "key2": "value2"}')
  - --file-json-data     *Path to file name that contain JSON-formatted data/payload to send in the request body to ALL requests (ex, '/path/to/data.json')
  - --data-encode-type   *Specify data encoding type for ['--data', '--json-data', '--file-json-data'] (default: 'utf-8')
  - --no-data-saving     *Do NOT save requests data/payload to '--output-file' (default: False)

**Proxy & Binding:**
  - --proxy              *Use a proxy server for HTTPs requests (ex, 'http://user:pass@127.0.0.1:8080')
  - --socks-proxy        *Use a SOCKS proxy server for HTTPs requests (ex, 'socks5://user:pass@127.0.0.1:9050')
  - --route-socks-first  *If both proxies are used, then route requests through SOCKS-PROXY first (default: False)
  - --no-rdns            *Do NOT resolve DNS through SOCKS proxy, resolve DNS locally instead (default: False)
  - --bind               *Set 'IP:PORT' to bind outgoing connections to. If port is '0' then the system will choose an available port (ex, '192.168.1.1:8080')

**Cookies & Authentication:**
  - --cookies                 *Set a cookies to be sent with ALL requests, semicolon-separated (ex, 'cookie1=value1;cookie2=value2')
  - --cookies-file            *Path to the file name that contain cookies to be sent with ALL requests (ex, 'mycookies.txt')
                              NOTE: cookies format in the file must be like this: 'cookie1=value1;cookie2=value2'
  - --specific-cookies        *Set cookies for a specific domains (ex, 'http://site1.com;cookie1=value1,cookie2=value2|https://site2.com;cookie3=value3')
  - --specific-cookies-file   *Path to the file name that contain cookies for a specific domains (ex, 'mycookies.txt')
                              NOTE: cookies format in the file must be like this: 'http://site1.com;cookie1=value1,cookie2=value2|https://site2.com;cookie3=value3'
  - --allow-unsafe-cookies    *Allow cross-domain cookies (default: False)
  - --ignore-cookies          *Disable cookies handling, no cookies will be stored or sent with requests (default: False)
  - --auth                    *Set USERNAME:PASSWORD for basic authentication for all HTTPs requests (ex, 'testuser:anypass123')
                              NOTE: If some requests don't require authentication, then using this option might cause errors.
  - --auth-file               *Path to the file name that contain USERNAME:PASSWORD for basic authentication for all HTTPs requests (ex, 'creds.txt')
                              NOTE: If some requests don't require authentication, then using this option might cause errors.

**SSL/TLS:**
  - --no-ssl              *Disable SSL certificate verification (default: False)
  - --ssl-cert            *Path to the client certificate file (ex, 'client.crt')
  - --ssl-key             *Path to the client private key file (ex, 'client.key')
  - --ca-cert             *Path to the custom CA certificate file (ex, 'ca.crt')
  - --fingerprint         *SSL fingerprint in hex format (ex, '2a63729dc68....')
  - --fingerprint-file    *Path to a file name containing the SSL fingerprint in hex format (ex, 'fingerprint.txt')

**Filtering & Analysing:**
  - --only                         *Show only responses with specific status code, comma-separated (ex, 200,201,403)
  - --skip                         *Skip responses with specific status code, comma-separated (ex, 404,501)
  - --only-2xx                     *Show only responses with 2xx status code (default: False)
  - --only-3xx                     *Show only responses with 3xx status code (default: False)
  - --only-4xx                     *Show only responses with 4xx status code (default: False)
  - --only-5xx                     *Show only responses with 5xx status code (default: False)
  - --less-400                     *Show only responses with less than 400 status code (default: False)
  - --no-empty-content             *Skip responses with 0 content-bytes (default: False)
  - --max-content                  *Only show responses with content size less than or equal to the specified number of bytes (ex, 1000)
  - --min-content                  *Only show responses with content size greater than or equal to the specified number of bytes (ex, 50)
  - --no-content-size              *Do NOT show response content size (default: False)
  - --no-payload-size              *Do NOT show payload size, if --random-payload or data given (default: False)
  - --no-request-headers           *Do NOT show the number of request headers (default: False)
  - --no-request-headers-size      *Do NOT show the size of request headers (default: False)
  - --no-response-headers          *Do NOT show the number of response headers (default: False)
  - --no-response-headers-size     *Do NOT show the size of response headers (default: False)
  - --no-time                      *Do NOT show request duration, the time that request took to be processed (default: False)
  - --no-title                     *Do NOT show response title (default: False)
  - --no-response-headers-saving   *Do NOT save response headers in '--output-file', if '--output-file' (default: False)
  - --no-analyze                   *Disable analyzing responses (default: False)
  - --analyze-by                   *Specify responses analyzing logic using AND/OR operators (default: read 'uquix/docs/analysis_guide.md')
                                   NOTE: Analyzing colors will be based on given logic
                                   NOTE: Sorting conditions is important

**Output Saving:**
  - --output-file      *Output file name to save requests with its info or discovered subdomains (ex, 'newurls.txt')
  - --output-sorted    *Output file name to save requests with its info but sorted by url, if --output-file (default: "sorted_'--output-file'")
  - --output-analyze   *Output file name to save responses analyzing results, if --output-file (default: "analyze_'--output-file'")
  - --html-dir         *Output directory name to save every response as '.html' file (ex, 'testedurls')

**Progress & Other:**
  - --disable-detailed-progress   *Disable showing the progress of HTTP URLs and HTTPS URLs, only show ALL URLs progress (default: False)
  - --disable-progress            *Disable the progress line entirely (default: False)
  - --show-errs                   *Show all unexpected errors, like when sending a huge size of headers (default: False)
  - --no-colors                   *Suppress output coloring (default: False)
  - --silence                     *Enable quiet mode, but keeps progress (default: False)
  - --no-history                  *Do NOT store current arguments to 'uquix/history.log' file (default: False)
  - --no-max-speed                *Reduce async concurrency for lower CPU usage (default: False)
  - --version                     *Show current UQUIX version

</details>

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

![Screenshot](UQUIX_example.png)

## Requirements
    
    Python 3.9+

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

- By: Abd Almoen Arafa (0.1Arafa)                              
- Age: 18                                                      
- Year: 2025
                                                   
#######################################################################

*WARNING: Please ask for PERMISSIONS before testing any web server.  
*Use this tool AT YOUR OWN RISK.                                     
*I'm NOT responsible for any unethical action.                       


