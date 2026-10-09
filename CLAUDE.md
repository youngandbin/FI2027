# FI2027: LLM 반복 추출 view × Black–Litterman, WRDS 데이터로 재검증 (Financial Innovation 투고 트랙)

목표: EAAI 2026 투고작("Integrating Large Language Models into Portfolio Optimization: A Black-Litterman Approach")을 **데이터·모델·평가를 바꿔** 다시 검증하고, 살아나면 Financial Innovation(Springer)에 낸다(사용자 결정 2026-10-09). IJCAI 2027 트랙(`../IJCAI2027`, 불확실성 신호 측정·보정)과는 별개 저장소이며 코드(`src/blx/`)를 공유한다.
설계 문서: `docs/00_설계_WRDS_재검증.md`. 왜 다시 하는지: EAAI 리뷰 3건과 IJCAI2027 파일럿(`docs/01`) — 파이프라인을 고치면 EAAI 효과가 사라지고, 숫자만 입력한 LLM 예측은 모멘텀의 변환이며, 반복 추출 분산은 과신.

## 사용자 제약 (2026-10-09)
- **GPU 1만 쓴다.** GPU 0은 다른 사람 것이므로 절대 쓰지 않는다. GPU 1을 다른 세션이 쓰고 있으면 끝날 때까지 기다린다(서버를 끄지 않는다). 띄우기 전에 `nvidia-smi`와 `ListAgents`로 확인.
- **상용 API 모델은 쓰지 않는다.** 로컬 오픈 모델만(vLLM). 모델은 컷오프가 개발사 문서로 확인된 것만 주 실험에 쓴다(`docs/R3`, `docs/R4`).
- 반복 횟수는 100이 아니라 20(파일럿: API 10, 로컬 8B 50에서 포화; F1에서 재확인).
- 커밋·push 허용. 원격: `git@github.com:youngandbin/FI2027.git`.

## 연구 가이드 (항상 따를 것)
이용재 교수의 Research/Writing Field Guide(`research_guide/RESEARCH_GUIDE.md`)를 따른다. 핵심: 방법보다 문제부터 / 한 문장 주장 / 새로움은 관점에서 / 실험은 주장을 검증 / leakage·평가 편향 점검 / negative result도 결과 / 재현성 / 핵심을 앞에 / 그림·표는 스스로 설명 / 진행 보고는 "이전 문제 → 변경 → 새 실험 → 결과·해석 → 남은 질문 → 다음 결정".
**모든 산출물 끝에 "가이드 점검" 절**: (1) 한 문장 주장, (2) 관련 원칙 번호와 충족 여부, (3) 세 질문(정확히 무엇을 주장하는가 / 실험이 검증하는가 / 회의적 독자가 납득하는가) 한 줄 답. 미충족은 must fix / important / nice to have로 분류.

## 데이터 (`data/wrds/`, git 제외, 사용자가 WRDS에서 받은 zip)
- CRSP(US S&P 500) + Compustat Global(KOSPI 200, Nikkei 225, DAX), 2000-01~2025-12-31, 시점별 지수 편입 기간(`member_start/end`), 총수익률(`ret`/`ret_local`), 시가총액(`mktcap` 천 USD / `mktcap_local`), 회사명·ISIN.
- 무위험수익률: FRED(`src/01_get_rf.py` → `data/rf/`). US 일별 DTB3, KR/JP/DE 월별 3개월 은행간 금리.
- 로더: `src/blx/wrds.py` (`load_market(key)` → 수익률·시가총액·편입 행렬, `universe(asof, top_n)`).

## 폴더
- `src/blx/` 실험 라이브러리(IJCAI2027과 동일 출발, 여기서 동적 유니버스·walk-forward τ·모멘텀 baseline을 추가). `src/paths.py`, `src/api_conf.py`(vLLM 엔드포인트).
- `src/0N_*.py` 단계별 스크립트. `results/` 결과·보고서. `docs/` 설계·조사. `paper/eaai2026/` EAAI 원고(FI 원고의 출발점), `paper/fi/`(예정).

## 환경
- Python 3.12, `uv`, `.venv`. vLLM은 `../NAACL2027/.venv/bin/vllm`(0.24.0)을 빌려 쓴다(`../NAACL2027/shared/serve.sh` 참고, CUDA compat LD_LIBRARY_PATH 필요). HF 캐시(`~/.cache/huggingface/hub`)에 받아 둔 모델을 우선 쓴다.
