#!/bin/sh

wrk -t4 -c10 -d30s http://localhost/api/v1/classify -s post.lua