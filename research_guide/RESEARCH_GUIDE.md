# Research / Writing Field Guide (이용재)

- 출처: https://research-writing-field-guide.yongjaeleee.chatgpt.site/
- 저자: 이용재 (UNIST 부교수 · LinqAlpha Chief Scientist)
- 저장일: 2026-10-05
- 이 프로젝트에서 하는 모든 연구 작업(아이디어 도출, 설계, 실험, 집필, 진행 보고)은 이 가이드를 기준으로 삼는다.
- 1부와 2부는 원문을 그대로 옮겼다. 3부는 원문이 아니라, 이 가이드를 각 연구 단계에 적용하기 위해 정리한 체크리스트다.

---

## 1부. 원문 (한국어)

**학생 연구자를 위한 필드 가이드**

### 좋은 연구는 좋은 질문에서 시작됩니다.

논문은 얼마나 많은 일을 했는지를 보여주는 기록을 넘어, 중요한 주장을 독자가 납득할 수 있도록 증거를 차근차근 엮어 가는 글입니다.

이 가이드는 제가 평소 Slack에서 학생들에게 남긴 연구 피드백과 OpenReview에서 작성한 논문 리뷰를 바탕으로, GPT가 반복되는 관점과 조언을 정리해 재구성한 자료입니다.

#### 01. 방법보다 문제부터 살펴보기
*모델보다 먼저, 어디에서 실패가 생기는지 살펴보면 좋습니다.*

연구를 시작할 때는 사용할 모델이나 기술부터 정하기보다, 무엇이 제대로 작동하지 않는지부터 살펴보는 편이 좋습니다. 그 실패가 왜 중요하고, 기존 접근의 어떤 구조적 한계 때문에 해결되지 않는지를 정리하면 연구의 방향도 한층 선명해집니다.

'LLM을 금융에 적용한다'거나 '그래프 모델을 사용한다'는 아이디어만으로는 연구 문제를 충분히 설명하기 어렵습니다. 구체적인 실패 사례나 현실의 제약에서 이야기를 시작해 보세요. 첫 페이지를 읽은 독자가 이 문제가 실제로 존재하며 단순한 기존 방법만으로는 해결하기 어렵다는 점을 자연스럽게 이해할 수 있으면 좋습니다.

- 구체적으로 무엇이 실패하고 있나요?
- 그 실패는 왜 중요한가요?
- 기존 방법이 어려움을 겪는 구조적 이유는 무엇인가요?
- 이번 연구에서 다루려는 범위는 어디까지인가요?

#### 02. 핵심 주장을 한 문장으로 정리하기
*Contribution이 선명해지면 실험의 방향도 함께 또렷해집니다.*

'새로운 프레임워크를 제안합니다'라는 표현에서 한 걸음 더 나아가면 좋습니다. 무엇을 바꾸었고, 그 변화가 어떤 문제를 해결하며, 어느 조건에서 효과적인지를 한 문장으로 정리해 보세요.

그다음에는 주요 실험이 이 주장과 직접 연결되는지 차례로 확인해 볼 수 있습니다. 흥미롭지만 서로 떨어진 결과를 많이 보여주기보다, 중요한 질문에 정확히 답하는 소수의 실험이 더 설득력 있게 다가오는 경우가 많습니다.

#### 03. 부품의 수보다 새로운 관점에 집중하기
*표준 기법의 조합도 유용하지만, 새로움은 대개 문제를 바라보는 관점에서 나옵니다.*

Change-point detection, contrastive learning, LoRA, mixture-of-experts 같은 기법을 조합하는 것만으로 새로움이 충분히 드러나지는 않을 수 있습니다. 새로운 문제 정의, 이전에는 측정하기 어려웠던 대상, 도메인 특성 때문에 필요한 설계, 혹은 기존 실패를 설명하는 새로운 관점이 있는지 살펴보세요.

특히 금융 연구라면 거래비용, 위험 제약, 비정상성, 정보 공개 시점, 데이터 수정, 실제 운용 조건이 방법이나 평가에 어떻게 반영되는지가 중요합니다. 일반적인 머신러닝을 금융 데이터에 적용하는 데서 그치지 않고, 금융이라는 맥락이 연구 설계에 어떤 차이를 만드는지 보여주면 좋습니다.

#### 04. 실험으로 성능과 주장을 함께 점검하기
*주장을 먼저 정리하면, 그 주장에 꼭 필요한 증거도 더 잘 보입니다.*

Baseline은 이기기 쉬운 모델만 선택하기보다, 독자가 떠올릴 단순한 대안과 가장 강한 관련 방법을 함께 포함하는 편이 좋습니다. Ablation도 모듈을 하나씩 제거하는 절차에 그치지 않고, 각 실험이 어떤 연구 질문에 답하는지 연결해 보면 결과의 의미가 훨씬 분명해집니다.

