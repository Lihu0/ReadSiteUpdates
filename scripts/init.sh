#!/bin/bash
set -e

# --- INI settings ---
iniFile="../settings.ini"
section="[scheduler]"
inSection=false

start_time=""
interval=""
script_to_execute=""

while IFS= read -r line; do
    line="${line// /}"  # remove all spaces

    if [[ "$line" == "$section" ]]; then
        inSection=true
        continue
    elif [[ "$line" =~ ^\[.*\]$ ]]; then
        inSection=false
    fi

    if $inSection && [[ "$line" != "$section" ]]; then
        key="${line%%=*}"
        value="${line#*=}"
        case "$key" in
            start_time) start_time="$value" ;;
            interval) interval="$value" ;;
            script_to_execute) script_to_execute="$value" ;;
        esac
    fi
done < "$iniFile"

# --- Convert interval to minutes ---
if [[ "$interval" =~ ^([0-9]+(\.[0-9]+)?)([hmdHMD])$ ]]; then
    num="${BASH_REMATCH[1]}"
    unit="${BASH_REMATCH[3],,}"  # lowercase
    case "$unit" in
        m) minutes="$num" ;;
        h) minutes=$(echo "$num*60" | bc) ;;
        d) minutes=$(echo "$num*1440" | bc) ;;
    esac
else
    echo "Invalid interval format: $interval"
    exit 1
fi

# --- Resolve absolute script path ---
script_path=$(readlink -f "$script_to_execute")
script_folder=$(dirname "$script_path")
script_name=$(basename "$script_path")

# --- Debug output ---
echo "Start Time: $start_time"
echo "Script Folder: $script_folder"
echo "Script Name: $script_name"
echo "Interval (minutes): $minutes"

# --- Build cron command ---
cron_command="cd '$script_folder' && ./$(basename "$script_name")"

# --- Determine cron line ---
if (( $(echo "$minutes >= 1440" | bc -l) )); then
    hour="${start_time%%:*}"
    minute="${start_time##*:}"
    cron_line="$minute $hour * * * $cron_command"
else
    cron_line="*/$minutes * * * * $cron_command"
fi

# --- Add cron job safely ---
crontab_tmp=$(mktemp)
crontab -l 2>/dev/null | grep -v -F "$script_name" > "$crontab_tmp" || true
echo "$cron_line" >> "$crontab_tmp"
crontab "$crontab_tmp"
rm "$crontab_tmp"

echo "Cron job added:"
echo "$cron_line"
