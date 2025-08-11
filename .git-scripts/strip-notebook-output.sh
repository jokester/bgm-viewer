#!/usr/bin/env bash
if ! type jq &>/dev/null; then
  echo 1>&2 'jq not installed. unable to strip outputs from ipynb notebooks'
  exec cat
else
  exec jq --indent 1 \
    '
      (.cells[] | select(has("outputs")) | .outputs) = []
      | (.cells[] | select(has("execution_count")) | .execution_count) = null
      | .metadata = {"language_info": {"name":"python", "pygments_lexer": "ipython3"}}
      | .cells[].metadata = {}
    '
fi
