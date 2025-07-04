# V2Ray Config Security Checker

A Python-based command-line tool to analyze and evaluate the security level of V2Ray/VLESS/VMess/Trojan proxy configuration links. This tool helps you quickly assess the security posture of your proxy configuration URLs by checking their structural validity, encryption settings, TLS implementation, DNS resolution, and actual TLS handshake success.

---

## 🚀 What is this tool?

V2Ray and its protocols (VLESS, VMess, Trojan) are popular proxies widely used for bypassing network restrictions and enhancing online privacy. However, improper or insecure configurations can expose users to security risks such as eavesdropping, man-in-the-middle attacks, or data leaks.

This tool inspects your proxy config URLs and:

* Parses the config link (VMess, VLESS, Trojan)
* Verifies key security parameters such as TLS usage, encryption strength, transport type, and port safety
* Checks if the hostname resolves to a valid IP address (DNS validation)
* Performs a real TLS handshake test to confirm TLS is properly implemented on the server
* Assigns a security score (0–100%) with color-coded terminal output for easy interpretation
* Lists warnings and potential issues to help you improve your config security

---

## ⚙️ How does it work?

1. **Parsing the config:** Extracts parameters from the config URL or base64 encoded JSON for VMess.
2. **Security analysis:** Checks for critical settings like TLS enabled, use of secure ports (443/8443), appropriate transport (ws/grpc), encryption settings, and presence of host/SNI.
3. **DNS resolution:** Validates that the domain name used in the config actually resolves to an IP address.
4. **TLS handshake test:** Attempts a live TLS handshake with the server to verify real TLS support.
5. **Scoring & reporting:** Calculates an overall security score, colorizes it, and outputs detailed warnings for insecure or suspicious parameters.

---

## 🛠️ Installation

1. Make sure you have Python 3 installed.
2. Clone or download this repository.
3. Save the `config_check.py` script to your local machine.

---

## 💻 Usage

Run the script with your V2Ray config link as an argument:

```bash
python3 config_check.py '<your-v2ray-config-link>'
```

Example:

```bash
python3 ConfigChecker.py 'vless://5302d5a2-cba5-4ebe-a9ce-daa768b64ddb@speedtest.net:443?type=ws&security=tls&host=example.com&path=/proxy&encryption=none'
```

The output will show a colored security score and a list of any issues found.

---

## 📊 Sample Output

```
Analyzing Config:
vless://5302d5a2-cba5-4ebe-a9ce-daa768b64ddb@speedtest.net:443?type=ws&security=tls&host=example.com&path=/proxy&encryption=none

Security Score:  83% (Good)

Issues found:
 - Path is too short or missing.
 - Encryption should be 'none' for VLESS.
```

---

## 🚧 Limitations & Future Work

* Currently supports VMess, VLESS, and Trojan protocols.
* TLS handshake test depends on network accessibility to the host.
* Base64 decoding for VMess uses `eval` for legacy reasons; migrating to `json` parsing recommended.
* No GUI or batch file input yet (can be added).
* Does not check actual payload encryption or proxy traffic security.
* Could be extended with:

  * Batch file input and output reports (CSV/JSON)
  * Interactive CLI or GUI interface
  * Integration with public blacklists or threat intelligence for host validation
  * Detailed traffic analysis (if integrated with proxy logs)

---

## 📢 Disclaimer

This tool is intended for educational and auditing purposes only. It does not guarantee complete security but aims to help identify common misconfigurations and risks in V2Ray proxy configs.

---

## 🙋‍♂️ Contributions & Feedback

Feel free to fork, improve, and send pull requests. Issues and feature requests are welcome!

---

## 🧑‍💻 Author

Created by \[Your Name].
Contact: \[[Omidh225@gmail.com](mailto:Omidh225@gmail.com)]

---

If you want, I can help generate the actual `README.md` file or make it in Persian too.
