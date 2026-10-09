# Paper: EAAI 2026 원고 (보관용)

Overleaf 프로젝트 `FRL-LLM`(https://www.overleaf.com/project/697c58bb4645367342aa721d)을 2026-10-09에 Source zip으로 받아 옮긴 것. 참고용으로만 두고 수정하지 않는다. IJCAI 2027 원고는 `../paper`에서 작업한다.

```bash
cd paper_eaai2026
latexmk          # build/main.pdf (24쪽)
```

- `main.tex`: Overleaf의 `elsarticle-template-num.tex`(실제 원고)를 이름만 바꾼 것.
- `elsarticle.cls`: Overleaf export에 들어 있던 Elsevier 번들(`elsarticle.dtx`)에서 생성. 번들의 문서·예제 템플릿은 원고와 무관해 옮기지 않았다.
- `section/7_Appendix.tex`, `tables/`, `figure/table*.tex` 일부는 Overleaf에서도 `main.tex`에 포함되지 않은 파일이다.