- 강한 baseline과 단순 baseline을 모두 비교했나요?
- 각 모듈의 기여를 따로 확인했나요?
- 여러 데이터셋·기간·seed·모델에서도 결과가 안정적인가요?
- 사용한 지표가 실제 주장과 잘 맞나요?

**주장과 필요한 증거를 연결해 보기**

| 주장 | 필요한 증거 |
|---|---|
| 기존 방법보다 우수하다 | 강한 방법과 단순 방법을 포함한 baseline 비교 |
| 특정 모듈이 성능 향상에 기여한다 | 해당 모듈을 분리한 targeted ablation |
| 결과가 안정적이다 | 데이터셋·기간·seed·모델을 바꾼 검증 |
| 실제 활용 가능성이 있다 | 비용·시간·위험·latency를 포함한 평가 |
| 정보를 더 잘 활용한다 | 최종 성능 외에 정보 선택과 reasoning 분석 |

#### 05. Leakage와 평가 편향을 꼼꼼히 살펴보기
*아주 좋은 결과일수록, 먼저 다른 설명이 가능한지 확인해 보면 좋습니다.*

금융 시계열과 LLM 연구에서는 정보의 시점을 세심하게 구분할 필요가 있습니다. 예측일 이후의 정보, 사후 수정된 경제지표, 같은 기업이나 문서의 train-test 중복이 없는지 확인해 보세요.

같은 LLM이 데이터 생성, 검증, reward modeling, 평가를 모두 맡으면 자기강화 편향이 생길 수 있습니다. LLM-as-a-judge를 사용한다면 human evaluation과의 agreement, 여러 judge 사이의 일치도, 통계적 안정성을 함께 제시하는 방식도 고려해 볼 수 있습니다.

#### 06. 예상과 다른 결과에서도 배움 찾기
*Negative result는 가정이 어디까지 유효한지를 보여주는 중요한 단서입니다.*

방법이 더 많은 reasoning signal을 포착했지만 예측 성능은 개선하지 못할 수도 있습니다. 이럴 때는 단순히 실패로 정리하기보다, 정보 검색·해석·최종 의사결정 가운데 어느 단계에서 어려움이 생겼는지를 나누어 살펴보면 새로운 통찰을 얻을 수 있습니다.

근거가 제한적이라면 주장의 범위도 함께 조절하는 편이 좋습니다. 한두 데이터셋의 결과는 보편적 우수성보다 case study나 exploratory finding으로 표현하는 것이 더 정확할 수 있습니다. 범위를 정교하게 설정하는 일은 논문을 약하게 만들기보다 오히려 신뢰를 높여 줍니다.

#### 07. 재현 가능성도 중요한 기여로 생각하기
*'자세한 내용은 GitHub에 있습니다'만으로는 방법 설명을 충분히 대신하기 어렵습니다.*

독자가 논문만 읽고도 핵심 설정을 이해할 수 있도록 돕는 것이 좋습니다. 코드 저장소에서 추가 정보를 제공하더라도, 본문과 appendix에는 재현에 꼭 필요한 구현 정보를 남겨 주세요.

- 정확한 모델 이름과 버전
- 데이터 구성과 전처리
- 학습·평가 prompt와 loss
- Hyperparameter와 baseline 구현
- 실행 시간, 계산 자원, API 비용
- 코드와 데이터의 공개 범위

#### 08. 논문의 핵심을 앞부분에서 보여주기
*독자가 글의 목적을 초반부터 이해할 수 있으면 이후 내용도 훨씬 편하게 따라옵니다.*

Introduction은 중요한 문제와 실패 사례, 기존 접근의 한계, 핵심 아이디어, 해결 방식, 주요 결과의 흐름으로 전개해 볼 수 있습니다. Method 역시 전체 프로세스를 먼저 보여준 뒤 세부 구성요소를 설명하면 독자가 큰 그림을 놓치지 않는 데 도움이 됩니다.

용어와 notation은 처음 등장할 때 자연스럽게 정의하고, 꼭 필요하지 않은 새 이름은 줄이는 편이 좋습니다. 제목과 초록만 읽어도 어떤 연구인지 짐작할 수 있도록 구성해 보세요.

#### 09. 표와 그림만으로도 맥락이 보이게 만들기
*표와 그림은 장식을 넘어, 주장을 가장 빠르게 전달하는 도구가 될 수 있습니다.*

