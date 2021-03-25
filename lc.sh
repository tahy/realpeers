#!/usr/bin/env bash

find . -name '*.py' -type f -print0 | xargs -0 cat | wc -l
