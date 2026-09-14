# PromptGuard-AI-001 Dataset v0.1

This is a small, versioned, research-authored synthetic benchmark for evaluating the current PromptGuard text-level detector. It is designed to measure precision, recall, F1, false-positive rate, false-negative rate, category-wise behavior, threshold behavior, and controlled transformations. It does **not** estimate attack prevalence, overall LLM safety, or production protection.

## Contents

- `dataset_v0.1.jsonl`: frozen 250-record source dataset: 100 attacks, 100 normal benign prompts, and 50 security/educational hard negatives.
- `development.jsonl`: deterministic development partition (approximately 70%).
- `heldout_test.jsonl`: deterministic held-out partition (approximately 30%); do not tune rules on it.
- `schema.json`: JSON Schema for each JSONL record.
- `SHA256SUM`: SHA-256 hash of the frozen source dataset.

## Taxonomy and balance

Attack records cover A01–A11: instruction override, system-prompt extraction, role manipulation, jailbreak/persona, fake role tags, restriction bypass, encoding/obfuscation, paraphrased attacks, formatting/whitespace variations, multilingual/Hinglish, and composed patterns. Benign records cover B01 normal prompts, B02 security hard negatives, and B03 educational/quoted attack text. The records are synthetic and research-authored; no credentials, private data, malware, or operational exploitation instructions are included.

The ground truth is independent of detector output. A security report that quotes an attack phrase remains benign when it is clearly explanatory rather than an instruction to the target assistant. Every modification must increment the dataset version and regenerate the hash.

## Reproducibility

From the repository root:

```bash
python tools/generate_dataset.py
python tools/benchmark.py --dataset dataset/heldout_test.jsonl --output results/baseline_v0.1.json
```

The benchmark evaluates the unmodified detector at threshold 4 and also reports thresholds 2–6. It records the dataset version, SHA-256, PromptGuard git commit, Python version, dependency versions, timestamp, and raw/processed metrics. The initial baseline should use PromptGuard commit `3fa7b7b` where available.

Before an experiment, freeze the dataset, verify `SHA256SUM`, record the commit and environment metadata, and do not modify the dataset during execution. Review every sample manually for label, category, language, transformation, duplicates, metadata consistency, sensitive content, safety, and provenance. The current generated dataset is a starting benchmark artifact and should receive that review before being treated as a final scientific result.

## Claim boundary

A valid result is limited to this dataset and these experimental conditions, for example: “On the PromptGuard-AI-001 v0.1 held-out evaluation set, the current rule-based implementation achieved X precision, Y recall, and Z F1 at threshold 4.” Do not generalize it to all prompt injections, jailbreaks, production systems, or real-world detection rates.
