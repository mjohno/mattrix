#!/usr/bin/env bash
# Run the repeatable Stagger Step quality evaluation from the project root.
set -euo pipefail

readonly goal_file="agents/stagger-step/evals/quality_check.md"
readonly change_dir="./tmp/stagger-step-eval"
readonly step_file="${change_dir}/STEP-quality-eval.yaml"

if [[ ! -f "${goal_file}" ]]; then
  printf 'Run this script from the project root.\n' >&2
  exit 1
fi

mkdir -p "${change_dir}"
rm -f "${step_file}"

STEP_FILE="${step_file}" stagger-step --log-level INFO init \
  --change . \
  --session \
  --goal "$(cat "${goal_file}")"
