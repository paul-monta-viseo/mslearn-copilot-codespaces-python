#!/bin/bash
# Run the linter and formatter on any Python file that was just written
if [[ "$COPILOT_HOOK_FILE" == *.py ]]; then
  ruff check --fix "$COPILOT_HOOK_FILE"
  ruff format "$COPILOT_HOOK_FILE"
fi