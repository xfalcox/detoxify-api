#!/bin/sh

wrk -t4 -c10 -d30s http://127.0.0.1:8000/api/v1/classify -s post.lua