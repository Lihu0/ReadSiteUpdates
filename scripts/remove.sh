#!/bin/bash
set -e

# The script name or unique identifier in the cron job
script_name="run_me.sh"

# Check if the cron job exists
if crontab -l 2>/dev/null | grep -q "$script_name"; then
    echo "Cron job for \"$script_name\" exists. Deleting..."
    # Remove the cron job containing the script
    crontab -l 2>/dev/null | grep -v "$script_name" | crontab -
    echo "Cron job deleted."
else
    echo "Cron job for \"$script_name\" does not exist."
fi