그림 하나에는 가능하면 하나의 핵심 메시지를 담고, 방법론 그림에서는 입력·단계·출력이 분명히 보이도록 구성해 보세요. Caption만 읽어도 실험 설정을 이해할 수 있게 쓰고, 본문에서는 결과가 무엇을 의미하는지 함께 해석하면 좋습니다.

핵심 주장에 꼭 필요하지 않은 결과는 appendix로 옮기는 방법도 있습니다. PPT에서도 표와 그림만 배치하기보다, 각 결과에서 무엇을 읽어야 하는지 한 문장으로 덧붙이면 전달력이 좋아집니다.

#### 10. 피드백과 진행 상황을 구조화하기
*좋은 업데이트는 현재 상황을 공유하는 데서 나아가, 다음 결정을 돕습니다.*

'실험을 더 했습니다'라고만 보고하기보다 이전 문제, 변경 내용, 새 실험, 결과와 해석, 남은 질문, 다음 결정의 순서로 정리해 보세요. 듣는 사람이 연구의 흐름을 빠르게 파악하고 필요한 판단을 내리기 쉬워집니다.

모든 피드백을 한꺼번에 반영할 필요는 없습니다. 제출 전에 꼭 고칠 must fix, 설득력을 크게 높이는 important, 시간이 허용되면 추가할 nice to have로 나누어 우선순위를 정하면 부담을 줄이면서도 중요한 일을 놓치지 않을 수 있습니다.

#### RESEARCH CHECKPOINT: 연구를 진행하면서 함께 생각해 볼 세 가지 질문

복잡한 모델이나 많은 실험만으로 좋은 연구가 완성되지는 않습니다. 중요한 문제, 검증 가능한 주장, 그리고 그 주장에 정확히 대응하는 증거가 서로 잘 맞물릴 때 연구의 설득력이 높아집니다.

1. 우리는 정확히 무엇을 주장하고 있나요?
2. 현재 실험이 그 주장을 실제로 검증하고 있나요?
3. 회의적인 독자도 이 증거를 보고 주장을 납득할 수 있을까요?

---

## 2부. 원문 (English)

**A field guide for student researchers — Strong research begins with a strong question.**

A paper is not a record of how much work you completed. It is an evidence-based argument designed to make an important claim believable.

1. **Define the problem before choosing the method.** *The model is not the starting point. The failure is.* Identify what currently fails, why that failure matters, and what structural limitation prevents existing approaches from addressing it. 'Applying LLMs to finance' or 'using a graph model' does not define a research problem. Begin with a concrete failure or practical constraint. By the end of the first page, readers should understand that the problem genuinely exists and cannot be resolved by simply applying an existing method. (What fails? Why does the failure matter? What structural limitation causes it? What is the precise scope?)
2. **Express the central claim in one sentence.** *When the contribution is unclear, the experiments drift with it.* Explain what changed, which problem the change addresses, and under what conditions it is effective—in one sentence. Then check that every major experiment directly supports that claim. A smaller set of decisive experiments is stronger than many interesting but disconnected results.
3. **Novelty comes from perspective, not component count.** *A useful combination of standard techniques is not automatically a new idea.* Look for a new problem formulation, a phenomenon that could not previously be measured, a domain-driven design, or a new explanation for an existing failure. In financial research, the method or evaluation should reflect transaction costs, risk constraints, non-stationarity, information timing, data revisions, and realistic deployment conditions. Applying generic machine learning to financial data is rarely sufficient.
4. **Use experiments to test claims, not merely performance.** *Write the claim first; design the evidence it requires second.* Include both the simple alternative a reader will immediately consider and the strongest relevant method. Each ablation must answer a specific research question. (Strong and simple baselines? Each component isolated? Stable across datasets, periods, seeds, and models? Metrics match the claim?) Claim→evidence: outperforms → strong+simple baselines; a component causes the improvement → targeted ablation; stable → datasets/periods/seeds/models; practically useful → cost, runtime, risk, latency, deployment; uses information better → information-selection and reasoning analysis beyond final accuracy.
5. **Actively search for leakage and evaluation bias.** *Celebrate unusually strong results only after trying to disprove them.* Separate information by time with exceptional care: post-prediction information, revised economic data, the same entities or documents in training and test sets. If one LLM generates the data, validates it, models rewards, and performs the final evaluation, self-reinforcing bias may arise. For LLM-as-a-judge, report agreement with humans, agreement across judges, and statistical stability.
6. **Unexpected results are still research results.** *A negative result reveals the boundary of an assumption.* Separate failures in retrieval, interpretation, and final decision aggregation. The claim should match the evidence: one or two datasets → case study or exploratory finding. Careful calibration increases credibility.
7. **Treat reproducibility as part of the contribution.** *'See our GitHub' cannot replace a methodological explanation.* Exact model names and versions; dataset construction and preprocessing; training and evaluation prompts and losses; hyperparameters and baseline implementations; availability of code and data.
8. **Readers should not discover a section's purpose only at the end.** Introduction: important problem and concrete failure → limitation of existing approaches → central idea → how it resolves the failure → primary findings. Method: complete process first, then components. Define terms when they first appear; avoid unnecessary names. Title and abstract alone should tell the subject.
9. **Make figures and tables self-contained.** *Visuals are not decoration; they are the fastest form of argument.* One primary message per figure; method diagrams with clear inputs, stages, outputs; captions explain the setting; text interprets the result. Move non-essential results to the appendix.
10. **Structure feedback and research updates.** *A strong update makes the next decision possible.* Previous problem → what changed → new experiment → result and interpretation → unresolved questions → decision required next. Prioritize feedback as must fix / important / nice to have.

