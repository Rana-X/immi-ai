#!/usr/bin/env bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT 