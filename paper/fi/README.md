# FI paper draft (Financial Innovation, Springer)

Draft of the re-examination paper. Built with the standard `article` class so it compiles here; port to the
Springer Nature LaTeX template (`sn-jnl`, author-year `sn-basic` style) before submission.

- `./build.sh` builds `main.pdf` (logs in `build/`) and counts open `\todo{}` / `\pending{}` markers.
- `./overleaf_sync.sh pack` makes `build/overleaf_upload.zip`; `unpack <zip>` imports an Overleaf download for diffing.
- Tables and figures are generated, not hand-edited: `cd ../../src && python 92_paper_assets.py --market US --tag gptoss20b_A`
  writes `tables/*.tex`, `figures/*.pdf` and `tables/facts.json` (numbers quoted in the text).
- `bib_verification.md`: source check of every bibliography entry (2026-10-10). Cite `he2002intuition`, not `he1999intuition`.

## Status (2026-10-10)
- Written: all sections for the US pilot (S&P 500, gpt-oss-20b, prompt A, N=20, 2025).
- `\pending{}` (blue): results not yet run — KR/JP/DE, gpt-oss-120b, Gemma 3 27B, Llama 3.3 70B, prompt B, temperature.
- `\todo{}` (red): author list and declarations, model-cutoff appendix table, stage-0 re-run on the earlier data,
  fixed-universe and fixed-split robustness, reference to the unpublished EAAI 2026 version, AI-use wording.

## Before submission
- Check the journal's current submission guidelines (abstract length, declarations, AI policy, APC); the
  guideline pages were not readable from this environment.
- Every number in the text must match `tables/facts.json` or a generated table after the final run.
- Shuffled Omega is one random permutation (seed 0); report the mean over several seeds.
- Check claims attributed to Satchell & Scowcroft and Walters (tau/Omega identification) against the sources.
