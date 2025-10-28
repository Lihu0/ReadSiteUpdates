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
    line="${line%%#*}"   # remove inline comments
    line="${line// /}"    # remove spaces

    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^[;\#] ]] && continue

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
    # round to nearest integer
    minutes=$(printf "%.0f" "$minutes")
else
    echo "Invalid interval format: $interval"
    exit 1
fi

# --- Resolve absolute script path ---
script_path=$(readlink -f "$script_to_execute")
script_name=$(basename "$script_path")
# use project root as working directory
project_root=$(dirname "$script_path")/..

# --- Debug output ---
echo "Start Time: $start_time"
echo "Project Root: $project_root"
echo "Script Name: $script_name"
echo "Interval (minutes): $minutes"

# --- Build cron command ---
cron_command="cd '$project_root' && ./$(basename "$script_name") >> '$project_root/cron.log' 2>&1"

# --- Determine cron line ---
if (( minutes >= 1440 )); then
    # validate start_time HH:MM
    if [[ ! "$start_time" =~ ^([01]?[0-9]|2[0-3]):([0-5][0-9])$ ]]; then
        echo "Invalid start_time format (expected HH:MM): $start_time"
        exit 1
    fi
    hour="${start_time%%:*}"
    minute="${start_time##*:}"
    cron_line="$minute $hour * * * $cron_command"
else
    cron_line="*/$minutes * * * * $cron_command"
fi

# --- Add cron job safely ---
(crontab -l 2>/dev/null | grep -v -F "$script_name" || true; echo "$cron_line") | crontab -

echo "Cron job added:"
echo "$cron_line"
