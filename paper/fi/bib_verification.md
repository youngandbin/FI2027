# refs.bib verification log

- Date: 2026-10-10
- Scope: the 23 Task-A keys inherited from the EAAI submission, plus 20 new entries (Task B and `team2025gemma3`). The other 20 inherited entries (e.g. `hwang2025deep`, `kim2023llms`, `merton1980estimating`, `kong2025fusing`, `openai2024gpt4o`, `yang2024qwen2technicalreport`) were **not** checked and are unchanged.
- Method: each entry was checked against a primary record:
  - Crossref REST API (`api.crossref.org/works/<DOI>` and `query.bibliographic`) for journal, book-chapter, ACL Anthology and ACM entries;
  - arXiv API (`export.arxiv.org/api/query?id_list=`) for preprints;
  - the ICLR proceedings site (`proceedings.iclr.cc`, official BibTeX) and the ICLR 2023 virtual-site poster pages (which link the OpenReview forum IDs);
  - the TMLR paper list and its official BibTeX (`jmlr.org/tmlr`);
  - the Hugging Face model API;
  - the author's own publication page (Politis, UCSD).
  - Where Crossref gives only a first page (JSTOR DOIs), the end page comes from the Semantic Scholar record.
  - SSRN abstract pages return HTTP 403 to scripted access. SSRN metadata comes from the Crossref record of the SSRN DOI, with dates read from the search-engine index of the SSRN page; this is flagged per row.
  - DBLP timed out and OpenReview's API needed a challenge, so neither was used directly.
- Titles follow the publisher's capitalisation. Proper nouns and acronyms are braced ({GPT}, {LLMs}, {Black-Litterman}). Every arXiv preprint gets its DataCite DOI (`10.48550/arXiv.<id>`).
- Original file backed up outside the repo before editing. No entries were removed.

