#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 LAPTOP_IPV4"
  echo "Example: $0 192.168.1.25"
  exit 2
fi

receiver_ip="$1"
rpicam-vid -t 0 -n \
  --width 640 --height 480 --framerate 15 \
  --bitrate 1000000 --inline -o - \
  | ffmpeg -loglevel warning -fflags nobuffer -flags low_delay \
      -f h264 -i pipe:0 -an -c:v copy -flush_packets 1 \
      -f rtp_mpegts "rtp://$receiver_ip:5004?pkt_size=1316"


