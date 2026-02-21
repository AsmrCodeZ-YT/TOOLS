#!/usr/bin/env bash

# ============================
#  Modern DNS Inspector v2
# ============================

DOMAIN="${1:-github.com}"
DNS_FILE="${2:-}"
TIMEOUT=3

# ---------- Colors ----------
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"

GREEN="\033[38;5;46m"
RED="\033[38;5;196m"
YELLOW="\033[38;5;226m"
BLUE="\033[38;5;39m"
CYAN="\033[38;5;51m"
GRAY="\033[38;5;245m"
MAGENTA="\033[38;5;213m"

# ---------- Spinner ----------
spin() {
  local pid=$1
  local delay=0.08
  local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
  while ps -p $pid > /dev/null 2>&1; do
    local temp=${spinstr#?}
    printf " ${CYAN}[%c]${RESET} Testing..." "$spinstr"
    spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\r"
  done
  printf "                     \r"
}

# ---------- Dependencies ----------
for cmd in dig curl; do
  command -v $cmd >/dev/null || {
    echo -e "${RED}Missing dependency: $cmd${RESET}"
    exit 1
  }
done

# ---------- Default DNS ----------
DEFAULT_DNS=(
"8.8.8.8|Google"
"8.8.4.4|Google"
"1.1.1.1|Cloudflare"
"9.9.9.9|Quad9"
"208.67.222.222|OpenDNS"
)

# ---------- Load DNS ----------
DNS_LIST=()
if [[ -f "$DNS_FILE" ]]; then
  while IFS='|' read -r ip name; do
    [[ -z "$ip" || "$ip" =~ ^# ]] && continue
    DNS_LIST+=("$ip|${name:-Custom}")
  done < "$DNS_FILE"
else
  DNS_LIST=("${DEFAULT_DNS[@]}")
fi

# ---------- Banner ----------
clear
echo -e "${MAGENTA}${BOLD}"
echo "  ██████╗ ███╗   ██╗███████╗     ██╗███╗   ██╗███████╗"
echo "  ██╔══██╗████╗  ██║██╔════╝     ██║████╗  ██║██╔════╝"
echo "  ██║  ██║██╔██╗ ██║███████╗     ██║██╔██╗ ██║███████╗"
echo "  ██║  ██║██║╚██╗██║╚════██║     ██║██║╚██╗██║╚════██║"
echo "  ██████╔╝██║ ╚████║███████║     ██║██║ ╚████║███████║"
echo -e "${RESET}"
echo -e "${GRAY}  Domain:${RESET} ${CYAN}${BOLD}$DOMAIN${RESET}"
echo -e "${GRAY}  Date  :${RESET} $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ---------- Table Header ----------
printf "${DIM}%-15s %-15s %-6s %-8s %-15s %-8s %-6s\n${RESET}" \
"DNS Name" "DNS IP" "Proto" "Status" "Resolved IP" "Time" "HTTP"
echo -e "${GRAY}────────────────────────────────────────────────────────────────────────────${RESET}"

# ---------- Counters ----------
total=0
success=0
fastest=9999
fastest_dns=""

# ---------- Test Loop ----------
for entry in "${DNS_LIST[@]}"; do
  IFS='|' read -r ip name <<< "$entry"
  ((total++))

  start=$(date +%s%3N)
  (dig @"$ip" "$DOMAIN" +short +time=$TIMEOUT +tries=1 >/tmp/dnsout.$$ 2>/dev/null) &
  spin $!
  wait $! 2>/dev/null
  end=$(date +%s%3N)

  time_ms=$((end-start))
  resolved_ip=$(grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' /tmp/dnsout.$$ | head -n1)

  if [[ -n "$resolved_ip" ]]; then
    status="${GREEN}✔${RESET}"
    ((success++))

    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
      --resolve "${DOMAIN}:80:${resolved_ip}" \
      --connect-timeout 3 "http://${DOMAIN}")

    [[ "$time_ms" -lt "$fastest" ]] && {
      fastest=$time_ms
      fastest_dns="$name ($ip)"
    }
  else
    status="${RED}✖${RESET}"
    http_code="---"
  fi

  # Colorize time
  if [[ "$time_ms" -lt 50 ]]; then
    tcolor=$GREEN
  elif [[ "$time_ms" -lt 200 ]]; then
    tcolor=$YELLOW
  else
    tcolor=$RED
  fi

  printf "%-15s %-15s %-6s %-8b %-15s ${tcolor}%-8sms${RESET} %-6s\n" \
  "$name" "$ip" "UDP" "$status" "${resolved_ip:-—}" "$time_ms" "$http_code"

done

rm -f /tmp/dnsout.$$

# ---------- Summary ----------
echo ""
echo -e "${BLUE}╭──────────────────────── Summary ────────────────────────╮${RESET}"
echo -e "  ${BOLD}Total DNS Tested :${RESET} $total"
echo -e "  ${BOLD}Successful       :${RESET} ${GREEN}$success${RESET}"
echo -e "  ${BOLD}Failed           :${RESET} ${RED}$((total-success))${RESET}"
echo -e "  ${BOLD}Fastest DNS      :${RESET} ${CYAN}$fastest_dns${RESET} (${fastest} ms)"
echo -e "${BLUE}╰──────────────────────────────────────────────────────────╯${RESET}"
echo ""