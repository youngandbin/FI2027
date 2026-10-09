# FI2027

LLM 반복 추출 예측을 Black–Litterman의 view와 view 불확실성으로 쓰는 연구를 **WRDS 데이터(시점별 지수 편입, 4개 시장)와 컷오프가 문서화된 오픈 LLM**으로 다시 검증한다. Financial Innovation 투고 트랙. EAAI 2026 투고작의 후속이며, IJCAI 2027 트랙(`../IJCAI2027`)과 코드를 공유한다.

- 운용 규칙·제약: `CLAUDE.md` · 설계: `docs/00_설계_WRDS_재검증.md` · 연구 가이드: `research_guide/`
- 데이터: `data/wrds/` (git 제외; WRDS에서 받은 CRSP·Compustat Global parquet), `data/rf/` (FRED, `src/01_get_rf.py`)

## 구조
```
src/blx/        실험 라이브러리: wrds(로더·시점 유니버스) engine(동적 유니버스 백테스트) bl views metrics calibration
src/01_get_rf.py     FRED 무위험수익률
src/02_get_views.py  vLLM 서버에서 반복 추출 view 수집 → data/views/{market}/{model}/{prompt}/
results/        결과·보고서
docs/           설계·조사·참고
paper/eaai2026/ EAAI 원고(출발점)
```

## 환경
```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python src/01_get_rf.py
# vLLM (GPU 1만): ../NAACL2027/shared/serve.sh 방식으로 띄운 뒤
.venv/bin/python src/02_get_views.py --market US --model google/gemma-3-27b-it --model_tag gemma3-27b --prompt A --n 20
```
