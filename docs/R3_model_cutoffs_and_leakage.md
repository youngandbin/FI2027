# R3. 모델 선정표 (학습 데이터 컷오프) 및 누출(leakage) 문헌 조사

- 작성일: 2026-10-09 (모든 가격·문서 열람 날짜 동일)
- 목적: LLM 수치 수익률 예측 백테스트에서 **2025-07-01부터 시작하는 깨끗한 out-of-sample 구간**을 보장할 수 있는 모델을 고르고, 지식 컷오프 누출 관련 선행 연구를 정리한다.
- 원칙: 컷오프는 **개발사 자체 문서**(모델 카드·릴리스 블로그·API 문서)에서 읽은 것만 기재. 개발사가 공개하지 않으면 "미공개"로 표기하고 릴리스 날짜로 추정하지 않는다. 문서 간 불일치는 둘 다 기록.

---

## Part 1. 모델 선정표

### 1-A. 오픈 웨이트 모델

| 모델 | 정확한 버전 식별자 (HF repo / main revision sha, 2026-10-09 기준) | 파라미터 | 공개일 | 라이선스 | 학습 데이터 컷오프 (개발사 문서) | 출처 URL | temperature / logprobs |
|---|---|---|---|---|---|---|---|
| Llama 3.1 8B Instruct (baseline, 선행 연구 유지) | `meta-llama/Llama-3.1-8B-Instruct` @ `0e9e39f249a16976918f6564b8830bc894c89659` | 8B | 2024-07-23 ("Model Release Date: July 23, 2024") | Llama 3.1 Community License | **2023-12** ("The pretraining data has a cutoff of December 2023.") | https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct ; sha: https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct | vLLM: 둘 다 가능 (`SamplingParams.temperature`, `logprobs`, `prompt_logprobs`) https://docs.vllm.ai/en/latest/api/vllm/sampling_params.html |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` @ `6f6073b423013f6a7d4d9f39144961bfbfbc386b` | 70B (HF 메타데이터 71B) | 2024-12-06 ("70B Instruct: December 6, 2024") | Llama 3.3 Community License Agreement | **2023-12** ("The pretraining data has a cutoff of December 2023.") | https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct ; sha: https://huggingface.co/api/models/meta-llama/Llama-3.3-70B-Instruct | vLLM: 가능 |
| Llama 4 Scout | `meta-llama/Llama-4-Scout-17B-16E-Instruct` @ `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` | 17B active / 109B total (16 experts) | 2025-04-05 ("Model Release Date: April 5, 2025") | Llama 4 Community License Agreement | **2024-08** ("The pretraining data has a cutoff of August 2024.") | https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct ; sha: https://huggingface.co/api/models/meta-llama/Llama-4-Scout-17B-16E-Instruct | vLLM: 가능 |
| Llama 4 Maverick | `meta-llama/Llama-4-Maverick-17B-128E-Instruct` (sha 미조회) | 17B active / 400B total (128 experts; HF 메타데이터 402B) | 2025-04-05 | Llama 4 Community License Agreement (효력일 2025-04-05) | **2024-08** ("The pretraining data has a cutoff of August 2024.") | https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct | vLLM: 가능 (단 2×H100에는 부적합, 아래 참조) |
| Qwen2.5 7B / 14B / 32B / 72B Instruct | `Qwen/Qwen2.5-7B-Instruct` @ `a09a35458c702b33eeacc393d103063234e8bc28` (14B/32B/72B sha 미조회) | 7.61B / 14B / 32B / 72.7B | 2024-09-19 (블로그 게시일) | 7B·14B·32B: Apache-2.0; **3B·72B: Qwen license** ("All our open-source models, except for the 3B and 72B variants, are licensed under Apache 2.0.") | **미공개** (모델 카드·블로그 모두 컷오프 미기재; "18 trillion tokens"만 명시) | https://huggingface.co/Qwen/Qwen2.5-7B-Instruct ; https://huggingface.co/Qwen/Qwen2.5-72B-Instruct ; https://qwenlm.github.io/blog/qwen2.5/ | vLLM: 가능 |
| Qwen3 8B / 14B / 32B (dense) | `Qwen/Qwen3-8B` @ `b968826d9c46dd6066d109eabc6255188de91218`; `Qwen/Qwen3-32B` @ `9216db5781bf21249d130ec9da846c4624c16137` | 8.2B / 14B / 32.8B | 2025-04-29 (블로그 게시일) | Apache-2.0 (dense 6종) | **미공개** ("approximately 36 trillion tokens"만 명시) | https://huggingface.co/Qwen/Qwen3-8B ; https://huggingface.co/Qwen/Qwen3-32B ; https://qwenlm.github.io/blog/qwen3/ | vLLM: 가능 (thinking 모드 on/off 선택 필요) |
| Gemma 3 4B / 12B / 27B (it) | `google/gemma-3-27b-it` @ `005ad3404e59d6023443cb575daa05336842228a` (4B/12B sha 미조회) | 4B / 12B / 27B | 2025-03-12 (Google 블로그 게시일) | Gemma Terms of Use (커스텀 약관; HF 태그 `license: gemma`) | **2024-08** ("The knowledge cutoff date for the training data was August 2024.") | 컷오프: https://ai.google.dev/gemma/docs/core/model_card_3 ; 공개일: https://blog.google/technology/developers/gemma-3/ ; 약관: https://ai.google.dev/gemma/terms ; HF: https://huggingface.co/google/gemma-3-27b-it | vLLM: 가능 |
| Mistral Small 3.1 (2503) | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | 24B | HF 카드에 미기재; Mistral 블로그 2025-03-17 | Apache-2.0 | **미공개** — HF 카드에는 시스템 프롬프트 예시 문구 "Your knowledge base was last updated on 2023-10-01."만 있음(개발사가 컷오프로 명시한 것은 아님, 참고로만 기록) | https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503 ; https://mistral.ai/news/mistral-small-3-1 | vLLM: 가능 |
| Mistral Small 3.2 (2506) | `mistralai/Mistral-Small-3.2-24B-Instruct-2506` @ `95a6d26c4bfb886c58daf9d3f7332c857cb27b43` (HF createdAt 2025-06-19) | 24B | HF 카드에 미기재 (Mistral 문서 버전 "25.06"; API명 `mistral-small-2506`, API 폐기 2026-04-30 / 종료 2026-07-31) | Apache-2.0 | **미공개** | https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506 ; https://docs.mistral.ai/getting-started/models/models_overview | vLLM: 가능 |
| DeepSeek-V3 / V3-0324 | `deepseek-ai/DeepSeek-V3`, `deepseek-ai/DeepSeek-V3-0324` | 671B total / 37B active (HF 메타데이터 685B) | V3: 2024-12-26, V3-0324: 2025-03-25 (DeepSeek 뉴스 색인) | 코드 MIT; V3 가중치는 DeepSeek Model License("supports commercial use"); V3-0324는 MIT | **미공개** ("14.8 trillion diverse and high-quality tokens"만 명시) | https://huggingface.co/deepseek-ai/DeepSeek-V3 ; https://huggingface.co/deepseek-ai/DeepSeek-V3-0324 ; https://api-docs.deepseek.com/news/news1226 | vLLM: 가능하나 2×H100 불가 |
| DeepSeek-R1 / R1-0528 | `deepseek-ai/DeepSeek-R1`, `deepseek-ai/DeepSeek-R1-0528` | 671B total / 37B active | R1: 2025-01-20, R1-0528: 2025-05-28 (DeepSeek 뉴스 색인) | MIT | **미공개** | https://huggingface.co/deepseek-ai/DeepSeek-R1 ; https://huggingface.co/deepseek-ai/DeepSeek-R1-0528 ; https://api-docs.deepseek.com/news/news1226 (뉴스 색인) | vLLM: 가능하나 2×H100 불가 |
| DeepSeek-R1 Distill (Qwen 1.5B/7B/14B/32B, Llama 8B/70B; R1-0528-Qwen3-8B) | 예: `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` @ `711ad2ea6aa40cfca18895e8aca02ab92df1a746` | 베이스 모델 크기와 동일 (베이스: Qwen2.5-Math-1.5B/7B, Llama-3.1-8B, Qwen2.5-14B/32B, Llama-3.3-70B-Instruct; 0528 버전은 Qwen3-8B Base) | 2025-01-20 (R1와 동시); 0528-Qwen3-8B는 2025-05-28 | MIT | **미공개** (베이스가 Llama 계열이면 베이스 컷오프 2023-12가 하한이지만, 증류 데이터 자체의 컷오프는 미공개) | https://huggingface.co/deepseek-ai/DeepSeek-R1 ; https://huggingface.co/deepseek-ai/DeepSeek-R1-0528 | vLLM: 가능 |

