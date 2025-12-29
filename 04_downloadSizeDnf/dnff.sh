#!/usr/bin/env bash
set -euo pipefail

dnf repoquery --upgrades --qf '%{downloadsize} %{name}\n' |
sort -nr |
numfmt --to=iec |
awk '
BEGIN {
    print "┌────────────┬────────────────────────────────────────────────────┐"
    printf "│ \033[1;44m%-10s\033[0m │ \033[1;44m%-50s\033[0m │\n", "  SIZE", "  PACKAGE NAME"
    print "├────────────┼────────────────────────────────────────────────────┤"
}
{
    if($1 ~ /G/) color="\033[1;31m";
    else if($1 ~ /M/) color="\033[1;33m";
    else color="\033[0;32m";

    printf "│ %s%-10s\033[0m │ %-50s │\n", color, $1, $2
}
END {
    print "└────────────┴────────────────────────────────────────────────────┘"
}'