| key | status | source URL or DOI | what changed |
|---|---|---|---|
| best1991sensitivity | corrected | 10.1093/rfs/4.2.315 | Title case and journal name fixed (The Review of Financial Studies); author initials given periods; DOI added. Bibliographic data was already correct. |
| black1992global | corrected | 10.2469/faj.v48.n5.28 | Title and journal capitalisation fixed; DOI added. |
| he2002intuition | corrected | 10.2139/ssrn.334304 | `@article` with fake journal "Available at SSRN 334304" changed to `@misc`, howpublished = SSRN Working Paper No. 334304; DOI added. SSRN lists it as posted 28 Oct 2002, 27 pp. **Cite this key** (see he1999intuition). |
| idzorek2007step | corrected | 10.1016/B978-075068321-0.50003-0 | Title set to the book-chapter title in Crossref ("A Step-by-Step Guide to the Black-Litterman Model"). The subtitle "Incorporating user-specified confidence levels" belongs to the stand-alone working paper, not the chapter. DOI added. Pages 17--38 confirmed. |
| lopez2023can | corrected | 10.1016/j.jfineco.2026.104335 | **Now published**: Journal of Financial Economics 184, 104335 (Oct 2026 issue). Changed from arXiv 2304.07619 to the JFE version: year is now 2026 but the key is unchanged. Earlier versions: SSRN 4412788 / arXiv 2304.07619. Check that the year matches the text if it says "Lopez-Lira and Tang (2023)". |
| kim2023if | corrected | 10.1016/j.frl.2023.104580 | {ChatGPT} braced; DOI added. Volume 58 and article 104580 confirmed. |
| romanko2023chatgpt | corrected | 10.1007/s43069-023-00277-6 | Was `@inproceedings`; Operations Research Forum is a journal, so changed to `@article` (vol 4, no 4, article 91). Title "ChatGPT-Based Investment Portfolio Selection". DOI added. |
| markowitz1952portfolio | corrected | 10.1111/j.1540-6261.1952.tb01525.x | Entry was corrupt (title "Portfolio Selection, the journal of finance. 7 (1)", journal "N", vol 1, pp. 71--91). Now The Journal of Finance 7(1):77--91, 1952, author Harry Markowitz; DOI added. |
| chopra1993effect | corrected | 10.3905/jpm.1993.409440 | Spurious "and others" and wrong publisher (World Scientific) removed; journal is The Journal of Portfolio Management 19(2):6--11; DOI added. |
| ledoit2004well | corrected | 10.1016/S0047-259X(03)00096-4 | Journal capitalisation fixed; DOI added. |
| demiguel2009optimal | corrected | 10.1093/rfs/hhm075 | Title and journal capitalisation fixed ("1/{N}"); DOI added. |
| satchell2007demystification | corrected | 10.1016/B978-075068321-0.50004-2 | Chapter title set to Crossref's ("A demystification of the Black-Litterman model"); DOI added. Note: the chapter reprints Satchell & Scowcroft (2000), *Journal of Asset Management* 1(2):138--150, doi 10.1057/palgrave.jam.2240011. A finance referee may expect the original journal article. |
| drinkall2024time | corrected | 10.18653/v1/2024.findings-naacl.208 | Changed from arXiv preprint to the published version: Findings of ACL: NAACL 2024, pp. 3281--3292; DOI added. |
| dubey2024llama | corrected | arXiv 2407.21783 (v3) / 10.48550/arXiv.2407.21783 | arXiv v3 lists Aaron Grattafiori first (561 authors). Author list now starts with Grattafiori, Dubey, ... "and others", so the in-text citation will read "Grattafiori et al." while the key stays `dubey2024llama`. Title capitalisation fixed; DOI added. |
| team2024gemma | corrected | arXiv 2403.08295 / 10.48550/arXiv.2403.08295 | "Team, Gemma" changed to the corporate author {Gemma Team}; title capitalisation fixed; DOI added. Kept as requested. |
| team2025gemma3 | added-verified | arXiv 2503.19786 / 10.48550/arXiv.2503.19786 | New: "Gemma 3 Technical Report", {Gemma Team} and Kamath, Ferret, Pathak, ... "and others", 2025. |
| kwon2023efficient | corrected | 10.1145/3600006.3613165 | Title capitalisation fixed ({PagedAttention}); publisher ACM and DOI added. SOSP '23, pp. 611--626 confirmed. |
| pastor2000portfolio | corrected | 10.1111/0022-1082.00204 | Author name fixed to P{\'a}stor, {\v{L}}ubo{\v{s}} (was "L'ubo{\v{s}}"); publisher normalised; DOI added. |
| garlappi2007portfolio | corrected | 10.1093/rfs/hhl003 | Title case; DOI added. |
| michaud1989markowitz | corrected | 10.2469/faj.v45.n1.31 | Missing space and stray Unicode quotes in the title fixed ("Is `Optimized' Optimal?"); journal capitalisation fixed; DOI added. |
| jorion1986bayes | corrected | 10.2307/2331042 | Title and journal capitalisation fixed; DOI added. End page 292 is from Semantic Scholar, because Crossref and OpenAlex give only the first page (279). |
| lee2025your | corrected | 10.1145/3768292.3770375 | **Now published**: Proceedings of the 6th ACM International Conference on AI in Finance (ICAIF '25), pp. 150--158. Changed from arXiv 2507.20957 to `@inproceedings`; title capitalisation fixed ({AI}, {LLMs}); DOI added. |
| tetlock2007giving | corrected | 10.1111/j.1540-6261.2007.01232.x | Title and journal capitalisation fixed; DOI added. |
| gentzkow2019text | corrected | 10.1257/jel.20181020 | Publisher street address removed; title case; DOI added. |
| jegadeesh1990evidence | added-verified | 10.1111/j.1540-6261.1990.tb05110.x | J. Finance 45(3):881--898. |
| lehmann1990fads | added-verified | 10.2307/2937816 | QJE 105(1):1--28. End page 28 from Semantic Scholar; Crossref gives the first page only. |
| glasserman2023assessing | added-verified | 10.3905/jfds.2023.1.143 | The journal version exists and is used: The Journal of Financial Data Science 6(1):25--42, 2024 (the DOI string says 2023 but the issue is Winter 2024). Earlier versions: arXiv 2309.17322, SSRN 4586726. |
| sarkar2024lookahead | added-verified | 10.2139/ssrn.4754678 | Canonical version is the SSRN working paper (2024). Not on arXiv (arXiv search by title+author returned nothing). It was also shown as an NBER conference paper and an ICML 2025 workshop poster; no archival proceedings or journal version was found. |
| kadavath2022language | added-verified | arXiv 2207.05221 / 10.48550/arXiv.2207.05221 | All 36 arXiv authors listed. |
| xiong2024can | added-verified | proceedings.iclr.cc (ICLR 2024 official BibTeX) | ICLR 2024, pp. 23650--23678, 7 authors including Bryan Hooi. URL to the proceedings abstract page. |
| lin2022teaching | added-verified | https://openreview.net/forum?id=8s8K2UZGTZ (TMLR listing + official BibTeX) | TMLR 2022, ISSN 2835-8856. |
| kuhn2023semantic | added-verified | https://openreview.net/forum?id=VD-AYtP0dve (ICLR 2023 poster page) | ICLR 2023 (spotlight per the arXiv comment). No page numbers exist (ICLR 2023 has no paginated proceedings). |
| manakul2023selfcheckgpt | added-verified | 10.18653/v1/2023.emnlp-main.557 | EMNLP 2023 main, pp. 9004--9017. |
| wang2023selfconsistency | added-verified | https://openreview.net/forum?id=1PL1NIMMrw (ICLR 2023 poster page) | ICLR 2023; 8 authors from arXiv 2203.11171. |
| gneiting2007strictly | added-verified | 10.1198/016214506000001437 | JASA 102(477):359--378. |
| politis1992circular | added-verified | https://mathweb.ucsd.edu/~politis/DPpublication.html | In LePage & Billard (eds.), *Exploring the Limits of Bootstrap*, John Wiley, New York, 1992, pp. 263--270 (author's own publication list; editors, year and ISBN 0471536318 confirmed in library catalogue). No DOI exists. The publisher's TOC page is partial and does not list the chapter. |
| ledoit2008robust | added-verified | 10.1016/j.jempfin.2008.03.002 | J. Empirical Finance 15(5):850--859. Crossref misspells the first author as "Oliver"; "Olivier" is used. |
| openai2025gptoss | added-verified | arXiv 2508.10925 / 10.48550/arXiv.2508.10925 | Corporate author {OpenAI}; title "gpt-oss-120b \& gpt-oss-20b Model Card". |
| walters2014black | added-verified (year caveat) | 10.2139/ssrn.1314585 | SSRN working paper, Jay Walters; Crossref confirms title, author and DOI. Year 2014 = latest revision ("last revised June 2014"; posted 28 Jan 2009; 65 pp.), taken from the search-engine index of the SSRN abstract page, because SSRN blocks direct fetches (403). Crossref's DOI record shows 2011. Re-check on the SSRN page in a browser before submission. |
| brown1992survivorship | added-verified | 10.1093/rfs/5.4.553 | RFS 5(4):553--580. Goetzmann's given name is entered as "William", as in Crossref. |
| elton1996survivorship | added-verified | 10.1093/rfs/9.4.1097 | RFS 9(4):1097--1120. **The published title is "Survivor Bias and Mutual Fund Performance"**, not "Survivorship bias ..."; the published title is used. |
| he1999intuition | unverified — original Goldman Sachs report not retrievable | (secondary only: cited as "Investment Management Research, Goldman Sachs & Company, 1999" in e.g. https://sites.bu.edu/paschalidis/files/2015/06/Black-Litterman.pdf) | Added as `@techreport` (institution Goldman Sachs, type Investment Management Research, 1999). No month, because citing works disagree or give none, and no primary copy was found. **Recommendation: cite `he2002intuition`** (same paper, SSRN 334304, has a DOI and can be checked by referees). Keep `he1999intuition` only if a sentence needs the 1999 origin date. |
| meta2024llama33 | added-verified | https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct | `@misc`, author {Meta}, year 2024 (HF repo created 2024-11-26, last modified 2024-12-21, per the HF API). The title "Llama 3.3 70B Instruct Model Card" is descriptive, since a model card has no formal title. Accessed 2026-10-10. |

## Counts

- Task A (23 keys): verified unchanged 0, corrected 23, unverified 0. Every key needed at least a DOI or a capitalisation fix. The substantive fixes were markowitz1952portfolio, chopra1993effect, romanko2023chatgpt, he2002intuition, lopez2023can, lee2025your, drinkall2024time, dubey2024llama and pastor2000portfolio.
- Additions (20 keys including team2025gemma3): added-verified 19 (walters2014black with a year caveat), unverified 1 (he1999intuition).

## Points for the authors

1. `lopez2023can` now resolves to JFE 2026, so in-text citations should read "Lopez-Lira and Tang (2026)".
2. `dubey2024llama` will print as "Grattafiori et al. (2024)".
3. `elton1996survivorship` uses the published title "Survivor Bias ...".
4. Cite `he2002intuition` rather than `he1999intuition`.
5. Consider citing the original *Journal of Asset Management* (2000) article for Satchell & Scowcroft instead of the 2007 book reprint.
6. The 20 untouched inherited entries are still unverified. `kong2025fusing` produces a BibTeX warning (empty institution).

## Sanity check (2026-10-10)

`python3 -c` parse of `refs.bib`: entries: 63 | unbalanced braces per entry: none | duplicate keys: none | keys with spaces: none | global brace balance: 0.

Extra check: `bibtex` with `plainnat` and `\citation{*}`, run on a scratch copy outside the repo, produced 63 `\bibitem`s and 1 warning ("empty institution in kong2025fusing", an untouched inherited entry).

## 가이드 점검

1. 한 문장 주장: FI 원고가 인용할 43개 키(기존 23 + 신규 20)는 1차 출처(Crossref/arXiv/ICLR·TMLR 공식 BibTeX/HF/저자 페이지)와 대조했으며, 확인 못 한 1건(he1999intuition)과 연도만 2차 확인인 1건(walters2014black)을 명시했다.
2. 관련 원칙: 재현성(출처 URL·DOI를 표에 기록) — 충족. 평가 편향·leakage 점검(look-ahead 문헌 glasserman/sarkar/drinkall을 정식 판본으로 확보) — 충족. 핵심을 앞에(저자가 알아야 할 변경 6가지를 별도 절로) — 충족.
3. 세 질문: 무엇을 주장하는가 — 각 항목의 서지 정보가 1차 출처와 일치한다. 검증하는가 — 키별 출처를 표에 남겼고 파싱·bibtex 검사를 통과했다. 회의적 독자가 납득하는가 — 대체로 그렇다. 남은 것: he1999 원문 미확보(important), Walters 개정 연도 브라우저 재확인(nice to have), 손대지 않은 기존 20개 항목 미검증(important, 원고에서 인용하면 must fix).
