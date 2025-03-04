################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################

import asyncio, aiodns, aiohttp, aiohttp_socks, aiofiles, sys, ssl, string, datetime, time, os, random, re, pathlib
from collections import defaultdict
from itertools import combinations
from uquix.headers_generator import MyMainHeaders

class MyMainClass:

    def __init__(self, args):

        self.args = args
        self.SHOW_ERRORS = self.args.show_errs
        self.NO_COLORS = self.args.no_colors
        if not self.SHOW_ERRORS:
            with open(os.devnull, "w") as nullfile:
                sys.stderr = nullfile
        self.MODE = self.args.mode.lower().strip()
        self.USE_UJSON = self.args.no_ujson
        self.HEADERS_RULES_FILE = self.args.headers_rules_file
        if self.USE_UJSON:
            import ujson as json
        else:
            import json
        try:
            hdrs_rules_file = pathlib.Path(__file__).parent.parent.parent / "configs" / "headers_rules.json" if not self.HEADERS_RULES_FILE else self.HEADERS_RULES_FILE
            if not os.path.exists(hdrs_rules_file):
                print(f"[-] Error, '{hdrs_rules_file}' file not found")
                exit(0)
            with open(hdrs_rules_file, "r") as hmf:
                self.headersrules = json.load(hmf)
        except FileNotFoundError:
            print(f"[-] Error, '{hdrs_rules_file}' file not found")
            exit(1)
        except Exception as e:
            print(f"[-] Error while validating JSON in '{hdrs_rules_file}' file: {e}")
            exit(1)
        self.CONCURRENT_QUERIES = self.args.concurrent_queries if self.MODE == "subs-xplore" else None
        self.CONCURRENT_REQUESTS = self.args.concurrent_requests if self.MODE == "response-xplore" else None
        if self.CONCURRENT_QUERIES is not None and self.CONCURRENT_QUERIES < 0:
            print("[-] Error, '--concurrent-queries' must be positive integer number")
            exit(0)
        if self.CONCURRENT_REQUESTS is not None and self.CONCURRENT_REQUESTS < 0:
            print("[-] Error, '--concurrent-requests' must be positive integer number")
            exit(0)
        if self.CONCURRENT_REQUESTS is not None and not self.CONCURRENT_REQUESTS:
            print("[-] Error, '--concurrent-requests' must be bigger than 0")
            exit(0)
        if self.CONCURRENT_QUERIES is not None and not self.CONCURRENT_QUERIES:
            print("[-] Error, '--concurrent-queries' must be bigger than 0")
            exit(0)
        subs_allowed_args = {
            "-h", "--help", "--target-domain", "--target-domains-file", "--timeout", "--dns-timeout",
            "--concurrent-queries", "--show-records", "--show-only-a", "--show-only-cname",
            "--dns-servers", "--dns-servers-file", "--udp-port", "--tcp-port", "--flags",
            "--socket-sbs", "--socket-rbs", "--enable-rotate", "--bind-ip-dns", "--net-dev",
            "--resolvconf", "--output-file", "--disable-progress", "--hide-errs",
            "--no-colors", "--silence", "--retries", "--dns-retries"
        }
        if self.CONCURRENT_QUERIES:
            subs_invalid_args = [arg for arg in sys.argv[3:] if arg not in subs_allowed_args]
            if subs_invalid_args:
                print(f"[-] Error, 'Subs-Xplore' mode only accepts these arguments:\n  {', '.join(sorted(subs_allowed_args))}")
                exit(0)
        self.OUTPUT = self.args.output_file.strip() if self.args.output_file else None
        if self.OUTPUT and not os.path.basename(self.OUTPUT):
            print("[-] Error, '--output-file' must be a file path not a directory")
            exit(0)
        if self.OUTPUT:
            output_dir = os.path.dirname(self.OUTPUT)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        if self.args.output_file is not None and self.args.output_file.strip() == "":
            print("[-] Error, '--output-file' isn't valid file path")
            exit(0)
        self.SILENCE = self.args.silence
        self.NO_RESPONSE_HEADERS_SAVING = self.args.no_response_headers_saving
        self.ALL_SUBDOMAINS = list() if self.CONCURRENT_QUERIES else set()
        self.UNIQUE_HTTP = set()
        self.UNIQUE_HTTPS = set()
        self.wildcard_ips = set()
        self.START_TIME = None
        self.ALL_REQUESTS = 0
        self.ALL_HTTP_REQUESTS = 0
        self.ALL_HTTP_SUBDOMAINS = list()
        self.ALL_HTTPS_REQUESTS = 0
        self.ALL_HTTPS_SUBDOMAINS = list()
        self.TOTAL_FAILED_REQS = 0
        self.HTTP_FAILED_REQS = 0
        self.HTTPS_FAILED_REQS = 0
        self.ALL_SORTED_RESULTS = list()
        self.DETAILED_ALL_SORTED_RESULTS = list()

        self.SUBDOMAINS_FILE = self.args.file.strip()
        self.TARGET_DOMAIN = self.args.target_domain.strip() if self.args.target_domain else None
        self.TARGET_DOMAINS_FILE = self.args.target_domains_file.strip() if self.args.target_domains_file else None
        self.DOMAINS = None
        if self.TARGET_DOMAINS_FILE and self.TARGET_DOMAIN:
            print("[-] Error, you can't use '--target-domain' and '--target-domains-file' together, use only one option")
            exit(0)
        if self.TARGET_DOMAINS_FILE:
            try:
                with open(self.TARGET_DOMAINS_FILE, "r") as f:
                    self.DOMAINS = [d.strip() for d in f.readlines() if d.strip()]
            except FileNotFoundError:
                print("[-] Error, target domains file not found")
                exit(1)
            except Exception as e:
                print(f"[-] Error in target domains file. {e}")
                exit(1)
        if self.TARGET_DOMAINS_FILE is not None and not self.DOMAINS:
            print("[-] Error, target domains file is empty")
            exit(0)
        if self.TARGET_DOMAIN is not None and "://" in self.TARGET_DOMAIN:
            print("[-] Error, '--target-domain' mustn't contain the protocol type, remove 'http://' or 'https://'")
            exit(0)
        if self.CONCURRENT_QUERIES and not self.TARGET_DOMAIN and not self.DOMAINS:
            print("[-] Error, no target domain was given")
            exit(0)
        self.TIMEOUT = self.args.timeout
        self.DNS_TIMEOUT = self.args.dns_timeout
        self.REQ_TIMEOUT = self.args.req_timeout
        if self.DNS_TIMEOUT is not None and self.REQ_TIMEOUT is None and self.CONCURRENT_REQUESTS:
            self.REQ_TIMEOUT = self.TIMEOUT
        if self.REQ_TIMEOUT is not None and self.DNS_TIMEOUT is None and self.CONCURRENT_REQUESTS:
            self.DNS_TIMEOUT = self.TIMEOUT
        if self.DNS_TIMEOUT is not None or self.REQ_TIMEOUT is not None:
            self.TIMEOUT = None
        self.CONNECT_TIMEOUT = self.args.connect_timeout
        self.SOCK_CONNECT_TIMEOUT = self.args.sock_connect_timeout
        self.SOCK_READ_TIMEOUT = self.args.sock_read_timeout
        self.KEEPALIVE_TIMEOUT = self.args.keepalive_timeout
        if self.TIMEOUT is not None and self.TIMEOUT < 0 or self.DNS_TIMEOUT is not None and self.DNS_TIMEOUT < 0 or self.REQ_TIMEOUT is not None and self.REQ_TIMEOUT < 0 or self.CONNECT_TIMEOUT is not None and self.CONNECT_TIMEOUT < 0 or self.SOCK_CONNECT_TIMEOUT is not None and self.SOCK_CONNECT_TIMEOUT < 0 or self.SOCK_READ_TIMEOUT is not None and self.SOCK_READ_TIMEOUT < 0 or self.KEEPALIVE_TIMEOUT is not None and self.KEEPALIVE_TIMEOUT < 0:
            print("[-] Error, timeouts must be positives numbers")
            exit(0)
        if self.args.max_connections is not None:
            try:
                if self.args.max_connections.lower().strip() == "unlimited":
                    self.LIMIT = None
                else:
                    self.LIMIT = int(self.args.max_connections)
                if self.LIMIT is not None and self.LIMIT < 0:
                    print("[-] Error, '--max-connections' must be positive integer number or 'unlimited'")
                    exit(0)
            except Exception as e:
                print(f"[-] Error, '--max-connections' must be positive integer number or 'unlimited'")
                exit(1)
        self.LIMIT_PER_HOST = self.args.per_host_connections if self.args.per_host_connections is not None else None
        if self.LIMIT_PER_HOST is not None and self.LIMIT_PER_HOST < 0:
            print("[-] Error, '--per-host-connections' must be positive integer number")
            exit(0)
        self.NO_DNS_CACHE = self.args.no_dns_cache
        self.TTL_DNS_CACHE = self.args.ttl_dns_cache
        if self.TTL_DNS_CACHE is not None and self.TTL_DNS_CACHE < 0:
            print("[-] Error, '--ttl-dns-cache' must be positive integer number")
            exit(0)
        self.SHOW_RECORDS = self.args.show_records
        self.SHOW_ONLY_A = self.args.show_only_a
        self.SHOW_ONLY_CNAME = self.args.show_only_cname
        self.CUSTOM_RESOLVERS = self.args.dns_servers.strip() if self.args.dns_servers else None
        self.CUSTOM_RESOLVERS_FILE = self.args.dns_servers_file.strip() if self.args.dns_servers_file else None
        self.UDP_PORT = self.args.udp_port
        if self.UDP_PORT is not None and self.UDP_PORT < 0:
            print("[-] Error, '--udp-port' must be positive integer number")
            exit(0)
        self.TCP_PORT = self.args.tcp_port
        if self.TCP_PORT is not None and self.TCP_PORT < 0:
            print("[-] Error, '--tcp-port' must be positive integer number")
            exit(0)
        self.FLAGS = self.args.flags
        if self.FLAGS is not None and self.FLAGS < 0:
            print("[-] Error, '--flags' must be positive integer number")
            exit(0)
        self.SOCKET_SBS = self.args.socket_sbs
        if self.SOCKET_SBS is not None and self.SOCKET_SBS < 0:
            print("[-] Error, '--socket-sbs' must be positive integer number")
            exit(0)
        self.SOCKET_RBS = self.args.socket_rbs
        if self.SOCKET_RBS is not None and self.SOCKET_RBS < 0:
            print("[-] Error, '--socket-rbs' must be positive integer number")
            exit(0)
        self.ENABLE_ROTATE = self.args.enable_rotate
        self.BIND_IP_DNS = self.args.bind_ip_dns
        self.NET_DEV = self.args.net_dev
        self.RESOLVCONF_PATH = self.args.resolvconf
        self.OUTPUT_SORTED = None
        self.OUTPUT_ANALYZE = None
        if self.args.output_analyze and self.CONCURRENT_REQUESTS:
            self.OUTPUT_ANALYZE = self.args.output_analyze.strip()
        else:
            if self.OUTPUT and self.CONCURRENT_REQUESTS:
                soa = os.path.dirname(self.OUTPUT)
                if soa:
                    self.OUTPUT_ANALYZE = os.path.join(soa, f"analyze_{os.path.basename(self.OUTPUT)}")
                else:
                    self.OUTPUT_ANALYZE = f"analyze_{self.OUTPUT}"
        if self.OUTPUT_ANALYZE and not self.OUTPUT:
            print("[-] Error, '--output-file' is required when using '--output-analyze'")
            exit(0)
        if self.OUTPUT_ANALYZE and not os.path.basename(self.OUTPUT_ANALYZE.strip()):
            print("[-] Error, '--output-analyze' must be a file path not a directory")
            exit(0)
        if self.OUTPUT_ANALYZE:
            analyze_output_dir = os.path.dirname(self.OUTPUT_ANALYZE)
            if analyze_output_dir:
                os.makedirs(analyze_output_dir, exist_ok=True)
        if self.args.output_analyze is not None and self.args.output_analyze.strip() == "":
            print("[-] Error, '--output-analyze' isn't valid file path")
            exit(0)
        if self.args.output_sorted and self.CONCURRENT_REQUESTS:
            self.OUTPUT_SORTED = self.args.output_sorted.strip()
        else:
            if self.OUTPUT and self.CONCURRENT_REQUESTS:
                sod = os.path.dirname(self.OUTPUT)
                if sod:
                    self.OUTPUT_SORTED = os.path.join(sod, f"sorted_{os.path.basename(self.OUTPUT)}")
                else:
                    self.OUTPUT_SORTED = f"sorted_{self.OUTPUT}"
        if self.OUTPUT_SORTED and not self.OUTPUT:
            print("[-] Error, '--output-file' is required when using '--output-sorted'")
            exit(0)
        if self.OUTPUT_SORTED and not os.path.basename(self.OUTPUT_SORTED.strip()):
            print("[-] Error, '--output-sorted' must be a file path not a directory")
            exit(0)
        if self.OUTPUT_SORTED:
            sorted_output_dir = os.path.dirname(self.OUTPUT_SORTED)
            if sorted_output_dir:
                os.makedirs(sorted_output_dir, exist_ok=True)
        if self.OUTPUT_SORTED:
            self.OUTPUT_DETAILED_SORTED = os.path.join(os.path.dirname(self.OUTPUT_SORTED), f"detailed_{os.path.basename(self.OUTPUT_SORTED)}")
        if self.args.output_sorted is not None and self.args.output_sorted.strip() == "":
            print("[-] Error, '--output-sorted' isn't valid file path")
            exit(0)
        self.OUTPUT_DIR = self.args.html_dir.strip() if self.args.html_dir else None
        self.USE_RANDOM_HEADERS = self.args.random_headers
        if self.USE_RANDOM_HEADERS is not None and self.USE_RANDOM_HEADERS < 0:
            print("[-] Error, '--random-headers' must be positive integer number")
            exit(0)
        self.NUMS_OF_RANDOM_HEADERS = self.USE_RANDOM_HEADERS if self.USE_RANDOM_HEADERS else 1
        self.USE_RANDOM_AGENTS = self.args.random_agents
        self.CUSTOM_HEADERS = self.args.custom_headers
        self.FILE_CUSTOM_HEADERS = self.args.file_custom_headers
        self.NO_403 = self.args.no_403headers
        if self.CUSTOM_HEADERS and self.FILE_CUSTOM_HEADERS:
            print("[-] Error, you can't use '--custom-headers' and '--file-custom-headers' together, use only one option")
            exit(0)
        self.METHODS = self.args.methods
        if self.METHODS.lower().strip() == "all" or self.METHODS.strip() == "*":
            self.METHODS = "GET,POST,PUT,PATCH,DELETE,HEAD,OPTIONS,TRACE,CONNECT"
        else:
            self.METHODS = [i.upper().strip() for i in self.METHODS.split(",") if i.strip()]
            for i in self.METHODS:
                if i.lower() not in ["get", "post", "put", "patch", "delete", "head", "options", "trace", "connect"]:
                    print(f"[-] Error, '{i}' isn't a valid method")
                    exit(0)
            self.METHODS = ",".join(self.METHODS)
        self.PROXY = self.args.proxy.strip() if self.args.proxy else None
        self.SOCKS_PROXY = self.args.socks_proxy.strip() if self.args.socks_proxy else None
        self.ROUTE_SOCKS_FIRST = self.args.route_socks_first
        self.NO_RDNS = self.args.no_rdns
        if self.args.bind:
            try:
                local_ip, local_port = self.args.bind.split(':', 1)
                self.BIND = (local_ip.strip(), int(local_port.strip()))
            except ValueError:
                print("[-] Error: '--bind' must be formatted as 'IP:PORT', port can be '0' for system selection")
                exit(1)
        else:
            self.BIND = None
        self.CONTENT_CUSTOM_HEADERS = None
        self.CONTENT_FILE_CUSTOM_HEADERS = None
        if self.FILE_CUSTOM_HEADERS or self.CUSTOM_HEADERS:
            try:
                if self.CUSTOM_HEADERS:
                    self.CONTENT_CUSTOM_HEADERS = json.loads(self.CUSTOM_HEADERS)
                else:
                    with open(self.FILE_CUSTOM_HEADERS, "r") as fh:
                        self.CONTENT_FILE_CUSTOM_HEADERS = json.load(fh)
            except FileNotFoundError:
                print(f"[-] Error, custom headers file not found")
                exit(1)
            except json.JSONDecodeError:
                print("[-] Error while parsing custom headers file, headers must be JSON-formatted")
                exit(1)
        try:
            self.PARAMS = json.loads(self.args.params) if self.args.params else None
        except json.JSONDecodeError:
            print("[-] Error while parsing query parameters, '--params' must be JSON-formatted")
            exit(1)
        except Exception as e:
            print(f"[-] Error while parsing query parameters: {e}")
            exit(1)
        self.RANDOM_DATA = self.args.random_payload
        self.PAYLOADS_FILE = self.args.payloads_file
        if self.PAYLOADS_FILE and not self.args.random_payload:
            print("[-] Error, payloads file was given but '--random-payload' is false. Use '--random-payload' option")
            exit(0)
        self.DATA = self.args.data
        self.FILE_DATA = self.args.file_data
        self.JSON_DATA = self.args.json_data
        self.FILE_JSON_DATA = self.args.file_json_data
        if self.args.data_encode_type and (self.RANDOM_DATA or self.FILE_DATA):
            print("[-] Error, '--data-encode-type' isn't required when using '--random-payload' or '--file-data'")
            exit(0)
        if self.args.data_encode_type and not (self.DATA or self.JSON_DATA or self.FILE_JSON_DATA):
            print("[-] Error, '--data-encode-type' is given but without data")
            exit(0)
        self.DATA_ENCODE_TYPE = self.args.data_encode_type.strip() if self.args.data_encode_type and (self.DATA or self.JSON_DATA or self.FILE_JSON_DATA) else None
        try:
            paylds_file = pathlib.Path(__file__).parent.parent.parent / "configs" / "random_payloads.txt" if not self.PAYLOADS_FILE else self.PAYLOADS_FILE
            if not os.path.exists(paylds_file):
                print(f"[-] Error, '{paylds_file}' file not found")
                exit(0)
            with open(paylds_file, "rb") as f:
                self.PAYLOADS = f.read().strip().split(b"\n===\n")
        except FileNotFoundError:
            print(f"[-] Error, '{paylds_file}' file not found")
            exit(1)
        except Exception as e:
            print(f"[-] Error while looking for '{paylds_file}' file: {e}")
            exit(1)
        if sum(1 for arg in [self.DATA, self.FILE_DATA, self.JSON_DATA, self.FILE_JSON_DATA, self.RANDOM_DATA] if arg) > 1:
            print("[-] Error, you can use only one option from these: '--random-payload', '--data', '--file-data', '--json-data', '--file-json-data'")
            exit(0)
        self.DATA_PAYLOAD = None
        if self.RANDOM_DATA or self.DATA or self.FILE_DATA or self.FILE_JSON_DATA or self.JSON_DATA:
            try:
                if self.RANDOM_DATA:
                    self.DATA_PAYLOAD = True
                elif self.DATA:
                    self.DATA_PAYLOAD = self.DATA.encode(self.DATA_ENCODE_TYPE if self.DATA_ENCODE_TYPE else "utf-8")
                elif self.JSON_DATA:
                    json_data = json.loads(self.JSON_DATA)
                    self.DATA_PAYLOAD = json.dumps(json_data).encode(self.DATA_ENCODE_TYPE if self.DATA_ENCODE_TYPE else "utf-8")
                else:
                    file_to_read = self.FILE_DATA if self.FILE_DATA else self.FILE_JSON_DATA
                    reading_mode = "rb" if self.FILE_DATA else "r"
                    with open(file_to_read, reading_mode) as fd:
                        if self.FILE_DATA:
                            self.DATA_PAYLOAD = fd.read().strip()
                        else:
                            json_data = json.load(fd)
                            self.DATA_PAYLOAD = json.dumps(json_data).encode(self.DATA_ENCODE_TYPE if self.DATA_ENCODE_TYPE else "utf-8")
            except FileNotFoundError:
                print(f"[-] Error, '{self.FILE_DATA or self.FILE_JSON_DATA}' file not found")
                exit(1)
            except json.JSONDecodeError:
                print("[-] Error parsing JSON data")
                exit(1)
            except Exception as e:
                print(f"[-] Error while importing data: {e}")
                exit(1)
        self.DATA_METHODS = self.METHODS if self.DATA_PAYLOAD and not self.args.data_methods else None
        if self.args.data_methods and not self.DATA_PAYLOAD:
            print("[-] Error, no data given to send in request body, but '--data-methods' is given")
            exit(0)
        if self.args.data_methods:
            self.DATA_METHODS = [i.upper().strip() for i in self.args.data_methods.split(",") if i.strip()]
            for i in self.DATA_METHODS:
                if i.lower() not in ["get", "post", "put", "patch", "delete", "head", "options", "trace", "connect"]:
                    print(f"[-] Error, '{i}' isn't a valid method")
                    exit(0)
                if i not in self.METHODS.split(","):
                    print(f"[-] Error, '{i}' method isn't exist in '--methods', please add '{i}' to '--methods' option")
                    exit(0)
            self.DATA_METHODS = ",".join(self.DATA_METHODS)
        self.NO_DATA_SAVING = self.args.no_data_saving if self.DATA_PAYLOAD else False
        self.BUFFER_SIZE = self.args.buffer_size
        if self.BUFFER_SIZE is not None and self.BUFFER_SIZE < 0:
            print("[-] Error, '--buffer-size' must be positive integer number")
            exit(0)
        self.DISABLE_REDIRECT = self.args.disable_redirect
        self.DISABLE_REDIRECT_HTTP = self.args.disable_redirect_http
        self.DISABLE_REDIRECT_HTTPS = self.args.disable_redirect_https
        if self.DISABLE_REDIRECT and (self.DISABLE_REDIRECT_HTTP or self.DISABLE_REDIRECT_HTTPS):
            print("[-] Error, when using '--disable-redirect' then you can't use '--disable-redirect-http' or '--disable-redirect-https'")
            exit(0)
        self.MAX_REDIRECTS = self.args.max_redirects
        self.MAX_REDIRECTS_HTTP = self.args.max_redirects_http
        self.MAX_REDIRECTS_HTTPS = self.args.max_redirects_https
        self.NO_CONTENT_SIZE = self.args.no_content_size
        self.NO_PAYLOAD_SIZE = self.args.no_payload_size
        self.NO_REQUEST_HEADERS = self.args.no_request_headers
        self.NO_REQUEST_HEADERS_SIZE = self.args.no_request_headers_size
        self.NO_RESPONSE_HEADERS = self.args.no_response_headers
        self.NO_RESPONSE_HEADERS_SIZE = self.args.no_response_headers_size
        if not self.RANDOM_DATA and not self.DATA_PAYLOAD:
            self.NO_PAYLOAD_SIZE = True
        if self.DISABLE_REDIRECT and any(v is not None for v in [self.MAX_REDIRECTS, self.MAX_REDIRECTS_HTTP, self.MAX_REDIRECTS_HTTPS]) or self.DISABLE_REDIRECT_HTTP and self.MAX_REDIRECTS_HTTP is not None or self.DISABLE_REDIRECT_HTTPS and self.MAX_REDIRECTS_HTTPS is not None:
            print("[-] Error, you can't specify the maximum redirects when disabling redirects")
            exit(0)
        self.NO_TIME = self.args.no_time
        self.NO_TITLES = self.args.no_title
        self.NO_SSL = self.args.no_ssl
        self.SSL_CERT = self.args.ssl_cert.strip() if self.args.ssl_cert else None
        self.SSL_KEY = self.args.ssl_key.strip() if self.args.ssl_key else None
        self.CA_CERT = self.args.ca_cert.strip() if self.args.ca_cert else None
        self.FINGERPRINT = self.args.fingerprint.strip() if self.args.fingerprint else None
        self.FINGERPRINT_FILE = self.args.fingerprint_file.strip() if self.args.fingerprint_file else None
        self.COOKIES = dict(cookie.strip().split("=") for cookie in self.args.cookies.strip().split(";")) if self.args.cookies else None
        self.COOKIES_FILE = self.args.cookies_file.strip() if self.args.cookies_file else None
        if self.COOKIES_FILE:
            try:
                with open(self.COOKIES_FILE, "r") as f:
                    self.COOKIES = dict(cookie.strip().split("=") for cookie in f.read().strip().split(";"))
            except FileNotFoundError:
                print("[-] Error, cookies file not found")
                exit(1)
            except Exception as e:
                print(f"[-] Error in cookies file, Makesure cookies are in the right format. {e}")
                exit(1)
        if self.args.cookies and self.COOKIES_FILE:
            print("[-] Error, you can't use '--cookies' and '--cookies-file' together, use only one option\nNOTE: if you don't want the cookies to be stored in the 'uquix/history.log' file then use '--cookies-file' option, so its better for security reasons")
            exit(0)
        self.SPECIFIC_COOKIES = self.args.specific_cookies.strip() if self.args.specific_cookies else None
        self.SPECIFIC_COOKIES_FILE = self.args.specific_cookies_file.strip() if self.args.specific_cookies_file else None
        if self.SPECIFIC_COOKIES_FILE:
            try:
                with open(self.SPECIFIC_COOKIES_FILE, "r") as f:
                    self.SPECIFIC_COOKIES = f.read().strip()
            except FileNotFoundError:
                print("[-] Error, specific cookies file not found")
                exit(1)
            except Exception as e:
                print(f"[-] Error in specific cookies file, Makesure cookies are in the right format. {e}")
                exit(1)
        if self.args.specific_cookies and self.SPECIFIC_COOKIES_FILE:
            print("[-] Error, you can't use '--specific-cookies' and '--specific-cookies-file' together, use only one option\nNOTE: if you don't want the cookies to be stored in the 'uquix/history.log' file then use '--specific-cookies-file' option, so its better for security reasons")
            exit(0)
        self.ALLOW_UNSAFE_COOKIES = self.args.allow_unsafe_cookies
        self.IGNORE_COOKIES = self.args.ignore_cookies
        if self.IGNORE_COOKIES and (self.COOKIES or self.SPECIFIC_COOKIES):
            print("[-] Error, you can't set cookies when ignoring cookies")
            exit(0)
        if self.args.auth is not None and self.args.auth_file is not None and self.args.auth_file.strip():
            print("[-] Error, you can't use '--auth' and '--auth-file' together, use only one option\nNOTE: if you don't want the username and password to be stored in the 'uquix/history.log' file then use '--auth-file' option, so its better for security reasons")
            exit(0)
        if self.args.auth or self.args.auth_file is not None and self.args.auth_file.strip():
            try:
                if self.args.auth:
                    username, password = self.args.auth.split(":", 1)
                else:
                    try:
                        with open(self.args.auth_file.strip(), "r") as f:
                            username, password = f.read().strip().split(":", 1)
                    except FileNotFoundError:
                        print("[-] Error, auth file not found")
                        exit(1)
                    except Exception as e:
                        print(f"[-] Error in auth file. Makesure username and password format is 'USERNAME:PASSWORD'. {e}")
                        exit(1)
                self.HTTP_AUTH = aiohttp.BasicAuth(username, password)
            except ValueError:
                print("[-] Error: '--auth' must be formatted as 'USERNAME:PASSWORD'")
                exit(1)
        else:
            self.HTTP_AUTH = None
        self.REAL_URL = self.args.real_url
        self.FINAL_URL = self.args.final_url
        if self.REAL_URL and self.FINAL_URL:
            print("[-] Error, '--real-url' and '--final-url' can't be used together, use only one option")
            exit(0)
        self.ONLY_RESPONSES = set(int(s.strip()) for s in self.args.only.split(",")) if self.args.only else None
        self.SKIP_RESPONSES = set(int(s.strip()) for s in self.args.skip.split(",")) if self.args.skip else None
        self.ONLY_2XX = self.args.only_2xx
        self.ONLY_3XX = self.args.only_3xx
        self.ONLY_4XX = self.args.only_4xx
        self.ONLY_5XX = self.args.only_5xx
        self.LESS_400_RESP = self.args.less_400
        if sum(1 for arg in [self.ONLY_RESPONSES, self.ONLY_2XX, self.ONLY_3XX, self.ONLY_4XX, self.ONLY_5XX, self.LESS_400_RESP] if arg) > 1:
            print("[-] Error, you can use only one option from these: '--only', '--only-2xx', '--only-3xx', '--only-4xx', '--only-5xx', '--less-400'")
            exit(0)
        if self.ONLY_RESPONSES and self.SKIP_RESPONSES:
            print("[-] Error, you can't use '--only' and '--skip' together, use only one option")
            exit(0)
        self.NO_EMPTY_CONTENT = self.args.no_empty_content
        self.MAX_CONTENT = self.args.max_content
        if self.MAX_CONTENT is not None and self.MAX_CONTENT < 0:
            print(f"[-] Error, '--max-content' must be positive integer")
            exit(0)
        self.MIN_CONTENT = self.args.min_content
        if self.MIN_CONTENT is not None and self.MIN_CONTENT < 0:
            print(f"[-] Error, '--min-content' must be positive integer")
            exit(0)
        self.RETRIES = self.args.retries
        if self.RETRIES is not None and self.RETRIES < 0:
            print("[-] Error, '--retries' must be positive integer number")
            exit(0)
        self.DNS_RETRIES = self.args.dns_retries
        if self.DNS_RETRIES is not None and self.DNS_RETRIES < 0:
            print("[-] Error, '--dns-retries' must be positive integer number")
            exit(0)
        self.REQ_RETRIES = self.args.req_retries
        if self.REQ_RETRIES is not None and self.REQ_RETRIES < 0:
            print("[-] Error, '--req-retries' must be positive integer number")
            exit(0)
        if self.DNS_RETRIES is not None and self.REQ_RETRIES is None and self.CONCURRENT_REQUESTS:
            self.REQ_RETRIES = self.RETRIES
        if self.REQ_RETRIES is not None and self.DNS_RETRIES is None and self.CONCURRENT_REQUESTS:
            self.DNS_RETRIES = self.RETRIES
        if self.DNS_RETRIES is not None or self.REQ_RETRIES is not None:
            self.RETRIES = None
        self.RETRIES_DELAY = self.args.retries_delay
        if self.RETRIES_DELAY is not None and self.RETRIES_DELAY < 0:
            print("[-] Error, '--retries-delay' must be positive number")
            exit(0)
        if self.RETRIES_DELAY is not None and not (self.RETRIES or self.REQ_RETRIES):
            print("[-] Error, retries must be bigger than 0 when using '--retries-delay'")
            exit(0)
        self.EXP_BACKOFF = self.args.exp_backoff
        if self.EXP_BACKOFF and (self.RETRIES_DELAY is not None and self.RETRIES_DELAY < 2 or self.RETRIES_DELAY is None) :
            print("[-] Error, '--retries-delay' is required when using '--exp-backoff'. In addition, 'retries-delay' must be at least 2")
            exit(0)
        if self.EXP_BACKOFF and (self.RETRIES is not None and not self.RETRIES or self.REQ_RETRIES is not None and not self.REQ_RETRIES):
            print("[-] Error, retries must be bigger than 0 when using 'exp-backoff'")
            exit(0)
        if self.CONCURRENT_REQUESTS and self.OUTPUT_DIR:
            self.IS_EXIST_DIR = os.path.exists(self.OUTPUT_DIR)
            if not self.IS_EXIST_DIR:
                os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        self.ADD_HTTP = self.args.add_http
        self.ADD_HTTPS = self.args.add_https
        self.PORTS = set(int(p.strip()) for p in self.args.ports.split(",")) if self.args.ports else None
        self.PORTS_HTTP = set(int(p.strip()) for p in self.args.ports_http.split(",")) if self.args.ports_http else None
        self.PORTS_HTTPS = set(int(p.strip()) for p in self.args.ports_https.split(",")) if self.args.ports_https else None
        if self.PORTS and (self.PORTS_HTTP or self.PORTS_HTTPS):
            print("[-] Error, you can't use '--ports-http' or '--ports-https' when using '--ports'")
            exit(0)
        self.DISABLE_PROGRESS = self.args.disable_progress
        self.DETAILED_PROGRESS = self.args.disable_detailed_progress if not self.DISABLE_PROGRESS else False
        self.NOT_FASTER = self.args.no_max_speed
        self.colors = {
            "reset": "\033[0m",
            "timestamp": "\033[90m",  # Gray
            "id": "\033[90m",         # Gray
            "method": "\033[94m",     # Blue
            "status_2xx": "\033[92m", # Bright Green
            "status_3xx": "\033[93m", # Yellow
            "status_4xx": "\033[31m", # Red
            "status_403": "\033[91m", # Orange \033[38;5;214m
            "status_5xx": "\033[91;1m", # Bright Red
            "size": "\033[95m",       # Magenta
            "payld_size": "\033[38;5;214m",
            "req_hdrs": "\033[38;2;255;184;108m",
            "res_hdrs": "\033[93m",
            "url": "\033[37;1m",      # Bright Gray
            "cyanurl": "\033[96;1m",  # Bright Cyan
            "title": "\033[37m",      # Little Brighter than timestamp
            "progress": "\033[36m",   # Little Dark Cyan
            "cols": "\033[1;33m",     # gold
            "out": "\033[1;35m",      # Bold Magenta
            "dur": "\033[33m"
        }
        self.red_bg = "\033[41m"
        if self.NO_COLORS:
            for color in self.colors:
                self.colors[color] = ""
            self.red_bg = ""
        self.analyse_by = self.args.analyze_by.strip() if self.args.analyze_by and not self.args.no_analyze else None
        self.NO_ANALYZE = self.args.no_analyze
        if self.NO_ANALYZE and self.args.output_analyze:
            print("[-] Error, can't set '--output-analyze' when disabling analyzing")
            exit(0)
        if self.args.analyze_by and self.NO_ANALYZE:
            print("[-] Error, can't set analyzing logic when disabling analyzing")
            exit(0)
        if self.analyse_by and not self.NO_ANALYZE:
            if not any(w in self.analyse_by.lower() for w in ["status", "content", "method", "title", "duration", "payload_size", "req_hdrs", "req_hdrs_size", "res_hdrs", "res_hdrs_size"]):
                print("[-] Error, invalid analyzing logic")
                exit(0)
        if not self.analyse_by and self.CONCURRENT_REQUESTS and not self.NO_ANALYZE:
            self.analyse_by = "STATUS and CONTENT and METHOD and TITLE or STATUS and CONTENT and METHOD or STATUS and CONTENT and TITLE or STATUS and METHOD and TITLE or CONTENT and METHOD and TITLE or STATUS and CONTENT or STATUS and METHOD or STATUS and TITLE or CONTENT and METHOD or CONTENT and TITLE or METHOD and TITLE or STATUS or CONTENT or TITLE or METHOD or RES_HDRS and RES_HDRS_SIZE or RES_HDRS or RES_HDRS_SIZE or REQ_HDRS and REQ_HDRS_SIZE or REQ_HDRS or REQ_HDRS_SIZE or PAYLOAD_SIZE or DURATION"
        if any([self.DNS_RETRIES, self.DNS_TIMEOUT, self.UDP_PORT, self.TCP_PORT, self.FLAGS, self.SOCKET_SBS, self.SOCKET_RBS, self.ENABLE_ROTATE,
        self.BIND_IP_DNS, self.NET_DEV, self.RESOLVCONF_PATH]) and not (self.CUSTOM_RESOLVERS or self.CUSTOM_RESOLVERS_FILE) and self.CONCURRENT_REQUESTS:
            print("[-] Error, '--dns-servers' or '--dns-servers-file' is required when using any of DNS arguments:\n\t'--dns-retries', '--dns-timeout', '--udp-port', '--tcp-port', '--flags', '--socket-sbs', '--socket-rbs', '--enable-rotate', '--bind-ip-dns', '--net-dev', '--resolvconf'")
            exit(0)


    async def aprint(self, msg, end="\n"):

        msg = f"{msg}{end}"
        sys.__stdout__.write(msg)
        sys.__stdout__.flush()


    def about_resolver(self) -> aiodns.DNSResolver | None:

        try:
            if self.CUSTOM_RESOLVERS and self.CUSTOM_RESOLVERS_FILE:
                print("\n[-] Error, u r importing dns servers from a file and from a string, import only from one source, default dns servers will be used now\n")
            elif self.CUSTOM_RESOLVERS or self.CUSTOM_RESOLVERS_FILE:
                if self.CUSTOM_RESOLVERS:
                    if isinstance(self.CUSTOM_RESOLVERS, str):
                        if ("[" and "]") not in self.CUSTOM_RESOLVERS:
                            self.resolvers_list = self.CUSTOM_RESOLVERS.split(",")
                        else:
                            before = self.CUSTOM_RESOLVERS.replace("[", "").replace("]", "").replace("'","").replace('"','')
                            self.resolvers_list = before.split(",")
                    else:
                        self.resolvers_list = [r.strip() for r in self.CUSTOM_RESOLVERS.split(",") if r.strip()]
                else:
                    with open(self.CUSTOM_RESOLVERS_FILE, "r") as f:
                        self.resolvers_list = [r.strip() for r in f.readlines() if r.strip()]
                return aiodns.DNSResolver(
                    nameservers=self.resolvers_list,
                    timeout=self.TIMEOUT if self.TIMEOUT is not None else self.DNS_TIMEOUT,
                    tries=self.RETRIES if self.RETRIES is not None else self.DNS_RETRIES,
                    udp_port=self.UDP_PORT if self.UDP_PORT is not None else 53,
                    tcp_port=self.TCP_PORT if self.TCP_PORT is not None else 53,
                    flags=self.FLAGS if self.FLAGS is not None else 0,
                    socket_send_buffer_size=self.SOCKET_SBS if self.SOCKET_SBS is not None else 0,
                    socket_receive_buffer_size=self.SOCKET_RBS if self.SOCKET_RBS is not None else 0,
                    rotate=self.ENABLE_ROTATE,
                    local_ip=self.BIND_IP_DNS,
                    local_dev=self.NET_DEV,
                    resolvconf_path=self.RESOLVCONF_PATH
                )
        except Exception as e:
            print(f"\n[-] Error in dns servers, system's default dns servers will be used now. {e}\n")
        if self.CONCURRENT_QUERIES:
            return aiodns.DNSResolver(
                nameservers=["1.1.1.1","8.8.8.8","1.0.0.1","8.8.4.4","9.9.9.9","149.112.112.112","208.67.222.222","208.67.220.220","45.90.28.0","185.222.222.222"],
                timeout=self.TIMEOUT if self.TIMEOUT is not None else self.DNS_TIMEOUT,
                tries=self.RETRIES if self.RETRIES is not None else self.DNS_RETRIES,
                udp_port=self.UDP_PORT if self.UDP_PORT is not None else 53,
                tcp_port=self.TCP_PORT if self.TCP_PORT is not None else 53,
                flags=self.FLAGS if self.FLAGS is not None else 0,
                socket_send_buffer_size=self.SOCKET_SBS if self.SOCKET_SBS is not None else 0,
                socket_receive_buffer_size=self.SOCKET_RBS if self.SOCKET_RBS is not None else 0,
                rotate=self.ENABLE_ROTATE,
                local_ip=self.BIND_IP_DNS,
                local_dev=self.NET_DEV,
                resolvconf_path=self.RESOLVCONF_PATH
            )
        else:
            return None


    def ssl_settings(self) -> ssl.SSLContext | aiohttp.Fingerprint | bool:

        context = ssl.create_default_context()

        try:
            if not self.NO_SSL:
                if self.SSL_CERT and self.SSL_KEY:
                    context.load_cert_chain(certfile=self.SSL_CERT, keyfile=self.SSL_KEY)
                if self.CA_CERT:
                    context.load_verify_locations(cafile=self.CA_CERT)
                if self.FINGERPRINT or self.FINGERPRINT_FILE:
                    if self.FINGERPRINT and self.FINGERPRINT_FILE:
                        raise ValueError("\n[-] Error, provide either FINGERPRINT or FINGERPRINT_FILE, not both\n")
                    if self.FINGERPRINT:
                        fp = self.FINGERPRINT
                    else:
                        with open(self.FINGERPRINT_FILE, "r") as f:
                            fp = f.read().strip()
                
                    fp_bytes = bytes.fromhex(fp.replace(":", "").replace(" ", ""))
                    return aiohttp.Fingerprint(fp_bytes)
                else:
                    return context
            else:
                return False
        except FileNotFoundError:
            print("\n[-] Error: SSL cert file or SSL key file or CA cert file or fingerprint file NOT FOUND\n")
        except ValueError as e:
            print(f"\n[-] Error: Invalid fingerprint format or file reading failed. {e}\n")
        except ssl.SSLError as e:
            print(f"\n[-] Error with SSL cert/key and/or CA cert: {e}\n")
        except Exception as e:
            print(f"\n[-] Unexpected error about SSL: {e}\n")

        return context


    def cookiejar_settings(self) -> aiohttp.DummyCookieJar | aiohttp.CookieJar:

        if self.IGNORE_COOKIES:
            return aiohttp.DummyCookieJar()
        else:
            jar = aiohttp.CookieJar(unsafe=self.ALLOW_UNSAFE_COOKIES)
            try:
                if self.SPECIFIC_COOKIES:
                    for spe_cookies in self.SPECIFIC_COOKIES.split('|'):
                        site, cookies_str = spe_cookies.strip().split(';', 1)
                        cookies_dict = dict(item.strip().split('=') for item in cookies_str.strip().split(','))
                        jar.update_cookies(cookies_dict, response_url=site.strip())
            except ValueError as e:
                print(f"\n[-] Error parsing specific cookies: {e}\n")
            except Exception as e:
                print(f"\n[-] Unexpected error about cookies: {e}\n")
            finally:
                return jar


    async def generate_headers(self) -> dict[str, str]:

        if self.USE_RANDOM_HEADERS is not None:
            headers = await MyMainHeaders(self.headersrules).mainheads(self.USE_RANDOM_AGENTS, self.USE_RANDOM_HEADERS, self.NO_403)
        if self.CUSTOM_HEADERS or self.FILE_CUSTOM_HEADERS:
            try:
                headers.update(self.CONTENT_CUSTOM_HEADERS or self.CONTENT_FILE_CUSTOM_HEADERS)
            except Exception as e:
                print(f"[-] Error while importing the custom headers: {e}")
                exit(1)

        return headers


    async def detect_wildcard(self, domain, resolver, test_count=3) -> None:

        ip_results = list()

        if "://" in domain:
            print(f"[-] Error, '{domain}' isn't a valid domain, remove the protocol type")
            exit(0)
        for _ in range(test_count):
            random_subdomain = "".join(random.choices(string.ascii_lowercase, k=12))
            test_domain = f"{random_subdomain}.{domain}"

            try:
                result = await resolver.query(test_domain, "A")
                ips = {answer.host for answer in result}
                ip_results.append(ips)
            except aiodns.error.DNSError:
                continue

        common_ips = set.intersection(*ip_results) if ip_results else set()
        if common_ips:
            self.wildcard_ips.update(common_ips)
        if not self.SILENCE:
            await print(f"[!] Wildcard IPs detected: {self.wildcard_ips}") if self.wildcard_ips else None


    async def dns_brute_force_function(self, domain, semaphore, resolver, subdomain, total, idx) -> None:

        runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))
        
        if not self.DISABLE_PROGRESS:
            await self.aprint(f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} - {runtime}{' '*20}{self.colors['reset']}", end="\r")

        target = f"{subdomain}.{domain}"
        try:
            async with semaphore:
                result = await resolver.query(target, "A")
                resolved_ips = [answer.host for answer in result]
                if not self.wildcard_ips.intersection(resolved_ips):
                    if self.SHOW_RECORDS or self.SHOW_ONLY_CNAME:
                        resolved_ips = list() if self.SHOW_ONLY_CNAME and not self.SHOW_RECORDS and not self.SHOW_ONLY_A else resolved_ips
                        try:
                            cname_result = await resolver.query(target, "CNAME")
                            resolved_ips.append(cname_result.cname)
                            while cname_result.cname:
                                cname_result = await resolver.query(cname_result.cname, "CNAME")
                                resolved_ips.append(cname_result.cname)
                        except aiodns.error.DNSError:
                            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))
                            if not self.DISABLE_PROGRESS:
                                await self.aprint(f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} - {runtime}{' '*20}{self.colors['reset']}", end="\r")
                    if self.OUTPUT:
                        async with aiofiles.open(self.OUTPUT, "a") as outputfile:
                            await outputfile.write(
                                f"{target}{f' -> {resolved_ips}' if resolved_ips else ''}\n" if self.SHOW_RECORDS or self.SHOW_ONLY_A or self.SHOW_ONLY_CNAME else f"{target}\n"
                            )
                    if not self.SILENCE:
                        await self.aprint(
                            f"{self.colors['url']}{target}{self.colors['reset']}{f' -> {self.colors['status_2xx']}{resolved_ips}{self.colors['reset']}' if resolved_ips else ''}{' '*60}" if self.SHOW_RECORDS or self.SHOW_ONLY_A or self.SHOW_ONLY_CNAME else f"{self.colors['url']}{target}{self.colors['reset']}{' '*70}"
                        )
                    self.ALL_SUBDOMAINS.append(target)

                    runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))
                    if not self.DISABLE_PROGRESS:
                        await self.aprint(f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} - {runtime}{' '*20}{self.colors['reset']}", end="\r")
        except aiodns.error.DNSError:
            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))
            if not self.DISABLE_PROGRESS:
                await self.aprint(f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} - {runtime}{' '*20}{self.colors['reset']}", end="\r")
        except Exception as e:
            await self.aprint(f"[-] Unexpected error when resolving: {e}{' '*20}")


    async def response_brute_force_function(self, method, semaphore, client, subdomain, total, idx) -> None:

        target = subdomain

        if self.DISABLE_REDIRECT_HTTP and target.startswith("http://") and not self.DISABLE_REDIRECT:
            disable_redirect = True
        elif self.DISABLE_REDIRECT_HTTPS and target.startswith("https://") and not self.DISABLE_REDIRECT:
            disable_redirect = True
        else:
            disable_redirect = self.DISABLE_REDIRECT
    
        if self.MAX_REDIRECTS_HTTP is not None and target.startswith("http://") and not self.DISABLE_REDIRECT and not self.DISABLE_REDIRECT_HTTP and self.MAX_REDIRECTS is None:
            max_redirect = self.MAX_REDIRECTS_HTTP
        elif self.MAX_REDIRECTS_HTTPS is not None and target.startswith("https://") and not self.DISABLE_REDIRECT and not self.DISABLE_REDIRECT_HTTPS and self.MAX_REDIRECTS is None:
            max_redirect = self.MAX_REDIRECTS_HTTPS
        else:
            max_redirect = self.MAX_REDIRECTS if self.MAX_REDIRECTS is not None else 10

        for _ in range(self.NUMS_OF_RANDOM_HEADERS if self.NOT_FASTER else 1):
            headers = await self.generate_headers()
            payload = random.choice(self.PAYLOADS).replace(b"METHOD", method.encode()).replace(b"example.com", target.split("://")[-1].split("/")[0].encode()) if self.RANDOM_DATA and method in self.DATA_METHODS else None
            async with semaphore:
                for attempt in range(-1, self.RETRIES if self.RETRIES is not None else self.REQ_RETRIES):
                    start_perf = time.perf_counter()
                    try:
                        async with client.request(
                            method,
                            target,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(
                                total=self.TIMEOUT if self.TIMEOUT is not None else self.REQ_TIMEOUT,
                                connect=self.CONNECT_TIMEOUT,
                                sock_connect=self.SOCK_CONNECT_TIMEOUT,
                                sock_read=self.SOCK_READ_TIMEOUT
                            ),
                            params=self.PARAMS,
                            data=self.DATA_PAYLOAD if self.DATA_PAYLOAD and not self.RANDOM_DATA and method in self.DATA_METHODS else payload,
                            allow_redirects=not disable_redirect,
                            max_redirects=max_redirect
                        ) as response:

                            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))

                            if not self.DISABLE_PROGRESS:
                                if self.DETAILED_PROGRESS:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: [ALL] {idx}/{total}/{len(self.ALL_SUBDOMAINS)}/{self.ALL_REQUESTS}/{self.TOTAL_FAILED_REQS} - {runtime} | "
                                        f"[HTTP] {len(self.ALL_HTTP_SUBDOMAINS)}/{len(self.UNIQUE_HTTP)}/{self.ALL_HTTP_REQUESTS}/{self.HTTP_FAILED_REQS} | "
                                        f"[HTTPS] {len(self.ALL_HTTPS_SUBDOMAINS)}/{len(self.UNIQUE_HTTPS)}/{self.ALL_HTTPS_REQUESTS}/{self.HTTPS_FAILED_REQS}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )
                                else:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} / {self.ALL_REQUESTS} / {self.TOTAL_FAILED_REQS} - {runtime}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )

                            content = await response.text()

                            end_perf = time.perf_counter()
                            final_perf = f" [{end_perf - start_perf:.4f}s]" if not self.NO_TIME else ""

                            if self.ONLY_RESPONSES:
                                assert response.status in self.ONLY_RESPONSES, "itsAssertionError"
                            if self.SKIP_RESPONSES and not self.ONLY_RESPONSES:
                                assert response.status not in self.SKIP_RESPONSES, "itsAssertionError"
                            if self.ONLY_2XX:
                                assert 300 > response.status >= 200, "itsAssertionError"
                            if self.ONLY_3XX:
                                assert 400 > response.status >= 300, "itsAssertionError"
                            if self.ONLY_4XX:
                                assert 500 > response.status >= 400, "itsAssertionError"
                            if self.ONLY_5XX:
                                assert 600 > response.status >= 500, "itsAssertionError"
                            if self.LESS_400_RESP:
                                assert response.ok, "itsAssertionError"
                            if self.NO_EMPTY_CONTENT:
                                assert len(content) > 0, "itsAssertionError"
                            if self.MAX_CONTENT:
                                assert len(content) <= self.MAX_CONTENT, "itsAssertionError"
                            if self.MIN_CONTENT:
                                assert len(content) >= self.MIN_CONTENT, "itsAssertionError"

                            response_status_code = response.status

                            self.ALL_REQUESTS+=1

                            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))

                            if not self.DISABLE_PROGRESS:
                                if self.DETAILED_PROGRESS:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: [ALL] {idx}/{total}/{len(self.ALL_SUBDOMAINS)}/{self.ALL_REQUESTS}/{self.TOTAL_FAILED_REQS} - {runtime} | "
                                        f"[HTTP] {len(self.ALL_HTTP_SUBDOMAINS)}/{len(self.UNIQUE_HTTP)}/{self.ALL_HTTP_REQUESTS}/{self.HTTP_FAILED_REQS} | "
                                        f"[HTTPS] {len(self.ALL_HTTPS_SUBDOMAINS)}/{len(self.UNIQUE_HTTPS)}/{self.ALL_HTTPS_REQUESTS}/{self.HTTPS_FAILED_REQS}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )
                                else:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} / {self.ALL_REQUESTS} / {self.TOTAL_FAILED_REQS} - {runtime}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )

                            if self.REAL_URL:
                                target = str(response.url)
                            elif self.FINAL_URL:
                                target = str(response.real_url)

                            if not self.NO_TITLES:
                                if content:
                                    first_title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                                    page_title = first_title_match.group(1) if first_title_match else "No title found"
                                else:
                                    page_title = False
                            else:
                                page_title = False
                            page_title = f" \"{page_title}\"" if page_title else ""
                            payload_size_var = ""
                            if not self.NO_PAYLOAD_SIZE and method not in self.DATA_METHODS:
                                payload_size_var = " [No_Payload]"
                            elif not self.NO_PAYLOAD_SIZE and method in self.DATA_METHODS:
                                payload_size_var = f" [{len(self.DATA_PAYLOAD)}b]" if self.DATA_PAYLOAD and not self.RANDOM_DATA else f" [{len(payload)}b]"
                            request_headers_num = f" ({len(headers)})" if not self.NO_REQUEST_HEADERS else ""
                            response_headers_num = f" ({len(response.headers)})" if not self.NO_RESPONSE_HEADERS else ""
                            request_headers_size = f" {{{len(", ".join([f"{key}: {value}" for key, value in headers.items()]))}b}}" if not self.NO_REQUEST_HEADERS_SIZE else ""
                            response_headers_size = f" {{{len(", ".join([f"{key}: {value}" for key, value in response.headers.items()]))}b}}" if not self.NO_RESPONSE_HEADERS_SIZE else ""
                            if self.OUTPUT:
                                async with aiofiles.open(self.OUTPUT, "a") as outputfile:
                                    await outputfile.write(
                                        f"[{runtime}] [{self.ALL_REQUESTS},{idx}] [{method}] {target} [{response_status_code}]{f" ({len(content)}b)" if not self.NO_CONTENT_SIZE else ""}{payload_size_var}{request_headers_num}{request_headers_size}{response_headers_num}{response_headers_size}{final_perf}{page_title} | REQUEST-HEADERS: {headers}{" || RESPONSE-HEADERS: '"+", ".join([f"{key}: {value}" for key, value in response.headers.items()])+"'" if self.NO_RESPONSE_HEADERS_SAVING else ''}{f" ||| REQUEST-DATA: {self.DATA_PAYLOAD if not self.RANDOM_DATA else payload}" if not self.NO_DATA_SAVING and self.DATA_PAYLOAD and method in self.DATA_METHODS else ''}\n"
                                    )
                            if self.OUTPUT_DIR:
                                full_html_path = os.path.join(
                                    self.OUTPUT_DIR,
                                    f"{self.ALL_REQUESTS}_{idx}_{method}__{target.replace("://", "_")}__{response_status_code}_{len(content)}b.html"
                                )
                                async with aiofiles.open(full_html_path, "w") as outputdir:
                                    await outputdir.write(content)

                            self.ALL_SORTED_RESULTS.append(
                                f"[{runtime}] [{self.ALL_REQUESTS},{idx}] [{method}] {target} [{response_status_code}]{f" ({len(content)}b)" if not self.NO_CONTENT_SIZE else ""}{payload_size_var}{request_headers_num}{request_headers_size}{response_headers_num}{response_headers_size}{final_perf}{page_title}"
                            )

                            if not self.SILENCE:
                                if 200 <= response_status_code < 300:
                                    status_color = self.colors["status_2xx"]
                                elif 300 <= response_status_code < 400:
                                    status_color = self.colors["status_3xx"]
                                elif 400 <= response_status_code < 500:
                                    status_color = self.colors["status_403"] if response_status_code == 403 else self.colors["status_4xx"]
                                elif 500 <= response_status_code < 600:
                                    status_color = self.colors["status_5xx"]
                                else:
                                    status_color = self.colors["reset"]
                                formatted_output = (
                                    f"{self.colors['timestamp']}[{runtime}]{self.colors['reset']} "
                                    f"{self.colors['id']}[{self.ALL_REQUESTS},{idx}]{self.colors['reset']} "
                                    f"{self.colors['method']}[{method}]{self.colors['reset']} "
                                    f"{self.colors['url']}{target}{self.colors['reset']} "
                                    f"{status_color}[{response_status_code}]{self.colors['reset']}"
                                    f"{self.colors['size']}{f" ({len(content)}b)" if not self.NO_CONTENT_SIZE else ""}{self.colors['reset']}{self.colors['payld_size']}{payload_size_var}{self.colors['reset']}{self.colors['req_hdrs']}{request_headers_num}{request_headers_size}{self.colors['reset']}{self.colors['res_hdrs']}{response_headers_num}{response_headers_size}{self.colors['reset']}{self.colors['dur']}{final_perf}{self.colors['reset']}{self.colors['title']+page_title+self.colors['reset'] if page_title else ' '*10}"
                                )
                                await self.aprint(formatted_output)

                            self.ALL_SUBDOMAINS.add(subdomain)

                            if self.DETAILED_PROGRESS:
                                if subdomain.startswith("http://"):
                                    self.ALL_HTTP_SUBDOMAINS.append(subdomain)
                                    self.UNIQUE_HTTP.add(subdomain)
                                elif subdomain.startswith("https://"):
                                    self.ALL_HTTPS_SUBDOMAINS.append(subdomain)
                                    self.UNIQUE_HTTPS.add(subdomain)

                            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))

                            if not self.DISABLE_PROGRESS:
                                if self.DETAILED_PROGRESS:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: [ALL] {idx}/{total}/{len(self.ALL_SUBDOMAINS)}/{self.ALL_REQUESTS}/{self.TOTAL_FAILED_REQS} - {runtime} | "
                                        f"[HTTP] {len(self.ALL_HTTP_SUBDOMAINS)}/{len(self.UNIQUE_HTTP)}/{self.ALL_HTTP_REQUESTS}/{self.HTTP_FAILED_REQS} | "
                                        f"[HTTPS] {len(self.ALL_HTTPS_SUBDOMAINS)}/{len(self.UNIQUE_HTTPS)}/{self.ALL_HTTPS_REQUESTS}/{self.HTTPS_FAILED_REQS}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )
                                else:
                                    await self.aprint(
                                        f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} / {self.ALL_REQUESTS} / {self.TOTAL_FAILED_REQS} - {runtime}{' '*20}{self.colors['reset']}",
                                        end="\r"
                                    )

                            break

                    except (OSError, BrokenPipeError, ConnectionResetError, aiohttp.ClientConnectorError, aiohttp.ClientConnectionError, aiohttp.ClientOSError, aiohttp.ClientError, asyncio.TimeoutError, aiohttp.ClientSSLError, aiohttp.TooManyRedirects, AssertionError) as e:

                        self.TOTAL_FAILED_REQS+=1
                        if self.DETAILED_PROGRESS:
                            if target.startswith("http://"):
                                self.HTTP_FAILED_REQS+=1
                            elif target.startswith("https://"):
                                self.HTTPS_FAILED_REQS+=1

                        runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))

                        if not self.DISABLE_PROGRESS:
                            if self.DETAILED_PROGRESS:
                                await self.aprint(
                                    f"  {self.colors['progress']}Progress: [ALL] {idx}/{total}/{len(self.ALL_SUBDOMAINS)}/{self.ALL_REQUESTS}/{self.TOTAL_FAILED_REQS} - {runtime} | "
                                    f"[HTTP] {len(self.ALL_HTTP_SUBDOMAINS)}/{len(self.UNIQUE_HTTP)}/{self.ALL_HTTP_REQUESTS}/{self.HTTP_FAILED_REQS} | "
                                    f"[HTTPS] {len(self.ALL_HTTPS_SUBDOMAINS)}/{len(self.UNIQUE_HTTPS)}/{self.ALL_HTTPS_REQUESTS}/{self.HTTPS_FAILED_REQS}{' '*20}{self.colors['reset']}",
                                    end="\r"
                                )
                            else:
                                await self.aprint(
                                    f"  {self.colors['progress']}Progress: {idx} / {total} / {len(self.ALL_SUBDOMAINS)} / {self.ALL_REQUESTS} / {self.TOTAL_FAILED_REQS} - {runtime}{' '*20}{self.colors['reset']}",
                                    end="\r"
                                )

                        if isinstance(e, AssertionError):
                            break

                        if (self.RETRIES is not None and attempt < self.RETRIES-1) or (self.REQ_RETRIES is not None and attempt < self.REQ_RETRIES-1):
                            if self.RETRIES_DELAY is not None and self.RETRIES_DELAY >= 0 and (self.RETRIES or self.REQ_RETRIES) > 0:
                                if self.EXP_BACKOFF:
                                    await asyncio.sleep(self.RETRIES_DELAY * 2 ** (attempt+1))
                                else:
                                    await asyncio.sleep(self.RETRIES_DELAY)
                            continue
                        else:
                            break
                    except Exception as e:
                        if e == "reentrant call inside <_io.BufferedWriter name='<stdout>'>":
                            raise KeyboardInterrupt
                        else:
                            await self.aprint(f"[-] Unexpected error when sending request: {e}{' '*30}")

        return


    def which_connector(self, resolver) -> aiohttp.TCPConnector | aiohttp_socks.ChainProxyConnector:

        now_resolve = aiohttp.AsyncResolver(resolver) if resolver else None
        about_ssl = self.ssl_settings()

        if self.PROXY or self.SOCKS_PROXY:
            proxies = list()
            try:
                if self.NO_RDNS and not self.SOCKS_PROXY:
                    print(f"\n[!] Warning: --no-rdns will be ignored, cause there's no SOCKS-PROXY\n")
                if self.PROXY:
                    proxies.append(self.PROXY)
                if self.SOCKS_PROXY:
                    proxies.append(self.SOCKS_PROXY)
                if self.ROUTE_SOCKS_FIRST and self.PROXY and self.SOCKS_PROXY:
                    if proxies.index(self.SOCKS_PROXY) > proxies.index(self.PROXY):
                        proxies.reverse()

                return aiohttp_socks.ChainProxyConnector.from_urls(
                    proxies,
                    rdns=not self.NO_RDNS,
                    resolver=now_resolve,
                    limit=self.LIMIT if self.args.max_connections is not None else 100,
                    limit_per_host=self.LIMIT_PER_HOST if self.LIMIT_PER_HOST is not None else 0,
                    enable_cleanup_closed=True,
                    ssl=about_ssl,
                    keepalive_timeout=self.KEEPALIVE_TIMEOUT if self.KEEPALIVE_TIMEOUT is not None else 30.0,
                    use_dns_cache=not self.NO_DNS_CACHE,
                    ttl_dns_cache=self.TTL_DNS_CACHE if self.TTL_DNS_CACHE is not None else 10,
                    local_addr=self.BIND
                )

            except Exception as e:
                print(f"\n[-] Proxy Error: {e}\n")
                exit(1)
        else:
            return aiohttp.TCPConnector(
                resolver=now_resolve,
                limit=self.LIMIT if self.args.max_connections is not None else 100,
                limit_per_host=self.LIMIT_PER_HOST if self.LIMIT_PER_HOST is not None else 0,
                enable_cleanup_closed=True,
                ssl=about_ssl,
                keepalive_timeout=self.KEEPALIVE_TIMEOUT if self.KEEPALIVE_TIMEOUT is not None else 30.0,
                use_dns_cache=not self.NO_DNS_CACHE,
                ttl_dns_cache=self.TTL_DNS_CACHE if self.TTL_DNS_CACHE is not None else 10,
                local_addr=self.BIND
            )


    async def worker(self, semaphore, subdomains, resolver, total) -> None:

        tasks = list()

        print(" >Creating tasks, wait a second...", end="\r", flush=True)

        try:
            if self.CONCURRENT_QUERIES:
                for idx,sub in enumerate(subdomains, 1):
                    if self.DOMAINS:
                        for domain in self.DOMAINS:
                            tasks.append(asyncio.create_task(self.dns_brute_force_function(domain, semaphore, resolver, sub, total, idx)))
                    else:
                        tasks.append(asyncio.create_task(self.dns_brute_force_function(self.TARGET_DOMAIN, semaphore, resolver, sub, total, idx)))

                await asyncio.gather(*tasks, return_exceptions=True)

            else:
                if self.USE_RANDOM_HEADERS is not None:
                    await MyMainHeaders(self.headersrules).validate_rules()
                about_cookie_jar = self.cookiejar_settings()
                conn = self.which_connector(resolver)
                async with aiohttp.ClientSession(
                    connector=conn,
                    connector_owner=True,
                    cookies=self.COOKIES,
                    cookie_jar=about_cookie_jar,
                    auth=self.HTTP_AUTH,
                    read_bufsize=self.BUFFER_SIZE if self.BUFFER_SIZE is not None else 2**16
                ) as session:
                    for idx,sub in enumerate(subdomains, 1):
                        for method in self.METHODS.split(","):
                            if self.NOT_FASTER:
                                tasks.append(asyncio.create_task(self.response_brute_force_function(method, semaphore, session, sub, total, idx)))
                            else:
                                for _ in range(self.NUMS_OF_RANDOM_HEADERS):
                                    tasks.append(asyncio.create_task(self.response_brute_force_function(method, semaphore, session, sub, total, idx)))

                    await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.exceptions.CancelledError:
            for t in tasks:
                t.cancel()
        except asyncio.exceptions.InvalidStateError:
            pass
        finally:
            await asyncio.gather(*tasks, return_exceptions=True)


    def parse_req(self, log) -> dict:

        pattern = r"""
            \[ (?P<time>[^\]]+) \]\s*
            \[ (?P<request_id>[^\]]+) \]\s*
            \[ (?P<method>[^\]]+) \]\s+
            (?P<url>\S+)\s+
            \[ (?P<status>\d+) \]\s*
            (?:\((?P<size>\d+)b\))?\s*
            (?:\[(?P<payload_size>.*?)\])?\s*
            (?:\((?P<req_hdrs>\d+)\))?\s*
            (?:\{(?P<req_hdrs_size>\d+)b\})?\s*
            (?:\((?P<res_hdrs>\d+)\))?\s*
            (?:\{(?P<res_hdrs_size>\d+)b\})?\s*
            (?:\[(?P<dur>[\d\.]+)s\])?\s*
            (?:"(?P<title>.*)")?\s*$
        """
        match = re.search(pattern, log, re.VERBOSE)
        if not match:
            raise ValueError(f"[-] Analyzing Error, format incorrect: {log}")
        groups = match.groupdict()
        return {
            "time": groups["time"].strip(),
            "request_id": groups["request_id"].strip(),
            "method": groups["method"].strip(),
            "domain": groups["url"].strip(),
            "status": int(groups["status"].strip()),
            "content": int(groups["size"].strip()) if not self.NO_CONTENT_SIZE else None,
            "payload_size": groups["payload_size"] if not self.NO_PAYLOAD_SIZE else None,
            "req_hdrs": groups["req_hdrs"] if not self.NO_REQUEST_HEADERS else None,
            "req_hdrs_size": groups["req_hdrs_size"] if not self.NO_REQUEST_HEADERS_SIZE else None,
            "res_hdrs": groups["res_hdrs"] if not self.NO_RESPONSE_HEADERS else None,
            "res_hdrs_size": groups["res_hdrs_size"] if not self.NO_RESPONSE_HEADERS_SIZE else None,
            "duration": groups["dur"] if not self.NO_TIME else None,
            "title": groups["title"] if groups.get("title") else "",
            "different": False,
            "triggered": set() 
        }


    def process_condition(self, analyse_by) -> list:

        analyse_by = analyse_by.lower().strip()
        or_groups = re.split(r'\s*or\s*', analyse_by)
        result = []
        for group in or_groups:
            sub_fields = re.split(r'\s*and\s*', group)
            sub_fields = [field.strip() for field in sub_fields if field.strip()]
            result.append(sub_fields)

        return result


    def mark_diff(self, requests, condition_groups) -> set:

        for req1, req2 in combinations(requests, 2):
            for group in condition_groups:
                valid_fields = [f for f in group if f in {"status", "content", "method", "title", "duration", "payload_size", "res_hdrs", "req_hdrs", "req_hdrs_size", "res_hdrs_size"}]
                if not valid_fields:
                    continue
                if all(req1[field] != req2[field] for field in valid_fields):
                    chosen_group = set(valid_fields)
                    for req in requests:
                        req["different"] = True
                        req["triggered"] = chosen_group
                    return chosen_group
        return set()


    def format_req(self, req, domain_triggered) -> str:

        timestamp_str = f"{self.colors['timestamp']}[{req['time']}] {self.colors['reset']}"
        id_str = f"{self.colors['id']}[{req['request_id']}] {self.colors['reset']}"
        if "method" in domain_triggered:
            method_str = f"{self.red_bg}[{req['method']}]{self.colors['reset']}"
        else:
            method_str = f"{self.colors['method']}[{req['method']}]{self.colors['reset']}"
        url_str = f"{self.colors['url']}{req['domain']}{self.colors['reset']}"
        s = req['status']
        if "status" in domain_triggered:
            status_str = f"{self.red_bg}[{s}]{self.colors['reset']}"
        else:
            if s == 403:
                stat_color = self.colors["status_403"]
            elif 200 <= s < 300:
                stat_color = self.colors["status_2xx"]
            elif 300 <= s < 400:
                stat_color = self.colors["status_3xx"]
            elif 400 <= s < 500:
                stat_color = self.colors["status_4xx"]
            elif 500 <= s < 600:
                stat_color = self.colors["status_5xx"]
            else:
                stat_color = ""
            status_str = f"{stat_color}[{s}]{self.colors['reset']}"
        c = req['content']
        if "content" in domain_triggered:
            content_str = f"{self.red_bg}({c}b){self.colors['reset']}" if c is not None else None
        else:
            content_str = f"{self.colors['size']}({c}b){self.colors['reset']}" if c is not None else None
        if "payload_size" in domain_triggered:
            p_size_str = f"{self.red_bg}[{req['payload_size']}]{self.colors['reset']}" if req['payload_size'] is not None else None
        else:
            p_size_str = f"{self.colors['payld_size']}[{req['payload_size']}]{self.colors['reset']}" if req['payload_size'] is not None else None
        if "req_hdrs" in domain_triggered:
            request_headers_str = f"{self.red_bg}({req['req_hdrs']}){self.colors['reset']}" if req['req_hdrs'] is not None else None
        else:
            request_headers_str = f"{self.colors['req_hdrs']}({req['req_hdrs']}){self.colors['reset']}" if req['req_hdrs'] is not None else None
        if "req_hdrs_size" in domain_triggered:
            request_headers_size_str = f"{self.red_bg}{{{req['req_hdrs_size']}b}}{self.colors['reset']}" if req['req_hdrs_size'] is not None else None
        else:
            request_headers_size_str = f"{self.colors['req_hdrs']}{{{req['req_hdrs_size']}b}}{self.colors['reset']}" if req['req_hdrs_size'] is not None else None
        if "res_hdrs" in domain_triggered:
            response_headers_str = f"{self.red_bg}({req['res_hdrs']}){self.colors['reset']}" if req['res_hdrs'] is not None else None
        else:
            response_headers_str = f"{self.colors['res_hdrs']}({req['res_hdrs']}){self.colors['reset']}" if req['res_hdrs'] is not None else None
        if "res_hdrs_size" in domain_triggered:
            response_headers_size_str = f"{self.red_bg}{{{req['res_hdrs_size']}b}}{self.colors['reset']}" if req['res_hdrs_size'] is not None else None
        else:
            response_headers_size_str = f"{self.colors['res_hdrs']}{{{req['res_hdrs_size']}b}}{self.colors['reset']}" if req['res_hdrs_size'] is not None else None
        if "duration" in domain_triggered:
            dur = f"{self.red_bg}[{req['duration']}s]{self.colors['reset']}"
        else:
            dur = f"{self.colors['dur']}[{req['duration']}s]{self.colors['reset']}"
        if "title" in domain_triggered:
            title_str = f'{self.red_bg}"{req["title"]}"{self.colors["reset"]}'
        else:
            title_str = f'{self.colors["title"]}"{req["title"]}"{self.colors["reset"]}' if req["title"] else ""

        return f"{timestamp_str}{id_str}{method_str} {url_str} {status_str}{' '+content_str if content_str is not None else ''}{' '+p_size_str if p_size_str is not None else ''}{' '+request_headers_str if request_headers_str is not None else ''}{' '+request_headers_size_str if request_headers_size_str is not None else ''}{' '+response_headers_str if response_headers_str is not None else ''}{' '+response_headers_size_str if response_headers_size_str is not None else ''}{' '+dur if req['duration'] is not None else ''}{' '+title_str if req['title'] else ''}"


    async def analyze_reqs(self, request_logs, analyse_by) -> None:

        parsed_requests = [self.parse_req(log) for log in request_logs]
        groups = defaultdict(list)
        for req in parsed_requests:
            groups[req["domain"]].append(req)
        condition_groups = self.process_condition(analyse_by)
        for domain, reqs in groups.items():
            if len(reqs) < 2:
                continue
            domain_triggered = self.mark_diff(reqs, condition_groups)
            if any(req["different"] for req in reqs):
                if self.OUTPUT:
                    async with aiofiles.open(self.OUTPUT_ANALYZE, "a") as f:
                        await f.write(f"[!] Differences detected for '{domain}'. {len(reqs)} Request:\n")
                print(f"{self.colors['status_403']}[!]{self.colors['reset']} {self.colors['status_3xx']}Differences detected for{self.colors['reset']} {self.colors['cyanurl']}'{domain}'{self.colors['reset']}{self.colors['status_3xx']}.{self.colors['reset']} {self.colors['url']}{len(reqs)}{self.colors['reset']} {self.colors['status_3xx']}Request:{self.colors['reset']}")
                diff_reqs = [req for req in reqs if req["different"]]
                normal_reqs = [req for req in reqs if not req["different"]]
                for req in diff_reqs:
                    if self.OUTPUT:
                        async with aiofiles.open(self.OUTPUT_ANALYZE, "a") as f:
                            await f.write(
                                f"\t[{req['time']}] [{req['request_id']}] [{req['method']}] {req['domain']} [{req['status']}]{f" ({req['content']}b)" if req.get("content") is not None else ""}{f" [{req['payload_size']}]" if req.get("payload_size") is not None else ""}{f" ({req['req_hdrs']})" if req.get("req_hdrs") is not None else ""}{f" {{{req['req_hdrs_size']}b}}" if req.get("req_hdrs_size") is not None else ""}{f" ({req['res_hdrs']})" if req.get("res_hdrs") is not None else ""}{f" {{{req['res_hdrs_size']}b}}" if req.get("res_hdrs_size") is not None else ""}{f" [{req['duration']}s]" if req.get('duration') is not None else ""}{f" \"{req['title']}\"" if req.get('title') else ""}\n"
                            )
                    print("\t" + self.format_req(req, domain_triggered))
                for req in normal_reqs:
                    if self.OUTPUT:
                        async with aiofiles.open(self.OUTPUT_ANALYZE, "a") as f:
                            await f.write(
                                f"\t[{req['time']}] [{req['request_id']}] [{req['method']}] {req['domain']} [{req['status']}]{f" ({req['content']}b)" if req.get("content") is not None else ""}{f" [{req['payload_size']}]" if req.get("payload_size") is not None else ""}{f" ({req['req_hdrs']})" if req.get("req_hdrs") is not None else ""}{f" {{{req['req_hdrs_size']}b}}" if req.get("req_hdrs_size") is not None else ""}{f" ({req['res_hdrs']})" if req.get("res_hdrs") is not None else ""}{f" {{{req['res_hdrs_size']}b}}" if req.get("res_hdrs_size") is not None else ""}{f" [{req['duration']}s]" if req.get('duration') is not None else ""}{f" \"{req['title']}\"" if req.get('title') else ""}\n"
                            )
                    print("\t" + self.format_req(req, domain_triggered))
                print()


    async def main(self) -> None:

        if self.MODE not in ["subs-xplore", "response-xplore"]:
            print(f"[-] Error, there's no MODE called '{self.MODE}'")
            exit(0)

        self.START_TIME = datetime.datetime.now()
        print(f"{self.colors['url']}[*] Starting: {self.START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")

        resolver = self.about_resolver()
        
        print(f"[+] MODE -> {'Subs-Xplore' if self.CONCURRENT_QUERIES else 'Response-Xplore'}")
        print(f"[+] WORDLIST -> {self.SUBDOMAINS_FILE}")
        print(f"[+] TARGET_DOMAIN -> {self.TARGET_DOMAIN}") if self.CONCURRENT_QUERIES and not self.DOMAINS else None
        print(f"[+] TARGET_DOMAINS_FILE -> {self.TARGET_DOMAINS_FILE}") if self.CONCURRENT_QUERIES and self.DOMAINS else None
        print(f"[+] TIMEOUT -> {self.TIMEOUT}s") if self.TIMEOUT is not None else None
        print(f"[+] DNS_TIMEOUT -> {self.DNS_TIMEOUT}s") if self.DNS_TIMEOUT is not None else None
        print(f"[+] REQ_TIMEOUT -> {self.REQ_TIMEOUT}s") if self.CONCURRENT_REQUESTS and self.REQ_TIMEOUT is not None else None
        print(f"[+] CONNECT_TIMEOUT -> {self.CONNECT_TIMEOUT}s") if self.CONCURRENT_REQUESTS and self.CONNECT_TIMEOUT is not None else None
        print(f"[+] SOCK_CONNECT_TIMEOUT -> {self.SOCK_CONNECT_TIMEOUT}s") if self.CONCURRENT_REQUESTS and self.SOCK_CONNECT_TIMEOUT is not None else None
        print(f"[+] SOCK_READ_TIMEOUT -> {self.SOCK_READ_TIMEOUT}s") if self.CONCURRENT_REQUESTS and self.SOCK_READ_TIMEOUT is not None else None
        print(f"[+] KEEPALIVE_TIMEOUT -> {self.KEEPALIVE_TIMEOUT}s") if self.CONCURRENT_REQUESTS and self.KEEPALIVE_TIMEOUT is not None else None
        print(f"[+] CONCURRENT_QUERIES -> {self.CONCURRENT_QUERIES}" if self.CONCURRENT_QUERIES else f"[+] CONCURRENT_REQUESTS -> {self.CONCURRENT_REQUESTS}")
        print(f"[+] MAX_CONNECTIONS -> {'unlimited' if self.LIMIT is None else self.LIMIT}") if self.CONCURRENT_REQUESTS and self.args.max_connections is not None else None
        print(f"[+] PER_HOST_CONNECTIONS -> {self.LIMIT_PER_HOST}") if self.CONCURRENT_REQUESTS and self.LIMIT_PER_HOST is not None else None
        print(f"[+] RETRIES -> {self.RETRIES}") if self.RETRIES is not None else None
        print(f"[+] DNS_RETRIES -> {self.DNS_RETRIES}") if self.DNS_RETRIES is not None else None
        print(f"[+] REQ_RETRIES -> {self.REQ_RETRIES}") if self.CONCURRENT_REQUESTS and self.REQ_RETRIES is not None else None
        print(f"[+] NO_DNS_CACHE -> {self.NO_DNS_CACHE}") if self.CONCURRENT_REQUESTS and self.NO_DNS_CACHE else None
        print(f"[+] TTL_DNS_CACHE -> {self.TTL_DNS_CACHE}") if self.CONCURRENT_REQUESTS and self.TTL_DNS_CACHE is not None else None
        print(f"[+] RETRIES_DELAY -> {self.RETRIES_DELAY}s") if self.CONCURRENT_REQUESTS and self.RETRIES_DELAY is not None and self.RETRIES_DELAY >= 0 and self.RETRIES > 0 else None
        print(f"[+] EXP_BACKOFF -> {self.EXP_BACKOFF}") if self.CONCURRENT_REQUESTS and self.RETRIES_DELAY and self.RETRIES_DELAY >= 2 and self.RETRIES > 0 and self.EXP_BACKOFF else None
        if self.CONCURRENT_QUERIES and self.SHOW_RECORDS or self.CONCURRENT_QUERIES and self.SHOW_ONLY_A or self.CONCURRENT_QUERIES and self.SHOW_ONLY_CNAME:
            if self.SHOW_RECORDS and not self.SHOW_ONLY_A and not self.SHOW_ONLY_CNAME:
                print("[+] SHOW_RECORDS -> A,CNAME")
            elif self.SHOW_ONLY_A and not self.SHOW_RECORDS and not self.SHOW_ONLY_CNAME:
                print("[+] SHOW_RECORDS -> A")
            elif self.SHOW_ONLY_CNAME and not self.SHOW_RECORDS and not self.SHOW_ONLY_A:
                print("[+] SHOW_RECORDS -> CNAME")
            else:
                print("\n[-] Error, u can only use ONE option from these: [--show-records, --show-only-a, --show-only-cname]")
                exit(0)
        print(f"[+] DNS_SERVERS -> {self.resolvers_list}") if self.CUSTOM_RESOLVERS else None
        print(f"[+] DNS_SERVERS_FILE -> {self.CUSTOM_RESOLVERS_FILE}") if self.CUSTOM_RESOLVERS_FILE else None
        print(f"[+] UDP_PORT -> {self.UDP_PORT}") if self.UDP_PORT is not None else None
        print(f"[+] TCP_PORT -> {self.TCP_PORT}") if self.TCP_PORT is not None else None
        print(f"[+] FLAGS -> {self.FLAGS}") if self.FLAGS is not None else None
        print(f"[+] SOCKET_SBS -> {self.SOCKET_SBS}b") if self.SOCKET_SBS is not None else None
        print(f"[+] SOCKET_RBS -> {self.SOCKET_RBS}b") if self.SOCKET_RBS is not None else None
        print(f"[+] ENABLE_ROTATE -> {self.ENABLE_ROTATE}") if self.ENABLE_ROTATE else None
        print(f"[+] BIND_IP_DNS -> {self.BIND_IP_DNS}") if self.BIND_IP_DNS else None
        print(f"[+] NET_DEV -> {self.NET_DEV}") if self.NET_DEV else None
        print(f"[+] RESOLVCONF -> {self.RESOLVCONF_PATH}") if self.RESOLVCONF_PATH else None
        print(f"[+] RANDOM_USER_AGENTS -> {self.USE_RANDOM_AGENTS}") if self.CONCURRENT_REQUESTS and self.USE_RANDOM_AGENTS is not None else None
        print(f"[+] RANDOM_HEADERS -> {self.USE_RANDOM_HEADERS}") if self.CONCURRENT_REQUESTS and self.USE_RANDOM_HEADERS is not None else None
        print(f"[+] HEADERS_RULES_FILE -> {self.HEADERS_RULES_FILE}") if self.CONCURRENT_REQUESTS and self.HEADERS_RULES_FILE else None
        print(f"[+] CUSTOM_HEADERS -> {self.CUSTOM_HEADERS}") if self.CONCURRENT_REQUESTS and self.CUSTOM_HEADERS else None
        print(f"[+] FILE_CUSTOM_HEADERS -> {self.FILE_CUSTOM_HEADERS}") if self.CONCURRENT_REQUESTS and self.FILE_CUSTOM_HEADERS else None
        print(f"[+] NO_403HEADERS -> {self.NO_403}") if self.CONCURRENT_REQUESTS and self.NO_403 else None
        print(f"[+] REQUEST_METHOD -> {self.METHODS}") if self.CONCURRENT_REQUESTS else None
        print(f"[+] ADD_HTTP -> {self.ADD_HTTP}") if self.CONCURRENT_REQUESTS and self.ADD_HTTP else None
        print(f"[+] ADD_HTTPS -> {self.ADD_HTTPS}") if self.CONCURRENT_REQUESTS and self.ADD_HTTPS else None
        print(f"[+] PORTS -> {",".join(str(p) for p in self.PORTS)}") if self.CONCURRENT_REQUESTS and self.PORTS is not None else None
        print(f"[+] PORTS_HTTP -> {",".join(str(p) for p in self.PORTS_HTTP)}") if self.CONCURRENT_REQUESTS and self.PORTS_HTTP is not None else None
        print(f"[+] PORTS_HTTPS -> {",".join(str(p) for p in self.PORTS_HTTPS)}") if self.CONCURRENT_REQUESTS and self.PORTS_HTTPS is not None else None
        print(f"[+] NO_RESPONSE_HEADERS_SAVING -> {True if not self.NO_RESPONSE_HEADERS_SAVING else False}") if self.CONCURRENT_REQUESTS and not self.NO_RESPONSE_HEADERS_SAVING and self.OUTPUT else None
        print(f"[+] PROXY -> {self.PROXY}") if self.CONCURRENT_REQUESTS and self.PROXY else None
        print(f"[+] SOCKS_PROXY -> {self.SOCKS_PROXY}") if self.CONCURRENT_REQUESTS and self.SOCKS_PROXY else None
        print(f"[+] ROUTE_SOCKS_FIRST -> {self.ROUTE_SOCKS_FIRST}") if self.CONCURRENT_REQUESTS and self.ROUTE_SOCKS_FIRST and self.PROXY and self.SOCKS_PROXY else None
        print(f"[+] NO_RDNS -> {self.NO_RDNS}") if self.CONCURRENT_REQUESTS and self.NO_RDNS and self.SOCKS_PROXY else None
        print(f"[+] BIND -> {self.BIND}") if self.CONCURRENT_REQUESTS and self.BIND else None
        print(f"[+] PARAMS -> {self.PARAMS}") if self.CONCURRENT_REQUESTS and self.PARAMS else None
        print(f"[+] RANDOM_PAYLOAD -> {self.RANDOM_DATA}") if self.CONCURRENT_REQUESTS and self.RANDOM_DATA else None
        print(f"[+] PAYLOADS_FILE -> {self.PAYLOADS_FILE}") if self.CONCURRENT_REQUESTS and self.PAYLOADS_FILE else None
        print(f"[+] DATA -> {self.DATA_PAYLOAD}") if self.CONCURRENT_REQUESTS and self.DATA else None
        print(f"[+] FILE_DATA -> {self.FILE_DATA}") if self.CONCURRENT_REQUESTS and self.FILE_DATA else None
        print(f"[+] JSON_DATA -> {self.DATA_PAYLOAD}") if self.CONCURRENT_REQUESTS and self.JSON_DATA else None
        print(f"[+] FILE_JSON_DATA -> {self.FILE_JSON_DATA}") if self.CONCURRENT_REQUESTS and self.FILE_JSON_DATA else None
        print(f"[+] DATA_ENCODE_TYPE -> {self.DATA_ENCODE_TYPE}") if self.CONCURRENT_REQUESTS and self.DATA_ENCODE_TYPE else None
        print(f"[+] DATA_METHODS -> {self.DATA_METHODS}") if self.CONCURRENT_REQUESTS and self.DATA_METHODS else None
        print(f"[+] NO_DATA_SAVING -> {self.NO_DATA_SAVING}") if self.CONCURRENT_REQUESTS and self.NO_DATA_SAVING else None
        print(f"[+] USE_UJSON -> {self.USE_UJSON}") if self.CONCURRENT_REQUESTS else None
        print(f"[+] BUFFER_SIZE -> {self.BUFFER_SIZE}b") if self.CONCURRENT_REQUESTS and self.BUFFER_SIZE is not None else None
        print(f"[+] DISABLE_REDIRECT -> {self.DISABLE_REDIRECT}") if self.CONCURRENT_REQUESTS and self.DISABLE_REDIRECT else None
        print(f"[+] DISABLE_REDIRECT_HTTP -> {self.DISABLE_REDIRECT_HTTP}") if self.CONCURRENT_REQUESTS and not self.DISABLE_REDIRECT and self.DISABLE_REDIRECT_HTTP else None
        print(f"[+] DISABLE_REDIRECT_HTTPS -> {self.DISABLE_REDIRECT_HTTPS}") if self.CONCURRENT_REQUESTS and not self.DISABLE_REDIRECT and self.DISABLE_REDIRECT_HTTPS else None
        print(f"[+] MAX_REDIRECTS -> {self.MAX_REDIRECTS}") if self.CONCURRENT_REQUESTS and not self.DISABLE_REDIRECT and self.MAX_REDIRECTS is not None else None
        print(f"[+] MAX_REDIRECTS_HTTP -> {self.MAX_REDIRECTS_HTTP}") if self.CONCURRENT_REQUESTS and not self.DISABLE_REDIRECT and not self.DISABLE_REDIRECT_HTTP and self.MAX_REDIRECTS is None and self.MAX_REDIRECTS_HTTP is not None else None
        print(f"[+] MAX_REDIRECTS_HTTPS -> {self.MAX_REDIRECTS_HTTPS}") if self.CONCURRENT_REQUESTS and not self.DISABLE_REDIRECT and not self.DISABLE_REDIRECT_HTTPS and self.MAX_REDIRECTS is None and self.MAX_REDIRECTS_HTTPS is not None else None
        print(f"[+] NO_CONTENT_SIZE -> {self.NO_CONTENT_SIZE}") if self.CONCURRENT_REQUESTS and self.NO_CONTENT_SIZE else None
        print(f"[+] NO_PAYLOAD_SIZE -> {self.NO_PAYLOAD_SIZE}") if self.CONCURRENT_REQUESTS and self.NO_PAYLOAD_SIZE else None
        print(f"[+] NO_REQUEST_HEADERS -> {self.NO_REQUEST_HEADERS}") if self.CONCURRENT_REQUESTS and self.NO_REQUEST_HEADERS else None
        print(f"[+] NO_REQUEST_HEADERS_SIZE -> {self.NO_REQUEST_HEADERS_SIZE}") if self.CONCURRENT_REQUESTS and self.NO_REQUEST_HEADERS_SIZE else None
        print(f"[+] NO_RESPONSE_HEADERS -> {self.NO_RESPONSE_HEADERS}") if self.CONCURRENT_REQUESTS and self.NO_RESPONSE_HEADERS else None
        print(f"[+] NO_RESPONSE_HEADERS_SIZE -> {self.NO_RESPONSE_HEADERS_SIZE}") if self.CONCURRENT_REQUESTS and self.NO_RESPONSE_HEADERS_SIZE else None
        print(f"[+] NO_TIME -> {self.NO_TIME}") if self.CONCURRENT_REQUESTS and self.NO_TIME else None
        print(f"[+] NO_TITLES -> {self.NO_TITLES}") if self.CONCURRENT_REQUESTS and self.NO_TITLES else None
        print(f"[+] NO_SSL -> {self.NO_SSL}") if self.CONCURRENT_REQUESTS and self.NO_SSL else None
        if self.CONCURRENT_REQUESTS and self.SSL_CERT and self.SSL_KEY and not self.NO_SSL and not self.FINGERPRINT and not self.FINGERPRINT_FILE:
            print(f"[+] SSL_CERT -> {self.SSL_CERT}")
            print(f"[+] SSL_KEY -> {self.SSL_KEY}")
        print(f"[+] CA_CERT -> {self.CA_CERT}") if self.CONCURRENT_REQUESTS and self.CA_CERT and not self.NO_SSL and not self.FINGERPRINT and not self.FINGERPRINT_FILE else None
        print(f"[+] FINGERPRINT -> {self.FINGERPRINT}") if self.CONCURRENT_REQUESTS and self.FINGERPRINT and not self.NO_SSL else None
        print(f"[+] FINGERPRINT_FILE -> {self.FINGERPRINT_FILE}") if self.CONCURRENT_REQUESTS and self.FINGERPRINT_FILE and not self.NO_SSL else None
        print(f"[+] COOKIES -> {self.COOKIES}") if self.CONCURRENT_REQUESTS and self.COOKIES and not self.COOKIES_FILE else None
        print(f"[+] COOKIES_FILE -> {self.COOKIES_FILE}") if self.CONCURRENT_REQUESTS and self.COOKIES_FILE else None
        print(f"[+] SPECIFIC_COOKIES -> {self.SPECIFIC_COOKIES}") if self.CONCURRENT_REQUESTS and self.SPECIFIC_COOKIES and not self.IGNORE_COOKIES and not self.SPECIFIC_COOKIES_FILE else None
        print(f"[+] SPECIFIC_COOKIES_FILE -> {self.SPECIFIC_COOKIES_FILE}") if self.CONCURRENT_REQUESTS and self.SPECIFIC_COOKIES_FILE and not self.IGNORE_COOKIES else None
        print(f"[+] ALLOW_UNSAFE_COOKIES -> {self.ALLOW_UNSAFE_COOKIES}") if self.CONCURRENT_REQUESTS and self.ALLOW_UNSAFE_COOKIES and not self.IGNORE_COOKIES else None
        print(f"[+] IGNORE_COOKIES -> {self.IGNORE_COOKIES}") if self.CONCURRENT_REQUESTS and self.IGNORE_COOKIES else None
        print(f"[+] AUTH -> {self.args.auth}") if self.CONCURRENT_REQUESTS and self.HTTP_AUTH and self.args.auth else None
        print(f"[+] AUTH_FILE -> {self.args.auth_file.strip()}") if self.CONCURRENT_REQUESTS and self.HTTP_AUTH and self.args.auth_file is not None and self.args.auth_file.strip() else None
        print(f"[+] REAL_URL -> {self.REAL_URL}") if self.CONCURRENT_REQUESTS and self.REAL_URL else None
        print(f"[+] FINAL_URL -> {self.FINAL_URL}") if self.CONCURRENT_REQUESTS and self.FINAL_URL else None
        print(f"[+] ONLY_RESPONSES -> {",".join(str(s) for s in self.ONLY_RESPONSES)}") if self.CONCURRENT_REQUESTS and self.ONLY_RESPONSES else None
        print(f"[+] SKIP_RESPONSES -> {",".join(str(s) for s in self.SKIP_RESPONSES)}") if self.CONCURRENT_REQUESTS and self.SKIP_RESPONSES else None
        print(f"[+] ONLY_2XX -> {self.ONLY_2XX}") if self.ONLY_2XX and self.CONCURRENT_REQUESTS else None
        print(f"[+] ONLY_3XX -> {self.ONLY_3XX}") if self.ONLY_3XX and self.CONCURRENT_REQUESTS else None
        print(f"[+] ONLY_4XX -> {self.ONLY_4XX}") if self.ONLY_4XX and self.CONCURRENT_REQUESTS else None
        print(f"[+] ONLY_5XX -> {self.ONLY_5XX}") if self.ONLY_5XX and self.CONCURRENT_REQUESTS else None
        print(f"[+] LESS_400_RESP -> {self.LESS_400_RESP}") if self.CONCURRENT_REQUESTS and self.LESS_400_RESP else None
        print(f"[+] NO_EMPTY_CONTENT -> {self.NO_EMPTY_CONTENT}") if self.CONCURRENT_REQUESTS and self.NO_EMPTY_CONTENT else None
        print(f"[+] MAX_CONTENT -> {self.MAX_CONTENT}b") if self.CONCURRENT_REQUESTS and self.MAX_CONTENT is not None else None
        print(f"[+] MIN_CONTENT -> {self.MIN_CONTENT}b") if self.CONCURRENT_REQUESTS and self.MIN_CONTENT is not None else None
        print(f"[+] ANALYZE_BY -> {self.analyse_by if self.args.analyze_by else 'read \"uquix/docs/analysis_guide.md\"'}") if self.CONCURRENT_REQUESTS and not self.NO_ANALYZE else None
        print(f"[+] NO_ANALYZE -> {self.NO_ANALYZE}") if self.CONCURRENT_REQUESTS and self.NO_ANALYZE else None
        print(f"[+] DISABLE_DETAILED_PROGRESS -> {True if not self.DETAILED_PROGRESS else False}") if self.CONCURRENT_REQUESTS and not self.DETAILED_PROGRESS and not self.DISABLE_PROGRESS else None
        print(f"[+] DISABLE_PROGRESS -> {self.DISABLE_PROGRESS}") if self.DISABLE_PROGRESS else None
        print(f"[+] SHOW_ERRS -> {self.SHOW_ERRORS}") if self.SHOW_ERRORS else None
        print(f"[+] NO_COLORS -> {self.NO_COLORS}") if self.NO_COLORS else None
        print(f"[+] SILENCE -> {self.SILENCE}") if self.SILENCE else None
        print(f"[+] OUTPUT_FILE -> {self.OUTPUT}") if self.OUTPUT else None
        print(f"[+] OUTPUT_SORTED -> {self.OUTPUT_SORTED}") if self.OUTPUT and self.CONCURRENT_REQUESTS else None
        print(f"[+] OUTPUT_ANALYZE -> {self.OUTPUT_ANALYZE}") if self.OUTPUT and self.CONCURRENT_REQUESTS and not self.NO_ANALYZE else None
        print(f"[+] OUTPUT_DETAILED_SORTED -> {self.OUTPUT_DETAILED_SORTED}") if self.OUTPUT and self.CONCURRENT_REQUESTS else None
        print(f"[+] HTML_DIR -> {self.OUTPUT_DIR}") if self.CONCURRENT_REQUESTS and self.OUTPUT_DIR else None
        print(f"[+] NO_HISTORY -> {self.args.no_history}") if self.args.no_history else None
        print(f"[+] NO_MAX_SPEED -> {self.NOT_FASTER}") if self.CONCURRENT_REQUESTS and self.NOT_FASTER else None
        print(f"{"="*100}{self.colors['reset']}")
        if self.CONCURRENT_REQUESTS and not self.SILENCE:
            print(f"\n{self.colors['cols']}[Timestamp] [ID] [Method] [URL] [Status_Code]{' [Content_Size]' if not self.NO_CONTENT_SIZE else ''}{' [Payload_Size]' if not self.NO_PAYLOAD_SIZE else ''}{' [Req_Hdrs]' if not self.NO_REQUEST_HEADERS else ''}{' [Req_Hdrs_Size]' if not self.NO_REQUEST_HEADERS_SIZE else ''}{' [Res_Hdrs]' if not self.NO_RESPONSE_HEADERS else ''}{' [Res_Hdrs_Size]' if not self.NO_RESPONSE_HEADERS_SIZE else ''}{' [Duration]' if not self.NO_TIME else ''}{' [Title]' if not self.NO_TITLES else ''}{self.colors['reset']}")
            print()

        if not self.args.no_history:
            his = pathlib.Path(__file__).parent.parent.parent / "history.log"
            if not his.exists():
                async with aiofiles.open(his, "w") as phg:
                    pass

            async with aiofiles.open(his, "r+") as hg:
                try:
                    hl = await hg.readlines()
                    await hg.seek(0, 2)
                    await hg.write(f"[{len(hl)+1}] {self.START_TIME.strftime('[%Y-%m-%d] [%H:%M:%S]')} -> {" ".join([r for r in sys.argv[1:]])}\n")
                except Exception as e:
                    print(f"[-] Error while writing into '{his}' file: {e}")

        if self.CONCURRENT_QUERIES:
            if self.DOMAINS:
                tasks = list()
                for domain in self.DOMAINS:
                    tasks.append(asyncio.create_task(self.detect_wildcard(domain, resolver)))
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                await self.detect_wildcard(self.TARGET_DOMAIN, resolver)

        wordlist_lines = 0
        subdomains = list()
        async with aiofiles.open(self.SUBDOMAINS_FILE, "r") as f:
            async for line in f:
                if line.strip():
                    wordlist_lines+=1
                    subdomain = line.strip()
                    if self.CONCURRENT_REQUESTS:
                        if self.ADD_HTTP or self.ADD_HTTPS:
                            if self.ADD_HTTP and "://" not in subdomain:
                                subdomains.append("http://"+subdomain)
                            elif self.ADD_HTTP and "://" in subdomain:
                                subdomains.append(subdomain)
                            if self.ADD_HTTPS and "://" not in subdomain:
                                subdomains.append("https://"+subdomain)
                            elif self.ADD_HTTPS and "://" in subdomain:
                                subdomains.append(subdomain)
                        else:
                            subdomains.append(subdomain)
                    else:
                        if "://" in subdomain:
                            subdomain = subdomain.replace("http://","").replace("https://","")
                        subdomains.append(subdomain)

        if subdomains and self.CONCURRENT_REQUESTS and (self.PORTS or self.PORTS_HTTP or self.PORTS_HTTPS):
            subdomains_with_ports = list()
            if self.PORTS:
                for su in subdomains:
                    for pu in self.PORTS:
                        subdomains_with_ports.append(f"{su}:{pu}")
            elif self.PORTS_HTTP or self.PORTS_HTTPS:
                for su in subdomains:
                    if self.PORTS_HTTP:
                        if su.startswith("http://"):
                            for pu in self.PORTS_HTTP:
                                subdomains_with_ports.append(f"{su}:{pu}")
                    if self.PORTS_HTTPS:
                        if su.startswith("https://"):
                            for pu in self.PORTS_HTTPS:
                                subdomains_with_ports.append(f"{su}:{pu}")
            if subdomains_with_ports:
                subdomains = subdomains_with_ports

        unique_http = set()
        unique_https = set()

        try:
            if self.DETAILED_PROGRESS and self.CONCURRENT_REQUESTS:
                for subdomain in subdomains:
                    assert "://" in subdomain, f"[-] Error, No Protocol Type, use '--add-http' and/or '--add-https'"
                    if subdomain.startswith("http://"):
                        self.ALL_HTTP_REQUESTS+=1
                        unique_http.add(subdomain)
                    elif subdomain.startswith("https://"):
                        self.ALL_HTTPS_REQUESTS+=1
                        unique_https.add(subdomain)
            else:
                if self.CONCURRENT_REQUESTS:
                    for subdomain in subdomains:
                        assert "://" in subdomain, f"[-] Error, No Protocol Type, use '--add-http' and/or '--add-https'"
        except AssertionError as e:
            print(e)
        
        total = len(subdomains)
    
        semaphore = asyncio.Semaphore(self.CONCURRENT_REQUESTS or self.CONCURRENT_QUERIES)

        try:
            await self.worker(semaphore, subdomains, resolver, total)
        finally:
            if self.CONCURRENT_REQUESTS:
                self.ALL_SORTED_RESULTS.sort(key=lambda x: (x.split()[3].split("://")[1].split("/")[0], x.split()[2]))
                if self.OUTPUT and os.path.exists(self.OUTPUT):
                    async with aiofiles.open(self.OUTPUT_SORTED, "a") as fs:
                        for r in self.ALL_SORTED_RESULTS:
                            await fs.write(r+"\n")
                    async with aiofiles.open(self.OUTPUT, "r") as ro:
                        async for row in ro:
                            self.DETAILED_ALL_SORTED_RESULTS.append(row.strip())
                    try:
                        self.DETAILED_ALL_SORTED_RESULTS.sort(key=lambda x: (x.split()[3].split("://")[1].split("/")[0], x.split()[2]))
                    except IndexError:
                        pass
                    async with aiofiles.open(self.OUTPUT_DETAILED_SORTED, "a") as rsf:
                        for sr in self.DETAILED_ALL_SORTED_RESULTS:
                            await rsf.write(sr+"\n")
                if not self.NO_ANALYZE:
                    print("\n"+" "*30+self.colors['url']+"-"*30+">"+" ANALYZING-RESPONSES "+"<"+"-"*30+f"{self.colors['reset']}\n")
                    await self.analyze_reqs(self.ALL_SORTED_RESULTS, self.analyse_by.replace("(", "").replace(")", ""))
            print(f"{self.colors['url']}{"-"*100}{self.colors['reset']}")
            runtime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - self.START_TIME).total_seconds())))
            print(f"{self.colors['url']}[*] Started: {self.START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[*] Finished: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[*] Runtime: {runtime}")
            print(f"[+] Wordlist Lines: {wordlist_lines}{self.colors['reset']}")
            if self.CONCURRENT_QUERIES:
                print(f"[+] Total Found Subs: {self.colors['status_2xx']}{len(self.ALL_SUBDOMAINS)}{self.colors['reset']}")
                print(f"[+] Total Found Unique Subs: {self.colors['status_2xx']}{len(set(self.ALL_SUBDOMAINS))}{self.colors['reset']}")
                print(f"[+] Discovered Subs are Saved to {self.colors['status_2xx']}'{self.OUTPUT}'{self.colors['reset']}") if self.OUTPUT and os.path.exists(self.OUTPUT) else None
            else:
                print(f" {self.colors['size']}[ALL URLs]:{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[*] Total URLs:{self.colors['reset']} {self.colors['url']}{total}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[*] Total Unique URLs:{self.colors['reset']} {self.colors['url']}{len(set(subdomains))}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[+] Total Processed Unique URLs:{self.colors['reset']} {self.colors['status_2xx']}{len(self.ALL_SUBDOMAINS)}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[-] Total Failed Unique URLs:{self.colors['reset']} {self.colors['status_403']}{len(set(subdomains))-len(self.ALL_SUBDOMAINS)}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[*] Total Requests:{self.colors['reset']} {self.colors['url']}{total*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[+] Total Processed Requests:{self.colors['reset']} {self.colors['status_2xx']}{self.ALL_REQUESTS}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[-] Total Failed Requests:{self.colors['reset']} {self.colors['status_403']}{(total*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS)-self.ALL_REQUESTS}{self.colors['reset']}")
                print(f"\t{self.colors['status_3xx']}[-] Total Actual Failed Requests (including retries):{self.colors['reset']} {self.colors['status_403']}{self.TOTAL_FAILED_REQS}{self.colors['reset']}")
                if self.DETAILED_PROGRESS:
                    print(f" {self.colors['size']}[HTTP URLs]:{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total HTTP URLs:{self.colors['reset']} {self.colors['url']}{self.ALL_HTTP_REQUESTS}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total Unique HTTP URLs:{self.colors['reset']} {self.colors['url']}{len(unique_http)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[+] Total Processed Unique HTTP URLs:{self.colors['reset']} {self.colors['status_2xx']}{len(self.UNIQUE_HTTP)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Failed Unique HTTP URLs:{self.colors['reset']} {self.colors['status_403']}{len(unique_http)-len(self.UNIQUE_HTTP)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total HTTP Requests:{self.colors['reset']} {self.colors['url']}{self.ALL_HTTP_REQUESTS*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[+] Total Processed HTTP Requests:{self.colors['reset']} {self.colors['status_2xx']}{len(self.ALL_HTTP_SUBDOMAINS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Failed HTTP Requests:{self.colors['reset']} {self.colors['status_403']}{(self.ALL_HTTP_REQUESTS*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS)-len(self.ALL_HTTP_SUBDOMAINS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Actual Failed HTTP Requests (including retries):{self.colors['reset']} {self.colors['status_403']}{self.HTTP_FAILED_REQS}{self.colors['reset']}")
                    print(f" {self.colors['size']}[HTTPS URLs]:{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total HTTPS URLs:{self.colors['reset']} {self.colors['url']}{self.ALL_HTTPS_REQUESTS}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total Unique HTTPS URLs:{self.colors['reset']} {self.colors['url']}{len(unique_https)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[+] Total Processed Unique HTTPS URLs:{self.colors['reset']} {self.colors['status_2xx']}{len(self.UNIQUE_HTTPS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Failed Unique HTTPS URLs:{self.colors['reset']} {self.colors['status_403']}{len(unique_https)-len(self.UNIQUE_HTTPS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[*] Total HTTPS Requests:{self.colors['reset']} {self.colors['url']}{self.ALL_HTTPS_REQUESTS*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[+] Total Processed HTTPS Requests:{self.colors['reset']} {self.colors['status_2xx']}{len(self.ALL_HTTPS_SUBDOMAINS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Failed HTTPS Requests:{self.colors['reset']} {self.colors['status_403']}{(self.ALL_HTTPS_REQUESTS*len(self.METHODS.split(','))*self.NUMS_OF_RANDOM_HEADERS)-len(self.ALL_HTTPS_SUBDOMAINS)}{self.colors['reset']}")
                    print(f"\t{self.colors['status_3xx']}[-] Total Actual Failed HTTPS Requests (including retries):{self.colors['reset']} {self.colors['status_403']}{self.HTTPS_FAILED_REQS}{self.colors['reset']}")
                print(f" {self.colors['out']}[OUTPUT]:{self.colors['reset']}") if self.OUTPUT and os.path.exists(self.OUTPUT) or self.OUTPUT_DIR else None
                if self.OUTPUT and os.path.exists(self.OUTPUT):
                    print(f"\t{self.colors['cols']}[+] All requests with its BASIC INFO are SORTLY saved in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT_SORTED}'{self.colors['reset']}")
                    print(f"\t{self.colors['cols']}[+] All requests with its ALL INFO are SORTLY saved in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT_DETAILED_SORTED}'{self.colors['reset']}")
                    print(f"\t{self.colors['cols']}[+] All requests with its ALL INFO are UNSORTLY saved in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT}'{self.colors['reset']}")
                    print(f"\t{self.colors['cols']}[+] Analyzing results are saved in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT_ANALYZE}'{self.colors['reset']}") if not self.NO_ANALYZE else None
                print(f"\t{self.colors['cols']}[+] Every response is saved as '.html' file in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT_DIR}'{self.colors['reset']} {self.colors['cols']}directory{self.colors['reset']}" if not self.IS_EXIST_DIR else f"\t{self.colors['cols']}[+] Every response is saved as '.html' in{self.colors['reset']} {self.colors['status_2xx']}'{self.OUTPUT_DIR}'{self.colors['reset']} {self.colors['cols']}already exist directory{self.colors['reset']}") if self.OUTPUT_DIR else None


################################################################
# Coded By: 0.1Arafa                                           #
# Age: 18                                                      #
# 2025                                                         #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################
