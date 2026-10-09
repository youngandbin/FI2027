# R4. 로컬 모델 지식 컷오프·스펙 검증 (개발사 1차 자료 기준)

조사일: 2026-10-09. 원칙: 개발사(OpenAI/Google/Qwen/NVIDIA/Meta/RedHat) 자체 모델카드·블로그·문서만 인용. 출시일로 컷오프를 추정하지 않음. 개발사가 명시하지 않으면 "미공개".
HF repo `createdAt`은 HF API(`/api/models/<repo>`)에서 읽은 개발사 업로드 시각이며, 공식 출시일이 없을 때만 보조 근거로 표기.

## 1. 요약 표

| Model | 지식 컷오프 (원문) | 파라미터 (총/활성) | 라이선스 | 출시일 | vLLM 지원 | 근거 URL |
|---|---|---|---|---|---|---|
| openai/gpt-oss-120b | **2024-06** — "Our model has a knowledge cutoff of June 2024." (모델카드 PDF §Pre-training, p.6); 개발자 문서 "Jun 01, 2024 knowledge cutoff". HF 카드에는 컷오프 없음 | 117B / 5.1B active (MoE) | Apache 2.0 | 2025-08-05 (모델카드 PDF 표지 날짜; HF createdAt 2025-08-04) | HF 카드 `vllm serve openai/gpt-oss-120b` | https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf · https://developers.openai.com/api/docs/models/gpt-oss-120b · https://huggingface.co/openai/gpt-oss-120b |
| openai/gpt-oss-20b | **2024-06** (위와 동일 문서, 두 모델 공통) | 21B / 3.6B active (MoE) | Apache 2.0 | 2025-08-05 (동일) | HF 카드 `vllm serve openai/gpt-oss-20b` | https://developers.openai.com/api/docs/models/gpt-oss-20b · https://huggingface.co/openai/gpt-oss-20b |
| google/gemma-4-31B-it | **2025-01** — "...with a cutoff date of January 2025." (HF 카드 §Training Dataset; ai.google.dev model_card_4 동일) | 30.7B dense | Apache 2.0 | 2026-04-02 (Google 블로그 게시일; HF createdAt 2026-03-11) | HF 카드 "How to use ... with vLLM" `vllm serve` 스니펫 | https://huggingface.co/google/gemma-4-31B-it · https://ai.google.dev/gemma/docs/core/model_card_4 · https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ |
| google/gemma-4-26B-A4B-it | **2025-01** (동일 문구) | 25.2B / 3.8B active (MoE) | Apache 2.0 | 2026-04-02 (동일) | HF 카드 `vllm serve` 스니펫 | https://huggingface.co/google/gemma-4-26B-A4B-it |
| Qwen/Qwen3.8-27B | **미공개** (HF 카드·인용 블로그 어디에도 cutoff 문구 없음) | 27B dense ("Number of Parameters: 27B"; safetensors 27.8B) | Apache 2.0 | 2026-08 (HF 카드 citation `month={August}, year={2026}`; HF createdAt 2026-08-05; 컬렉션 "Updated Aug 13") | HF 카드 "compatible with Hugging Face Transformers, vLLM, SGLang, TokenSpeed" | https://huggingface.co/Qwen/Qwen3.8-27B |
| Qwen/Qwen3-32B | **미공개** (확인: HF 카드·Qwen3 블로그 모두 없음) | 32.8B dense | Apache 2.0 | 2025-04-29 (Qwen 블로그 게시일; HF createdAt 2025-04-27) | HF 카드 `vllm>=0.8.5`, `vllm serve Qwen/Qwen3-32B --enable-reasoning --reasoning-parser deepseek_r1` | https://huggingface.co/Qwen/Qwen3-32B · https://qwenlm.github.io/blog/qwen3/ |
| Qwen/Qwen3-8B | **미공개** (동일) | 8.2B dense (non-embedding 6.95B) | Apache 2.0 | 2025-04-29 (동일) | HF 카드 `vllm>=0.8.5` | https://huggingface.co/Qwen/Qwen3-8B |
| nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | **사전학습 2025-09 / 사후학습 2026-05** — "The pre-training data has a cutoff date of September 2025." "The post-training data has a cutoff date of May 2026." (§Data Freshness) | 30B / 3B active (MoE) | OpenMDW-1.1 (HF 메타 `other`) | 2026-08-11 (§Release Date "Hugging Face — 08/11/2026") | HF 카드 Quick Start `vllm/vllm-openai:v0.27.1` 도커 `vllm serve` | https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 |
| google/gemma-3-27b-it | **2024-08** — "The knowledge cutoff date for the training data was August 2024." (ai.google.dev Gemma 3 model card §Training Dataset). **HF 카드 본문에는 컷오프 문구 없음**(토큰 수 14T만 기재) | 27B dense | Gemma Terms of Use (HF `license: gemma`, gated) | 2025-03-12 (Google 블로그 "Today, we're introducing Gemma 3"; HF createdAt 2025-03-01) | HF 카드 `vllm serve "google/gemma-3-27b-it"` 스니펫 | https://ai.google.dev/gemma/docs/core/model_card_3 · https://huggingface.co/google/gemma-3-27b-it · https://blog.google/technology/developers/gemma-3/ |
| google/gemma-3-12b-it | **2024-08** (동일 페이지, 12B도 동일 문구 적용; 12T tokens) | 12B dense | Gemma Terms of Use (gated) | 2025-03-12 (동일) | HF 카드 `vllm serve` 스니펫 | https://huggingface.co/google/gemma-3-12b-it |
| meta-llama/Llama-3.3-70B-Instruct | **2023-12** — "The pretraining data has a cutoff of December 2023." (§Data Freshness) | 70B dense | Llama 3.3 Community License (gated) | 2024-12-06 ("70B Instruct: December 6, 2024") | HF 카드 `vllm serve` 스니펫 | https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct |

## 2. gpt-oss 추가 확인 (샘플링·reasoning effort)
- 샘플링: GitHub README(openai/gpt-oss) "We recommend sampling with `temperature=1.0` and `top_p=1.0`." → temperature 조절 자체는 지원(HF 카드에는 샘플링 가이드 없음). https://github.com/openai/gpt-oss
- Reasoning effort: HF 카드 low("Fast responses for general dialogue") / medium("Balanced speed and detail") / high("Deep and detailed analysis"), 시스템 프롬프트 `Reasoning: high`로 지정. (참고) Qwen3.8-27B는 `reasoning_effort` xhigh(default)/medium/low, thinking 모드 권장 temperature=1.0, top_p=0.95.

## 3. Llama 3.3 70B FP8 변형 (HF repo명)
| Repo | 양자화 | 라이선스 | 출시일 | vLLM | URL |
|---|---|---|---|---|---|
| RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic | W8A8 FP8, weight static per-channel / activation dynamic per-token (llm-compressor) | llama3.3 | 2024-12-11 | "deployed efficiently using the vLLM backend" | https://huggingface.co/RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic |
| nvidia/Llama-3.3-70B-Instruct-FP8 | TensorRT Model Optimizer v0.27.1 (static per-tensor) | nvidia-open-model-license + llama3.3 | 2025-05-09 | "Supported Runtime Engine(s)"에 vLLM 명시 | https://huggingface.co/nvidia/Llama-3.3-70B-Instruct-FP8 |
- `neuralmagic/Llama-3.3-70B-Instruct-FP8-dynamic`: HF API 응답 없음(namespace가 RedHatAI로 이관됨). RedHatAI repo 사용할 것. FP8 변형의 컷오프는 base와 동일(별도 기재 없음).

## 4. 2024-08-31 이전 컷오프가 문서화된 모델 (OOS 2024-09-01 시작 시 clean)
| 판정 | 모델 | 근거 |
|---|---|---|
| **clean** | gpt-oss-20b, gpt-oss-120b | June 2024 (OpenAI 모델카드) — 3개월 여유 |
| **clean (경계)** | gemma-3-27b-it, gemma-3-12b-it | August 2024 (ai.google.dev) — 8월 말까지 데이터 포함 가능, 9/1 시작이면 겹침 없음이나 여유 0. HF 카드엔 미기재이므로 논문 인용 시 ai.google.dev 페이지를 인용 |
| **clean** | Llama-3.3-70B-Instruct (+ RedHatAI/nvidia FP8) | December 2023 — 8개월 여유 |
| **not clean** | gemma-4-31B-it, gemma-4-26B-A4B-it | January 2025 |
| **not clean** | Nemotron-3.5-Lightning-30B-A3B | 사전학습 2025-09, 사후학습 2026-05 |
| **판정 불가** | Qwen3.8-27B, Qwen3-32B, Qwen3-8B | 컷오프 미공개. 출시일(2025-04 / 2026-08)로 추정 금지. 사용 시 "컷오프 미공개" 명시 필요 |

## 5. 확인 불가 목록
- OpenAI 블로그 "Introducing gpt-oss"(openai.com/index/introducing-gpt-oss) 및 help.openai.com: HTTP 403으로 본문 열람 불가. 컷오프는 모델카드 PDF(cdn.openai.com)와 developers.openai.com에서 확인했으므로 결론에 영향 없음.
- Qwen3.8 공식 블로그(https://qwen.ai/blog?id=qwen3.8): JS 렌더링으로 본문 미수집. Qwen3.8-27B 정확한 출시일(일 단위)은 개발사 문서에서 확인 못함 → "2026-08"로만 기재.
- gpt-oss HF 모델카드 자체에는 knowledge cutoff·temperature 문구 없음(개발사 다른 문서로 보완).
- Gemma 3 HF 모델카드 본문에 컷오프 없음(ai.google.dev 모델카드로 보완). Gemma 3/4 HF 카드에는 출시일 없음(Google 블로그로 보완).
- Nemotron 3.5 Lightning HF 카드 마지막 ~1.5K자 미열람(길이 초과). 핵심 항목은 앞부분에서 모두 확인.
