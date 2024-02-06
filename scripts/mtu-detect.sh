#!/bin/bash

# Function to display script usage
usage() {
    echo "Usage: $0 -d <destination_ip> -m <min_size> -M <max_size> -s <step>"
    echo "Options:"
    echo "  -d <destination_ip>   Destination IP address for the ping test."
    echo "  -m <min_size>         Minimum packet size to start testing."
    echo "  -M <max_size>         Maximum packet size to end testing."
    echo "  -s <step>             Step size for increasing packet size during testing."
    exit 1
}

# Parse command line options
while getopts "d:m:M:s:" opt; do
    case $opt in
        d) destination_ip="$OPTARG" ;;
        m) min_size="$OPTARG" ;;
        M) max_size="$OPTARG" ;;
        s) step="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if all required parameters are provided
if [ -z "$destination_ip" ] || [ -z "$min_size" ] || [ -z "$max_size" ] || [ -z "$step" ]; then
    usage
fi

# Check localhost connectivity
echo "Checking localhost connectivity"
ping -c 1 localhost > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Localhost connectivity check successful"
else
    echo "Localhost connectivity check failed. Check your network settings."
    exit 1
fi

# Perform MTU detection
echo "Testing MTU from $min_size to $max_size with step $step"
for ((size = min_size; size <= max_size; size += step)); do
    echo -n "Testing MTU with packet size $size: "
    ping -c 1 -M do -s $size $destination_ip > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Success"
    else
        echo "Failed"
        echo "MTU size is likely $((size - step))"
        exit 0
    fi
done

echo "MTU detection complete. Maximum MTU size is $max_size."

