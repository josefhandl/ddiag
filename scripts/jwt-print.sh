#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <jwt_token>"
  exit 1
fi

header=$(echo "$1" | cut -d '.' -f1)
payload=$(echo "$1" | cut -d '.' -f2)
signature=$(echo "$1" | cut -d '.' -f3)

echo "Header:"
echo "$header" | base64 -d -w0 | jq
echo "Payload:"
echo "$payload" | base64 -d -w0 | jq

exp=$(echo "$payload" | base64 -d -w0 | jq | grep -Po '"exp": \K[^,]*')
iat=$(echo "$payload" | base64 -d -w0 | jq | grep -Po '"iat": \K[^,]*')
echo "Converted EXP: $(date -d @$exp)"
echo "Converted IAT: $(date -d @$iat)"

echo "Signature:"
echo "$signature"
