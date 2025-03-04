#!/usr/bin/python3

################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################

import argparse, uvloop, asyncio, signal, sys, os, time
from uquix.main import MyMainClass


def signal_handler(sig, frame) -> KeyboardInterrupt:

    sys.__stdout__.write("\n\033[1;31m[!] CTRL+C detected. Exiting...\033[0m\n" if "--no-colors" not in sys.argv else "\n[!] CTRL+C detected. Exiting...\n")
    sys.__stdout__.flush()
    time.sleep(1)
    raise KeyboardInterrupt


def version() -> str:

    return "1.0.0"


def banner() -> str:

    return f"""\033[90m
   ╭─────────╮
==>│  \033[31mUQUIX\033[90m  │─────┐
   ╰─────────╯     │
                   ▼
               ╭──────────────────╮
\033[\033[38;2;0;128;0mBy: 0.1Arafa\033[0m\033[90m   │    WEB SERVER    │─────┐
               │                  │     │
\033[\033[38;2;0;128;0mv{version()}\033[0m\033[90m         │  (╯^□^)╯ ︵ ┻━┻  │     │
               ╰──────────────────╯     │
                                        ▼
"Web Server panicked, flipped the table: \033[31m'FATAL ERROR: REQUEST PARSER SELF-DESTRUCTED!'\033[90m"
\033[0m"""


def theparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="Description:\n\tResponse-Xplore: Sends Unexpected Fully Customizable Requests to Test Server Responses.\n\tSubs-Xplore: Subdomain Enumeration by Resolving Subdomains for a Domain(s) via DNS Brute-force.",
        epilog=(
            "\033[1;37mUsage Examples:\033[0m\n\n"
            f"  uquix Response-Xplore urls.txt\n\n"
            f"  uquix Response-Xplore urls.txt --concurrent-requests 300 --random-agents --random-headers 10 --random-payload --methods all --data-methods POST,PUT,PATCH,DELETE --output-file subs.txt\n\n"
            f"  uquix Response-Xplore urls.txt --random-headers 3 --methods get,post --timeout 5 --retries 0 --auth-file creds.txt --disable-redirect --ignore-cookies --no-title --output-file subs.txt --output-dir htmlsubs\n\n"
            f"  uquix Response-Xplore urls.txt --random-headers 0 --methods all --max-redirects-http 1 --max-redirects-https 5 --no-ssl\n\n"
            f"  uquix Response-Xplore urls.txt --methods PUT,PATCH,OPTIONS,HEAD,CONNECT --concurrent-requests 1000 --dns-servers-file resolvers.txt --proxy http://127.0.0.1:8080 --socks-proxy socks5://user:pass@127.0.0.1:9050 --route-socks-first --no-dns-cache\n\n"
            f"  uquix Response-Xplore urls.txt --add-http --add-https --concurrent-requests 1000 --methods all --data-methods post,put --random-agents --random-headers 1 --random-payload --ignore-cookies --no-ssl --dns-retries 0 --req-retries 3 --retries-delay 2 --exp-backoff --dns-servers-file resolvers.txt --dns-timeout 0.5 --req-timeout 6 --ttl-dns-cache 5 --min-content 50 --final-url --max-redirects-http 3 --max-redirects-https 5 --less-400 --no-empty-content --no-title --analyze-by 'STATUS or RES_HDRS and RES_HDRS_SIZE or CONTENT or DURATION'\n\n"
            f"  uquix Subs-Xplore subslist.txt --target-domain example.com\n"
            f"  uquix Subs-Xplore subslist.txt --target-domain example.com --timeout 3 --concurrent-queries 1000 --show-records\n"
            f"  uquix Subs-Xplore subslist.txt --target-domains-file domains.txt --show-only-cname --output-file newsubs.txt --dns-servers-file resolvers.txt\n"
            f"  uquix Subs-Xplore subslist.txt --target-domain example.com --silence --enable-rotate\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    basic = parser.add_argument_group("\033[1;37mBasic Arguments\033[0m")
    basic.add_argument("mode", help="Mode ['Response-Xplore', 'Subs-Xplore']. Choose only one mode.\nChoose 'Response-Xplore' to manipulate HTTPs requests or 'Subs-Xplore' for subdomain enumeration via DNS brute-force.")
    basic.add_argument("file", help="Path to the URLs file (ex, '/path/to/urls.txt') for 'Response-Xplore' mode.\nPath to the subdomains file (ex, '/path/to/subs.txt') for 'Subs-Xplore' mode.")

    subs = parser.add_argument_group("\033[1;37mSubs-Xplore Options\033[0m")
    subs.add_argument("--target-domain", type=str, help="Target domain to resolve subdomains for, without a protocol (ex, 'example.com')")
    subs.add_argument("--target-domains-file", help="Path to file name that contain target domains without a protocol to resolve subdomains for (ex, 'domains.txt')")
    subs.add_argument("--concurrent-queries", type=int, default=600, help="Number of concurrent DNS queries (default: 600)")
    subs.add_argument("--show-records", action="store_true", help="Show 'A' and 'CNAME' records of discovered subdomains (default: False)")
    subs.add_argument("--show-only-a", action="store_true", help="Show only 'A' records of discovered subdomains (default: False)")
    subs.add_argument("--show-only-cname", action="store_true", help="Show only 'CNAME' records of discovered subdomains (default: False)")

    dns = parser.add_argument_group("\033[1;37mDNS Options\033[0m")
    dns.add_argument("--dns-servers", type=str,help="Custom DNS servers for resolving hostnames, as string comma-separated or as list (ex1, '8.8.8.8,8.8.4.4'.ex2, \"['8.8.8.8', '1.1.1.1']\")")
    dns.add_argument("--dns-servers-file", help="Path to a file name containing custom DNS servers for resolving hostnames, one per line (ex, 'resolvers.txt')")
    dns.add_argument("--udp-port", type=int, help="The UDP port to use for DNS queries (default: 53)")
    dns.add_argument("--tcp-port", type=int, help="The TCP port to use for DNS queries (default: 53)")
    dns.add_argument("--flags", type=int, help="Custom flags for DNS queries (default: 0)")
    dns.add_argument("--socket-sbs", type=int, help="Size of the send buffer for sockets, in bytes (default: system-defined)")
    dns.add_argument("--socket-rbs", type=int, help="Size of the receive buffer for sockets, in bytes (default: system-defined)")
    dns.add_argument("--enable-rotate", action="store_true", help="Enable DNS server rotation, useful for load balancing (default: False)")
    dns.add_argument("--bind-ip-dns", type=str, help="The local IP to bind for DNS queries (ex, '192.168.1.16')")
    dns.add_argument("--net-dev", type=str, help="The network device (interface) to use for DNS queries (ex, 'eth0')")
    dns.add_argument("--resolvconf", type=str, help="Path to a custom resolv.conf file for DNS configuration (default: '/etc/resolv.conf')")

    timeout = parser.add_argument_group("\033[1;37mTimeout & Connection\033[0m")
    timeout.add_argument("--timeout", type=float, default=10.0, help="Overall timeout for HTTPs request and timeout for DNS query, in seconds (default: 10.0)")
    timeout.add_argument("--dns-timeout", type=float, help="Timeout for DNS query, in seconds (ex, 5.0)")
    timeout.add_argument("--req-timeout", type=float, help="Overall timeout for HTTPs request, in seconds (ex, 10.0)")
    timeout.add_argument("--connect-timeout", type=float, default=None, help="Timeout for finding and connecting to the server, including DNS lookup and the initial TCP handshake,\nor timeout for waiting for a free connection from the pool if pool connection limits are exceeded, in seconds (default: unlimited)")
    timeout.add_argument("--sock-connect-timeout", type=float, default=None, help="Timeout for TCP handshake, in seconds (default: unlimited)")
    timeout.add_argument("--sock-read-timeout", type=float, default=None, help="Timeout for waiting for the server to send back data, in seconds (default: unlimited)")
    timeout.add_argument("--keepalive-timeout", type=float, help="Timeout for idle keep-alive connections, in seconds (default: 30.0)")
    timeout.add_argument("--concurrent-requests", type=int, default=100, help="Number of concurrent HTTPs requests (default: 100)")
    timeout.add_argument("--max-connections", help="Limit the maximum number of concurrent connections, to unlimit it pass 'unlimited' (default: 100)")
    timeout.add_argument("--per-host-connections", type=int, help="Limit the number of connections per host (default: unlimited)")
    timeout.add_argument("--no-dns-cache", action="store_true", help="Disable DNS caching (default: False)")
    timeout.add_argument("--ttl-dns-cache", type=int, help="Time To Live (TTL) for DNS cache entries, in seconds (default: 10)")

    retry = parser.add_argument_group("\033[1;37mRetry & Backoff\033[0m")
    retry.add_argument("--retries", type=int, default=1, help="HTTPs request retries, and DNS query retries (default: 1)")
    retry.add_argument("--dns-retries", type=int, help="DNS query retries (ex, 2)")
    retry.add_argument("--req-retries", type=int, help="HTTPs request retries (ex, 3)")
    retry.add_argument("--retries-delay", type=float, help="Set a delay number between retries for HTTPs requests, in seconds (default: 0.0)")
    retry.add_argument("--exp-backoff", action="store_true", help="Exponential Backoff, wait longer after each retry for HTTPs requests, '--retries-delay' option is required (default: False)")

    http = parser.add_argument_group("\033[1;37mHTTPs Request\033[0m")
    http.add_argument("--random-agents", action="store_true", help="Use random user-agent for every HTTPs request (default: False)")
    http.add_argument("--random-headers", type=int, default=3, help="Number of times to send the same request but with random headers based on headers rules file, and with random payload from payloads file if '--random-payload' (default: 3)\nNOTE: If 0, only headers that has '\"isalways\": true' rule will be sent")
    http.add_argument("--headers-rules-file", help="Path to JSON file name that contain headers with its rules (default: 'uquix/configs/headers_rules.json')")
    http.add_argument("--custom-headers", type=str, help="Add JSON-formatted headers (ex, '{\"header1\": \"value1\", \"header2\": \"value2\"}')")
    http.add_argument("--file-custom-headers", help="Path to file name that contain headers to add, headers must be JSON-formatted (ex, 'headers.txt')")
    http.add_argument("--no-403headers", action="store_true", help="Skip headers that has 'is403' rule is true (default: False)")
    http.add_argument("--methods", type=str, default="GET,POST,PUT,HEAD,DELETE", help="HTTPs request methods, comma-separated (default: GET,POST,PUT,HEAD,DELETE)")
    http.add_argument("--add-http", action="store_true", help="Add 'http://' to all URLs (default: False)")
    http.add_argument("--add-https", action="store_true", help="Add 'https://' to all URLs (default: False)")
    http.add_argument("--ports", type=str, help="Ports to append to ALL URLs, comma-separated (ex, 80,443) (default: None)")
    http.add_argument("--ports-http", type=str, help="Ports to append to HTTP URLs, comma-separated (default: 80)")
    http.add_argument("--ports-https", type=str, help="Ports to append to HTTPS URLs, comma-separated (default: 443)")
    http.add_argument("--real-url", action="store_true", help="Show the actual request url instead of as it given from the file (default: False)")
    http.add_argument("--final-url", action="store_true", help="Show the final request url instead of as it given from the file, after following any redirects (default: False)")
    http.add_argument("--params", type=str, help="Specify query parameters to append to ALL URLs, JSON-formatted (ex, '{\"param1\":\"value1\",\"param2\":\"value2\"}')")
    http.add_argument("--buffer-size", type=int, help="Set the size of the read buffer, in bytes (default: 65536)")
    http.add_argument("--disable-redirect", action="store_true", help="Disable ALL requests to follow redirects (default: False)")
    http.add_argument("--disable-redirect-http", action="store_true", help="Disable only HTTP requests to follow redirects (default: False)")
    http.add_argument("--disable-redirect-https", action="store_true", help="Disable only HTTPS requests to follow redirects (default: False)")
    http.add_argument("--max-redirects", type=int, help="Limit the number of maximum redirects to follow for ALL requests (default: 10)")
    http.add_argument("--max-redirects-http", type=int, help="Limit the number of maximum redirects to follow for only HTTP requests (ex, 5)")
    http.add_argument("--max-redirects-https", type=int, help="Limit the number of maximum redirects to follow for only HTTPS requests (ex, 5)")
    http.add_argument("--no-ujson", action="store_false", help="Use JSON instead of UltraJSON (ujson) (default: False)")

    data = parser.add_argument_group("\033[1;37mData/Payload\033[0m")
    data.add_argument("--random-payload", action="store_true", help="Enable to select one random payload for each request from 'uquix/configs/random_payloads.txt' (default: False)")
    data.add_argument("--payloads-file", help="Path to file name that contain payloads, one random payload will be picked randomly for each request, payloads must separated by '\\n===\\n', if '--random-payload' (default: 'uquix/configs/random_payloads.txt')")
    data.add_argument("--data-methods", type=str, help="Specify the request methods will include data/payload in request, comma-separated (ex, 'post,put,patch') (default: '--methods')")
    data.add_argument("--data", type=str, help="Send data/payload in the request body to ALL requests (ex, 'anykey=anyvalue&anything=anythingtoo')")
    data.add_argument("--file-data", help="Path to file name that contain data/payload to send in the request body to ALL requests (ex, '/path/to/anydata.bin')")
    data.add_argument("--json-data", type=str, help="Send JSON-formatted data/payload in the request body to ALL requests (ex, '{\"key\": \"value\", \"key2\": \"value2\"}')")
    data.add_argument("--file-json-data", help="Path to file name that contain JSON-formatted data/payload to send in the request body to ALL requests (ex, '/path/to/data.json')")
    data.add_argument("--data-encode-type", type=str, help="Specify data encoding type for ['--data', '--json-data', '--file-json-data'] (default: 'utf-8')")
    data.add_argument("--no-data-saving", action="store_true", help="Do NOT save requests data/payload to '--output-file' (default: False)")

    proxy = parser.add_argument_group("\033[1;37mProxy & Binding\033[0m")
    proxy.add_argument("--proxy", type=str, help="Use a proxy server for HTTPs requests (ex, 'http://user:pass@127.0.0.1:8080')")
    proxy.add_argument("--socks-proxy", type=str, help="Use a SOCKS proxy server for HTTPs requests (ex, 'socks5://user:pass@127.0.0.1:9050')")
    proxy.add_argument("--route-socks-first", action="store_true", help="If both proxies are used, then route requests through SOCKS-PROXY first (default: False)")
    proxy.add_argument("--no-rdns", action="store_true", help="Do NOT resolve DNS through SOCKS proxy, resolve DNS locally instead (default: False)")
    proxy.add_argument("--bind", type=str, help="Set 'IP:PORT' to bind outgoing connections to. If port is '0' then the system will choose an available port (ex, '192.168.1.1:8080')")

    auth = parser.add_argument_group("\033[1;37mCookies & Authentication\033[0m")
    auth.add_argument("--cookies", type=str, help="Set a cookies to be sent with ALL requests, semicolon-separated (ex, 'cookie1=value1;cookie2=value2')")
    auth.add_argument("--cookies-file", help="Path to the file name that contain cookies to be sent with ALL requests (ex, 'mycookies.txt')\nNOTE: cookies format in the file must be like this: 'cookie1=value1;cookie2=value2'")
    auth.add_argument("--specific-cookies", type=str, help="Set cookies for a specific domains (ex, 'http://site1.com;cookie1=value1,cookie2=value2|https://site2.com;cookie3=value3')")
    auth.add_argument("--specific-cookies-file", help="Path to the file name that contain cookies for a specific domains (ex, 'mycookies.txt')\nNOTE: cookies format in the file must be like this: 'http://site1.com;cookie1=value1,cookie2=value2|https://site2.com;cookie3=value3'")
    auth.add_argument("--allow-unsafe-cookies", action="store_true", help="Allow cross-domain cookies (default: False)")
    auth.add_argument("--ignore-cookies", action="store_true", help="Disable cookies handling, no cookies will be stored or sent with requests (default: False)")
    auth.add_argument("--auth", type=str, help="Set USERNAME:PASSWORD for basic authentication for all HTTPs requests (ex, 'testuser:anypass123')\nNOTE: If some requests don't require authentication, then using this option might cause errors.")
    auth.add_argument("--auth-file", help="Path to the file name that contain USERNAME:PASSWORD for basic authentication for all HTTPs requests (ex, 'creds.txt')\nNOTE: If some requests don't require authentication, then using this option might cause errors.")

    ssl = parser.add_argument_group("\033[1;37mSSL/TLS\033[0m")
    ssl.add_argument("--no-ssl", action="store_true", help="Disable SSL certificate verification (default: False)")
    ssl.add_argument("--ssl-cert", help="Path to the client certificate file (ex, 'client.crt')")
    ssl.add_argument("--ssl-key", help="Path to the client private key file (ex, 'client.key')")
    ssl.add_argument("--ca-cert", help="Path to the custom CA certificate file (ex, 'ca.crt')")
    ssl.add_argument("--fingerprint", type=str, help="SSL fingerprint in hex format (ex, '2a63729dc68....')")
    ssl.add_argument("--fingerprint-file", help="Path to a file name containing the SSL fingerprint in hex format (ex, 'fingerprint.txt')")

    res = parser.add_argument_group("\033[1;37mFiltering & Analysing\033[0m")
    res.add_argument("--only", type=str, help="Show only responses with specific status code, comma-separated (ex, 200,201,403)")
    res.add_argument("--skip", type=str, help="Skip responses with specific status code, comma-separated (ex, 404,501)")
    res.add_argument("--only-2xx", action="store_true", help="Show only responses with 2xx status code (default: False)")
    res.add_argument("--only-3xx", action="store_true", help="Show only responses with 3xx status code (default: False)")
    res.add_argument("--only-4xx", action="store_true", help="Show only responses with 4xx status code (default: False)")
    res.add_argument("--only-5xx", action="store_true", help="Show only responses with 5xx status code (default: False)")
    res.add_argument("--less-400", action="store_true", help="Show only responses with less than 400 status code (default: False)")
    res.add_argument("--no-empty-content", action="store_true", help="Skip responses with 0 content-bytes (default: False)")
    res.add_argument("--max-content", type=int, help="Only show responses with content size less than or equal to the specified number of bytes (ex, 1000)")
    res.add_argument("--min-content", type=int, help="Only show responses with content size greater than or equal to the specified number of bytes (ex, 50)")
    res.add_argument("--no-content-size", action="store_true", help="Do NOT show response content size (default: False)")
    res.add_argument("--no-payload-size", action="store_true", help="Do NOT show payload size, if --random-payload or data given (default: False)")
    res.add_argument("--no-request-headers", action="store_true", help="Do NOT show the number of request headers (default: False)")
    res.add_argument("--no-request-headers-size", action="store_true", help="Do NOT show the size of request headers (default: False)")
    res.add_argument("--no-response-headers", action="store_true", help="Do NOT show the number of response headers (default: False)")
    res.add_argument("--no-response-headers-size", action="store_true", help="Do NOT show the size of response headers (default: False)")
    res.add_argument("--no-time", action="store_true", help="Do NOT show request duration, the time that request took to be processed (default: False)")
    res.add_argument("--no-title", action="store_true", help="Do NOT show response title (default: False)")
    res.add_argument("--no-response-headers-saving", action="store_false", help="Do NOT save response headers in '--output-file', if '--output-file' (default: False)")
    res.add_argument("--no-analyze", action="store_true", help="Disable analyzing responses (default: False)")
    res.add_argument("--analyze-by", type=str, help="Specify responses analyzing logic using AND/OR operators (default: read 'uquix/docs/analysis_guide.md')\nNOTE: Analyzing colors will be based on given logic\nNOTE: Sorting conditions is important")

    output = parser.add_argument_group("\033[1;37mOutput Saving\033[0m")
    output.add_argument("--output-file", help="Output file name to save requests with its info or discovered subdomains (ex, 'newurls.txt')")
    output.add_argument("--output-sorted", help="Output file name to save requests with its info but sorted by url, if --output-file (default: \"sorted_'--output-file'\")")
    output.add_argument("--output-analyze", help="Output file name to save responses analyzing results, if --output-file (default: \"analyze_'--output-file'\")")
    output.add_argument("--html-dir", help="Output directory name to save every response as '.html' file (ex, 'testedurls')")

    progress = parser.add_argument_group("\033[1;37mProgress & Other\033[0m")
    progress.add_argument("--disable-detailed-progress", action="store_false", help="Disable showing the progress of HTTP URLs and HTTPS URLs, only show ALL URLs progress (default: False)")
    progress.add_argument("--disable-progress", action="store_true", help="Disable the progress line entirely (default: False)")
    progress.add_argument("--show-errs", action="store_true", help="Show all unexpected errors, like when sending a huge size of headers (default: False)")
    progress.add_argument("--no-colors", action="store_true", help="Suppress output coloring (default: False)")
    progress.add_argument("--silence", action="store_true", help="Enable quiet mode, but keeps progress (default: False)")
    progress.add_argument("--no-history", action="store_true", help="Do NOT store current arguments to 'uquix/history.log' file (default: False)")
    progress.add_argument("--no-max-speed", action="store_true", help="Reduce async concurrency for lower CPU usage (default: False)")
    progress.add_argument("--version", action="store_true", help="Show current UQUIX version")

    args = parser.parse_args()
    
    return args


def main():
    
    if "--version" in sys.argv:
        print(f"[*] Current UQUIX version is \033[92m{version()}\033[0m")
        exit(0)

    if not sys.argv[1:]:
        os.system("uquix --help")
        exit(0)

    print(banner())

    if sys.version_info < (3,9,0):
        print("[-] Error: Python 3.9+ required")
        print("[*] Update Python to the latest version by running: sudo apt update && sudo apt install python3 -y")
        exit(0)

    try:
        signal.signal(signal.SIGINT, signal_handler)
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(MyMainClass(theparser()).main())
    except KeyboardInterrupt:
        sys.__stdout__.write("\033[1;31m[!] Execution terminated manually.\033[0m" if "--no-colors" not in sys.argv else "[!] Execution terminated manually.")
        sys.__stdout__.flush()
        exit(1)
    except ValueError:
        pass


if __name__ == "__main__":

    main()


################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# 2025                                                         #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################
