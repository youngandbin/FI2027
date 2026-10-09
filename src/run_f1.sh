#!/usr/bin/env bash
# F1 go/no-go pilot: US only, one local model, prompt A, N=20, 2024-09..2025-12.
# Usage: src/run_f1.sh <hf_model> <model_tag> [port] [extra vllm args...]
#   src/run_f1.sh openai/gpt-oss-20b gptoss20b 8011
#   src/run_f1.sh google/gemma-3-27b-it gemma3-27b 8011 --max-model-len 4096
# Serves the model on GPU 1 (src/serve.sh), waits until it answers, collects views, runs the backtest,
# then stops the server. Logs: .state/f1_<tag>.log
set -euo pipefail
MODEL=${1:?hf model}; TAG=${2:?tag}; PORT=${3:-8011}; shift 3 2>/dev/null || true
ROOT=$(cd "$(dirname "$0")/.." && pwd); PY=$ROOT/.venv/bin/python; LOG=$ROOT/.state/f1_${TAG}.log
mkdir -p "$ROOT/.state"
echo "[$(date +%H:%M)] serving $MODEL" | tee -a "$LOG"
"$ROOT/src/serve.sh" "$MODEL" "$PORT" "$@" | tee -a "$LOG"
for i in $(seq 1 120); do
  if curl -sf "http://localhost:$PORT/v1/models" >/dev/null 2>&1; then break; fi
  sleep 10
done
curl -sf "http://localhost:$PORT/v1/models" >/dev/null || { echo "server did not come up"; tail -30 "$ROOT/.state/vllm_${PORT}.log"; exit 1; }
EXTRA=()
case "$MODEL" in openai/gpt-oss-*) EXTRA=(--max_tokens 1024 --reasoning low);; esac
echo "[$(date +%H:%M)] collecting views" | tee -a "$LOG"
"$PY" "$ROOT/src/02_get_views.py" --market US --model "$MODEL" --model_tag "$TAG" --prompt A --n 20 \
  --base_url "http://localhost:$PORT/v1" --concurrency 32 "${EXTRA[@]}" 2>&1 | grep -v Warning | tee -a "$LOG"
echo "[$(date +%H:%M)] backtest" | tee -a "$LOG"
"$PY" "$ROOT/src/03_backtest.py" --market US --model_tag "$TAG" --prompt A 2>&1 | grep -v Warning | tee -a "$LOG"
pkill -f "vllm serve $MODEL" || true
echo "[$(date +%H:%M)] done" | tee -a "$LOG"