### 1-B. API 모델

| 모델 | API 스냅샷 이름 | 파라미터 | 공개일 | 라이선스 | 학습 데이터 컷오프 (개발사 문서) | 출처 URL | 가격 (USD / 1M tokens, input / output; 2026-10-09 열람) | temperature / logprobs |
|---|---|---|---|---|---|---|---|---|
| GPT-4o mini | `gpt-4o-mini-2024-07-18` (유일 스냅샷) | 미공개 | 2024-07-18 (스냅샷명) | 상용 API | **2023-10-01** ("Oct 01, 2023 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-4o-mini | $0.15 / $0.60 (cached input $0.075) — https://developers.openai.com/api/docs/pricing | temperature 가능; Chat Completions `logprobs`/`top_logprobs`(0–20) 지원 (https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) |
| GPT-4.1 | `gpt-4.1-2025-04-14` | 미공개 | 2025-04-14 | 상용 API | **2024-06-01** ("Jun 01, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-4.1 | $2.00 / $8.00 (cached $0.50) | temperature·logprobs 가능 (비추론 모델) |
| GPT-4.1 mini | `gpt-4.1-mini-2025-04-14` | 미공개 | 2025-04-14 | 상용 API | **2024-06-01** ("Jun 01, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-4.1-mini | $0.40 / $1.60 (cached $0.10) | temperature·logprobs 가능 |
| GPT-5 | `gpt-5-2025-08-07` | 미공개 | 2025-08-07 | 상용 API | **2024-09-30** ("Sep 30, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-5 | $1.25 / $10.00 (cached $0.125) | 추론 모델. 현재 공식 모델 페이지·reasoning 가이드에는 temperature/logprobs 지원 여부가 **명시돼 있지 않음**. 커뮤니티 보고: gpt-5 계열에서 400 에러 "logprobs are not supported with reasoning models." (https://community.openai.com/t/gpt-5-2-logprobs-support-removed/1378114, 2026-03-30; 비공식) → 실제 호출로 확인 필요 |
| GPT-5 mini | `gpt-5-mini-2025-08-07` | 미공개 | 2025-08-07 | 상용 API | **2024-05-31** ("May 31, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-5-mini | $0.25 / $2.00 (cached $0.025) | 상동 |
| GPT-5 nano | `gpt-5-nano-2025-08-07` | 미공개 | 2025-08-07 | 상용 API | **2024-05-31** ("May 31, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/gpt-5-nano | $0.05 / $0.40 (cached $0.005) | 상동 |
| o3 | `o3-2025-04-16` | 미공개 | 2025-04-16 | 상용 API | **2024-06-01** ("Jun 01, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/o3 | $2.00 / $8.00 (pricing 페이지 및 모델 페이지 주표). **불일치**: o3 모델 페이지에 라벨 없는 두 번째 표 $1 / $4가 함께 표시됨 | 상동 (추론 모델) |
| o4-mini | `o4-mini-2025-04-16` | 미공개 | 2025-04-16 | 상용 API | **2024-06-01** ("Jun 01, 2024 knowledge cutoff") | https://developers.openai.com/api/docs/models/o4-mini | $1.10 / $4.40 (cached $0.275) | 상동 |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | 미공개 | 2025-09-29 | 상용 API | **Reliable knowledge cutoff: 2025-01 / Training data cutoff: 2025-07** (두 값을 구분해 공개) | https://platform.claude.com/docs/en/models/sonnet-4-5/overview | $3 / $15 (Batch 50% 할인). 상태: **Deprecated** (2026-09-30), 종료 2026-11-30 — https://platform.claude.com/docs/en/about-claude/pricing | temperature 가능(4.5 세대); **logprobs 없음** — Messages API 요청 파라미터 목록에 logprobs 항목 부재 (https://platform.claude.com/docs/en/api/messages). 참고: 같은 페이지에 "Models released after Claude Opus 4.6 do not support setting temperature" 명시 |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | 미공개 | 2025-10-15 | 상용 API | **Reliable: 2025-02 / Training data: 2025-07** | https://platform.claude.com/docs/en/models/haiku-4-5/overview | $1 / $5 (Batch $0.50 / $2.50). 상태: Active (legacy), 종료 2026-10-15 이후 | 상동 (logprobs 없음) |
| Claude Sonnet 4.6 (참고) | `claude-sonnet-4-6` | 미공개 | 2026-02-17 | 상용 API | **Reliable: 2025-08 / Training data: 2026-01** → 2025-07-01 OOS 조건 위반 | https://platform.claude.com/docs/en/models/sonnet-4-6/overview | $3 / $15 | temperature 미지원 세대 경계(4.6 이후 미지원), logprobs 없음 |
| Gemini 2.5 Pro | `gemini-2.5-pro` (Stable) | 미공개 | GA 2025-06-17 (Vertex "Release date: June 17, 2025"); Vertex 종료일 **2026-10-20** | 상용 API | **2025-01** ("Knowledge cutoff: January 2025", "Latest update: June 2025") | https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro ; https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro | $1.25 / $10.00 (≤200k 프롬프트; >200k는 $2.50 / $15.00; output은 thinking 포함) — https://ai.google.dev/gemini-api/docs/pricing | temperature 가능; `responseLogprobs`(bool) + `logprobs`(1–20) 지원. 단 "deprecated for Gemini 3.x models and will soon be completely deprecated" (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference) |
| Gemini 2.5 Flash | `gemini-2.5-flash` (Stable) | 미공개 | GA 2025-06-17; Vertex 종료일 **2026-10-20** | 상용 API | **2025-01** ("Knowledge cutoff: January 2025") | https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash ; https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash | $0.30 / $2.50 (output thinking 포함) | 상동 |

참고(가격 비교용, 2026-10-09 열람): DeepSeek API는 현재 `deepseek-flash`(V4.1-Flash, $0.15–0.30 / $0.60–1.20 off-peak/peak)와 `deepseek-v4-pro`만 제공하며 V3/R1은 가격표에서 사라짐 (https://api-docs.deepseek.com/quick_start/pricing). V3 출시 당시 가격은 $0.27 / $1.10 (https://api-docs.deepseek.com/news/news1226). Mistral API는 Small 3.1/3.2가 폐기 예정이고 Mistral Small 4 (`mistral-small-2603`, 119B total / 6.5B active, Apache-2.0)가 $0.15 / $0.60 (https://docs.mistral.ai/inference/pricing).

### 1-C. 2025-07-01 OOS 기준 판정 및 추천

**판정 기준**: 개발사가 문서화한 학습 데이터 컷오프 ≤ 2025-06-30. 릴리스 날짜만으로는 통과시키지 않음.

| 판정 | 모델 |
|---|---|
| 통과 (문서화된 컷오프 ≤ 2025-06-30) | Llama 3.1 8B (2023-12), Llama 3.3 70B (2023-12), Llama 4 Scout/Maverick (2024-08), Gemma 3 4B/12B/27B (2024-08), GPT-4o mini (2023-10-01), GPT-4.1/4.1 mini (2024-06-01), GPT-5/mini/nano (2024-09-30 / 2024-05-31), o3/o4-mini (2024-06-01), Gemini 2.5 Pro/Flash (2025-01) |
| 경계 (보수적으로 제외) | Claude Sonnet 4.5·Haiku 4.5: reliable cutoff는 2025-01/02이지만 **training data cutoff가 2025-07**로 OOS 시작월과 겹침. Anthropic이 두 값을 구분 공개하므로, 보수적 기준(training data cutoff)으로는 탈락. 쓰려면 OOS 시작을 2025-08-01 이후로 미루거나 "reliable cutoff 기준"임을 명시해야 함 |
| 판정 불가 (컷오프 미공개) | Qwen2.5 전 사이즈, Qwen3 dense, Mistral Small 3.1/3.2, DeepSeek-V3/R1 및 distill. (공개일이 2025-06-30 이전이므로 물리적으로 그 이후 데이터는 포함될 수 없으나, 이는 "개발사 문서화"가 아니므로 주 실험에서 제외하고 민감도 분석에만 사용 권장) |
| 탈락 | Claude Sonnet 4.6 (training 2026-01), Claude 5.x·GPT-6·Gemini 3.x 등 2026년 모델 전부 |

**추천 조합 (2×H100 80GB + vLLM, API 1–2개)**

1. **Llama 3.1 8B Instruct** (baseline, 선행 연구와 연속성; bf16 1×H100 충분).
2. **Gemma 3 27B it** (컷오프 2024-08 문서화, bf16 ~54GB로 1×H100에 적재 가능, Apache가 아닌 Gemma Terms이므로 논문 공개 시 약관 준수 확인).
3. **Llama 3.3 70B Instruct** (컷오프 2023-12 문서화). bf16 가중치 ~140GB로 2×H100(160GB) tensor-parallel 시 KV 캐시 여유가 매우 적으므로 **FP8 양자화 또는 `--max-model-len` 축소** 전제. 대안: Llama 4 Scout (109B total)는 bf16으로 2×H100에 들어가지 않아 FP8 전제 — 70B dense가 더 단순.
   - Qwen3-32B는 성능이 좋지만 컷오프 미공개이므로 부록 민감도용으로만.
4. API: **GPT-4.1 mini** (`gpt-4.1-mini-2025-04-14`; 컷오프 2024-06-01, $0.40/$1.60, logprobs·temperature 모두 지원 → 수치 예측의 분포 분석에 유리). 선행 연구 연속성이 필요하면 **GPT-4o mini (2024-07-18)** 유지.
5. API(선택): **Gemini 2.5 Flash** (컷오프 2025-01, $0.30/$2.50, logprobs 지원). **주의: Vertex 종료일 2026-10-20**, Gemini API 쪽은 "will continue to be served until further notice"이므로 실험을 즉시 돌리고 결과를 고정해 둘 것. 추론 모델(GPT-5, o3, o4-mini)은 logprobs 미지원 가능성이 높고 temperature 제어도 불명확하므로 수치 예측 주실험보다는 보조 비교군으로.

---

## Part 2. 누출(look-ahead / memorization / cutoff contamination) 문헌 조사

| # | 제목 | 저자 | 발표처 / 연도 | URL | 핵심 발견 (한 줄) | 검증 방법 |
|---|---|---|---|---|---|---|
| 1 | Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis | Paul Glasserman, Caden Lin | arXiv 2309.17322 (q-fin.GN), 2023-09-29 (v1만 존재) | https://arxiv.org/abs/2309.17322 | 학습 구간 내에서는 헤드라인에서 기업 식별자를 익명화하면 오히려 성과가 좋아져 "distraction" 효과가 look-ahead보다 컸고, 컷오프 이후 OOS에서는 look-ahead가 문제되지 않는다고 결론 | arXiv abs 페이지 WebFetch로 제목·저자·제출일·초록 확인 |
| 2 | Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models | Alejandro Lopez-Lira, Yuehua Tang | arXiv 2304.07619, v1 2023-04-15 ~ v6 2025-10-28 (SSRN 선게시) | https://arxiv.org/abs/2304.07619 | 모델 지식 컷오프 **이후** 뉴스 헤드라인만 사용해 GPT-4 점수가 익일 수익률을 예측함을 보임 — post-cutoff 평가 설계의 초기 사례 | arXiv abs 페이지 WebFetch로 확인 (초록에 "post-knowledge-cutoff" 명시) |
| 3 | Lookahead Bias in Pretrained Language Models | Suproteem Sarkar, Keyon Vafa | ICML 2025 Workshop on Reliable and Responsible Foundation Models (포스터) | https://icml.cc/virtual/2025/50857 | 예측 불가능해야 할 사건(어닝콜→리스크 요인, 후보 약력→선거 결과)으로 직접 검정해 사전학습 모델에 lookahead bias가 존재함을 입증; 프롬프트 기반 완화는 효과 제한적, 분석 기간 이전 텍스트로만 학습한 모델 사용을 권고 | ICML 가상 페이지 WebFetch로 제목·저자·초록 확인 |
| 4 | Chronologically Consistent Large Language Models (ChronoBERT / ChronoGPT) | Songrun He, Linying Lv, Asaf Manela, Jimmy Wu | arXiv 2502.21206, v1 2025-02-28, v3 2025-07-06 | https://arxiv.org/abs/2502.21206 | 시점별로 그 이전 텍스트만으로 학습한 모델 계열을 공개; 뉴스→익일 수익률 예측에서 Llama 대비 Sharpe가 유사해 lookahead bias는 "modest"하다고 보고 | arXiv abs 페이지 WebFetch로 확인 |
| 5 | Instruction Tuning Chronologically Consistent Language Models | Songrun He, Linying Lv, Asaf Manela, Jimmy Wu | arXiv 2510.11677, v1 2025-10-13, v2 2025-11-17 | https://arxiv.org/abs/2510.11677 | 고정 컷오프 이전 데이터만으로 instruction-tuned 모델을 만들어 lookahead 없는 "보수적 하한" 예측 정확도를 제공 | arXiv abs 페이지 WebFetch로 확인 |
| 6 | Large Language Models: An Applied Econometric Framework | Jens Ludwig, Sendhil Mullainathan, Ashesh Rambachan | arXiv 2412.07031 (econ.EM), v1 2024-12-09, v4 2025-12-05 | https://arxiv.org/abs/2412.07031 | 예측 과제에서 LLM 결론이 타당하려면 "no training leakage"(학습 데이터와 연구 표본의 비중첩)가 필요하며 모델 선택·연구 설계로 보장해야 한다고 정식화 | arXiv abs 페이지 WebFetch로 확인 |
| 7 | Detecting Lookahead Bias in LLM Forecasts | Zhenyu Gao, Wenxi Jiang, Yutong Yan | arXiv 2512.23847, v1 2025-12-29, v2 2026-06-12 | https://arxiv.org/abs/2512.23847 | 날짜만 주고 회상시키는 "Lookahead Propensity" 통계량을 제안; Llama-3.3-70B에서 컷오프(2023-12) 이전 구간엔 양(+)이다가 이후 구간에서 0으로 붕괴, 예측력-LAP 상호작용도 post-cutoff에서 유의성 상실 | arXiv abs 페이지 WebFetch + 검색 결과 요약 대조 |
| 8 | DatedGPT: Preventing Lookahead Bias in Large Language Models with Time-Aware Pretraining | Yutong Yan, Raphael Tang, Zhenyu Gao, Wenxi Jiang, Yao Lu | arXiv 2603.11838, v1 2026-03-12, v2 2026-07-23 | https://arxiv.org/abs/2603.11838 | 2013–2024 연도별 컷오프로 1.3B 모델 12개를 처음부터 학습; 결과 구간을 학습한 모델은 수익률 프리미엄이 부풀려짐(검색 요약: 26.4 bp/SD, t=10.65) | arXiv abs 페이지 WebFetch로 제목·저자·초록 확인 (효과 크기 수치는 검색 스니펫 기반) |
| 9 | A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs | Humzah Merchant, Bradford Levy | arXiv 2512.06607, v1 2025-12-07, v2 2026-09-23 | https://arxiv.org/abs/2512.06607 | 재학습 없이 추론 시 두 개의 소형 모델(잊을 정보/유지할 정보)로 로짓을 보정해 특정 시점 이후 지식을 제거하는 방법 제안 | arXiv abs 페이지 WebFetch로 확인 |
| 10 | Evaluating LLMs in Finance Requires Explicit Bias Consideration | Yaxuan Kong, Hoyoung Lee, Yoontae Hwang, Alejandro Lopez-Lira, Bradford Levy, Dhagash Mehta, Qingsong Wen, Chanyeol Choi, Yongjae Lee, Stefan Zohren | arXiv 2602.14233, 2026-02-15 (position paper) | https://arxiv.org/abs/2602.14233 | look-ahead·생존 편향 등 금융 고유 편향이 LLM 성과를 부풀리므로("time travel") 배포 주장 전에 구조적 타당성 점검을 요구 | arXiv abs 페이지 WebFetch로 확인 |
| 11 | Time Travel in LLMs: Tracing Data Contamination in Large Language Models | Shahriar Golchin, Mihai Surdeanu | ICLR 2024 Spotlight; arXiv 2308.08493 | https://arxiv.org/abs/2308.08493 | (일반 NLP) 다운스트림 테스트셋 오염을 guided-prompting으로 탐지하는 방법; GPT-4의 AG News·WNLI·XSum 오염 확인 — 금융 특화는 아니지만 "time travel" 용어의 원류 | arXiv abs 페이지 WebFetch로 확인 |
| 12 | ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities | Ezra Karger, Houtan Bastani, Chen Yueh-Han, Zachary Jacobs, Danny Halawi, Fred Zhang, Philip E. Tetlock | arXiv 2409.19839, v5 2025-02-28 (ICLR 2025 게재 여부는 abs 페이지에 미표기) | https://arxiv.org/abs/2409.19839 | 제출 시점에 미해결인 질문만 사용해 누출을 설계상 차단; LLM이 전문가 예측가보다 유의하게 못함 | arXiv abs 페이지 WebFetch로 확인 |
| 13 | LEAF: A Living Benchmark for Event-Augmented Forecasting | Mingtian Tan, Mihir Parmar, Palash Goyal, Chun-Liang Li, Nanyun Peng, Thomas Hartvigsen, Jinsung Yoon, Tomas Pfister | arXiv 2605.16358, v1 2026-05-09, v2 2026-10-01 | https://arxiv.org/abs/2605.16358 | 주식·원자재 등 시계열에서 컷오프 이전 데이터로 평가하면 정확도가 최대 147% 부풀려진다고 보고(검색 스니펫); 지속 갱신 테스트셋과 미래정보 누출 필터(8.6%→1.6%) 제안 | arXiv abs 페이지 WebFetch로 제목·저자·초록 확인 (147% 수치는 검색 스니펫 기반) |

**시사점 (우리 설계에 대한 함의)**
- 문헌 공통 권고는 (i) 컷오프 이후 구간만 평가, (ii) 시점 고정 모델(Chrono*, DatedGPT) 사용, (iii) 누출 직접 검정(#3, #7의 date-only recall 검정) 중 하나 이상을 병행하는 것. 우리 백테스트는 (i)를 기본으로 하고, #7의 Lookahead Propensity 검정을 2025-07 이전/이후 구간에 적용해 "컷오프 이후 LAP≈0"을 보이면 설득력이 커진다.
- #1·#4는 look-ahead 효과가 작다고 보고하나 #7·#8·#13은 유의하게 크다고 보고 → 양쪽 모두 인용하고, 우리 결과에서 in-sample vs post-cutoff 성과 차이를 직접 제시할 것.

---

## 검증하지 못한 항목

1. **OpenAI 추론 모델(GPT-5 계열, o3, o4-mini)의 temperature/logprobs 지원 여부**: 현재 공식 모델 페이지와 reasoning 가이드(https://developers.openai.com/api/docs/guides/reasoning)에 명시가 없음. "logprobs are not supported with reasoning models" 문구는 커뮤니티 포럼 인용(비공식). Chat Completions 레퍼런스 페이지(https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)는 직접 fetch 시 404 두 차례 → logprobs/top_logprobs 설명은 검색 엔진 스니펫으로만 확인.
2. **Anthropic Messages API의 logprobs 부재**: 요청 파라미터 목록(페이지 앞부분 100k자)에 logprobs가 없음을 확인했을 뿐, 페이지 전체(1.17M자)를 읽지 못함. 공식 "미지원" 선언 문장은 찾지 못함.
3. **Gemini 2.5 Pro/Flash 모델 카드 PDF**(https://storage.googleapis.com/model-cards/documents/gemini-2.5-pro.pdf, …/gemini-2.5-flash.pdf): 403으로 직접 열람 실패. 컷오프 2025-01은 ai.google.dev 모델 페이지로 확인했으므로 결론에는 영향 없음.
4. **Mistral Small 3.1/3.2 공식 공개일**: HF 카드에 미기재. 3.1은 Mistral 블로그(2025-03-17)로 확인, 3.2는 Mistral 문서의 버전 "25.06"과 HF createdAt(2025-06-19)만 확보.
5. **Mistral Small 3.1/3.2 API 가격**: 폐기 예정 모델이라 현재 가격표에 없음.
6. **DeepSeek-R1 API 가격**: 뉴스 페이지(news250120) fetch가 quick-start로 대체돼 당시 가격을 읽지 못함; 현재 가격표에서는 R1/V3가 제거됨.
7. **Llama 4 Maverick, Qwen2.5-14B/32B/72B, Qwen3-14B, Gemma 3 4B/12B의 HF main revision sha**: 조회하지 않음 (해당 repo의 컷오프·라이선스는 모델 카드로 확인).
8. **OpenAI 파라미터 수**(모든 API 모델)와 Anthropic·Google 파라미터 수: 개발사 미공개.
9. **o3 가격 불일치**($2/$8 vs 모델 페이지 내 라벨 없는 $1/$4 표): 두 번째 표의 적용 범위(Flex 등)를 확인하지 못함.
10. **DatedGPT(26.4 bp/SD)·LEAF(147%) 효과 크기**: 초록이 아닌 검색 스니펫에서 가져온 수치이므로 본문 인용 전 원문 확인 필요.
11. **ForecastBench의 ICLR 2025 게재 여부**: arXiv abs 페이지에 venue 미표기.
