#!/usr/bin/env bash
cd $(dirname "$0")
set -uex
git config filter.strip-notebook-output.clean .git-scripts/strip-notebook-output.sh
