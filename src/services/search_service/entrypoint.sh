#!/usr/bin/env bash
# Sync time with NTP to avoid AWS time skew errors
ntpdate -u pool.ntp.org || true
exec uvicorn main:app --host 0.0.0.0 --port 5001