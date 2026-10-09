#!/usr/bin/env bash
# Start a vLLM OpenAI-compatible server on GPU 1 ONLY (user constraint: GPU 0 belongs to someone else).
# Usage: src/serve.sh <model> [port] [extra vllm args]
#   src/serve.sh openai/gpt-oss-20b 8011
#   src/serve.sh google/gemma-3-27b-it 8011 --max-model-len 4096
#   src/serve.sh RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic 8011 --max-model-len 4096 --gpu-memory-utilization 0.95
# Refuses to start if GPU 1 is already in use by another process.
set -euo pipefail
MODEL=${1:?model}; PORT=${2:-8011}; shift 2 2>/dev/null || true
ROOT=$(cd "$(dirname "$0")/.." && pwd)
NAACL=$ROOT/../NAACL2027
[ -f "$NAACL/.env" ] && { set -a; . "$NAACL/.env"; set +a; }   # HF_TOKEN for gated models
export LD_LIBRARY_PATH=/home/elice/cuda-compat/usr/local/cuda-13.4/compat:${LD_LIBRARY_PATH:-}
USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)
if [ "$USED" -gt 2000 ]; then echo "GPU 1 is in use (${USED} MiB). Not starting."; exit 1; fi
mkdir -p "$ROOT/.state"
CUDA_VISIBLE_DEVICES=1 nohup "$NAACL/.venv/bin/vllm" serve "$MODEL" --port "$PORT" --enable-prefix-caching "$@" \
  > "$ROOT/.state/vllm_${PORT}.log" 2>&1 &
echo "pid $! model $MODEL port $PORT log $ROOT/.state/vllm_${PORT}.log"
