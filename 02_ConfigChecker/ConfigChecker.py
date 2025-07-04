import base64
import re
import socket
import ssl
from urllib.parse import urlparse, parse_qs

def parse_config(config):
    """
    Parse V2Ray/VLESS/VMess config links.
    Returns protocol and parsed data (dict or ParseResult).
    """
    if config.startswith("vmess://"):
        try:
            json_part = base64.b64decode(config[8:] + "==").decode("utf-8")
            # safer to use json.loads but eval for backward compatibility here
            return "vmess", eval(json_part)
        except Exception as e:
            return "vmess", {"error": f"Base64 decode failed: {e}"}
    elif config.startswith(("vless://", "trojan://")):
        parsed = urlparse(config)
        return parsed.scheme, parsed
    else:
        return "unknown", config

def domain_resolves(hostname):
    """
    Check if hostname resolves to a valid IP.
    Returns True if resolves, False otherwise.
    """
    try:
        ip = socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

def test_tls(domain, port):
    """
    Test if TLS handshake succeeds with the given domain and port.
    Returns (True, TLS_version) on success, (False, error_msg) on failure.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return True, ssock.version()
    except Exception as e:
        return False, str(e)

def color_percent(score):
    """
    Return colored string based on security score.
    """
    if score <= 30:
        return f"\033[91m{score}% (Low Security)\033[0m"     # Red
    elif score <= 60:
        return f"\033[93m{score}% (Medium-Low)\033[0m"       # Yellow
    elif score <= 85:
        return f"\033[92m{score}% (Good)\033[0m"             # Light Green
    else:
        return f"\033[92;1m{score}% (High Security)\033[0m"  # Bright Green

def evaluate_security(config):
    """
    Evaluate security of V2Ray config.
    Returns (score_percent, list_of_issues)
    """
    score = 0
    max_score = 12  # increased due to extra checks
    issues = []

    proto, parsed = parse_config(config)

    if proto == "unknown":
        return 0, ["Unsupported or unknown config format."]

    hostname = ""
    port = 0

    # --- VMESS ---
    if proto == "vmess":
        if "error" in parsed:
            return 0, [parsed["error"]]

        hostname = parsed.get("add", "")
        port = int(parsed.get("port", 0))

        # TLS check
        if parsed.get("tls") == "tls":
            score += 1
        else:
            issues.append("TLS is not enabled (`tls` should be 'tls').")

        # Port check
        if str(port) in ["443", "8443"]:
            score += 1
        else:
            issues.append("Non-standard port used for TLS (recommended 443 or 8443).")

        # Transport type
        if parsed.get("net") in ["ws", "grpc"]:
            score += 1
        else:
            issues.append(f"Insecure or unknown transport: {parsed.get('net')}")

        # Host / SNI
        if parsed.get("host"):
            score += 1
        else:
            issues.append("Missing host/SNI.")

        # Path
        if parsed.get("path", "") and len(parsed["path"]) > 2:
            score += 1
        else:
            issues.append("WebSocket path is too short or empty.")

        # Encryption (VMess specific)
        if parsed.get("encryption", "").lower() in [
            "auto",
            "aes-128-gcm",
            "chacha20-poly1305",
        ]:
            score += 1
        else:
            issues.append("Weak or missing encryption setting.")

        # AlterId (deprecated feature)
        if parsed.get("aid") == "0":
            score += 1
        else:
            issues.append("AlterId should be 0 (deprecated, better to disable).")

    # --- VLESS or Trojan ---
    elif proto in ["vless", "trojan"]:
        qs = parse_qs(parsed.query)
        hostname = parsed.hostname or ""
        port = parsed.port or 0

        # security param
        if qs.get("security", [""])[0] in ["tls", "reality"]:
            score += 1
        else:
            issues.append("`security` should be 'tls' or 'reality'.")

        # port check
        if port in [443, 8443]:
            score += 1
        else:
            issues.append(f"Insecure port used: {port}")

        # transport type
        if qs.get("type", [""])[0] in ["ws", "grpc"]:
            score += 1
        else:
            issues.append(f"Insecure or unknown transport: {qs.get('type', [''])[0]}")

        # host/SNI
        if qs.get("host", [""])[0]:
            score += 1
        else:
            issues.append("Host/SNI is not set.")

        # path
        if qs.get("path", [""])[0] and len(qs["path"][0]) > 2:
            score += 1
        else:
            issues.append("Path is too short or missing.")

        # encryption (for VLESS should be none)
        if qs.get("encryption", [""])[0] == "none":
            score += 1
        else:
            issues.append("Encryption should be 'none' for VLESS.")

        # validate hostname format
        if hostname and re.match(r"^[\w.-]+\.[a-z]{2,}$", hostname):
            score += 1
        else:
            issues.append("Invalid or missing domain name.")

    # --- DNS resolution check ---
    if hostname:
        if domain_resolves(hostname):
            score += 1
        else:
            issues.append(f"Domain name '{hostname}' does not resolve to an IP.")

    # --- TLS handshake test ---
    if hostname and port:
        tls_ok, tls_result = test_tls(hostname, port)
        if tls_ok:
            score += 1
        else:
            issues.append(f"TLS handshake failed: {tls_result}")

    percent = int((score / max_score) * 100)
    return percent, issues

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 config_check.py '<config-link>'")
        sys.exit(1)

    config_input = sys.argv[1]
    print(f"\nAnalyzing Config:\n{config_input}")
    score, warnings = evaluate_security(config_input)
    print(f"\nSecurity Score: {color_percent(score)}")
    if warnings:
        print("\nIssues found:")
        for w in warnings:
            print(f" - {w}")
    print("\n" + "-" * 60)