**Three questions to keep asking throughout the project:** What exactly are we claiming? Do our experiments genuinely test that claim? Would a skeptical reader believe it based on the current evidence?

---

## 3부. 단계별 적용 체크리스트 (원문 아님, 이 프로젝트의 운용 규칙)

### A. 아이디어 도출·선정 (원칙 1, 2, 3, 6)
- [ ] 아이디어는 기법이 아니라 **구체적 실패**에서 시작한다: 무엇이 실패하는가 / 왜 중요한가 / 기존 접근이 못 푸는 구조적 이유 / 범위.
- [ ] **한 문장 주장**: 무엇을 바꾸었고, 어떤 문제를 해결하며, 어떤 조건에서 효과적인가.
- [ ] 새로움의 종류를 명시한다: 새 문제 정의 / 이전에 측정 못 하던 현상 / 도메인이 요구하는 설계 / 기존 실패의 새 설명. 기법 조합만으로는 새로움이 아니다.
- [ ] 금융이 들어가면 거래비용·위험 제약·비정상성·정보 공개 시점·데이터 수정·실제 운용 조건이 설계나 평가에 어떻게 반영되는지 적는다.
- [ ] 실패했을 때(negative result) 무엇을 배우는지 미리 적는다.

### B. 실험 설계 (원칙 4, 5)
- [ ] 주장 → 필요한 증거 표를 먼저 만든다.
- [ ] 단순 baseline과 가장 강한 baseline을 모두 넣는다.
- [ ] 각 ablation이 답하는 연구 질문을 적는다.
- [ ] 데이터셋·기간·seed·모델을 바꿔 안정성을 확인한다. 지표가 주장과 맞는지 확인한다.
- [ ] Leakage 점검: 예측일 이후 정보, 사후 수정된 데이터, 같은 기업·문서의 train-test 중복, LLM 사전학습 컷오프.
- [ ] 같은 LLM이 생성·검증·보상·평가를 겸하지 않게 한다. LLM-as-a-judge를 쓰면 사람과의 일치도, judge 간 일치도, 통계적 안정성을 보고한다.

### C. 결과 해석 (원칙 6)
- [ ] 결과가 지나치게 좋으면 다른 설명부터 반증한다.
- [ ] 실패는 정보 검색 / 해석 / 최종 의사결정 집계 중 어느 단계인지 나눈다.
- [ ] 증거 범위에 맞게 주장의 범위를 조정한다(1~2개 데이터셋 → case study, exploratory finding).

### D. 재현성·집필 (원칙 7, 8, 9)
- [ ] 정확한 모델 이름·버전, 데이터 구성·전처리, prompt·loss, hyperparameter, baseline 구현, 실행 시간·자원·API 비용, 공개 범위를 본문이나 appendix에 남긴다.
- [ ] Introduction: 문제·실패 사례 → 기존 접근의 한계 → 핵심 아이디어 → 해결 방식 → 주요 결과. Method는 전체 과정부터 보여준다.
- [ ] 용어는 처음 나올 때 정의하고, 불필요한 새 이름은 만들지 않는다.
- [ ] 그림 하나에 메시지 하나. Caption만으로 설정을 이해할 수 있게 쓴다.

### E. 진행 보고 (원칙 10)
- [ ] 보고 순서: 이전 문제 → 변경 내용 → 새 실험 → 결과와 해석 → 남은 질문 → 다음 결정.
- [ ] 피드백은 must fix / important / nice to have로 나눈다.

### F. 매 단계 체크포인트
1. 우리는 정확히 무엇을 주장하고 있는가?
2. 현재 실험이 그 주장을 실제로 검증하고 있는가?
3. 회의적인 독자도 이 증거를 보고 주장을 납득할 수 있는가?
