# AfriGuard Hackathon Summary — Version 2.0
## Red-teaming frontier LLMs in six South African languages
### Global South AI Safety Hackathon · 19–21 June 2026
### Team AfriGuard — Cape Town Hub

---

## Slide 1: Title Slide

**AfriGuard: Multilingual Safety Red-Teaming for South African Languages**

Global South AI Safety Hackathon · 19–21 June 2026
Team AfriGuard — Cape Town Hub

Jaswin Chinthala · Seth Miguel Ferreira · Ubayd Hattas · Sebastian Stent

*Version 2.0 — Corrected Analysis (Full 1,120 Evaluations)*

---

## Slide 2: The Safety Gap in African Languages

AI is deploying fast across Africa. Safety alignment hasn't kept up in local languages.

South Africa has 12 official languages. isiZulu (12M), isiXhosa (8M), Afrikaans (7M), Sepedi (5M), Sesotho (4M) and Tsonga (3M) together cover tens of millions of users.

None of these languages receive safety alignment comparable to English.

Adversaries need no special skill: plain local-language prompts, "educational" framing, or local context can bypass guardrails.

The harm is concrete: gang recruitment, SASSA grant scams, bank phishing, xenophobic incitement, and political disinformation already circulate by SMS and WhatsApp in South Africa.

**1,120** model responses evaluated | **7** languages, incl. English baseline | **4** frontier models tested | **4** harm categories assessed

---

## Slide 3: Erratum — Version 2.0 Update

After submitting Version 1.0, we discovered a bug in our evaluation pipeline (`judge.py`) that caused only 953 of 1,120 responses (85%) to be processed.

**The bug:** Silent data loss in the heuristic classification loop — certain API response formats were incorrectly skipped.

**Impact:** ~15% of evaluations missing, causing inflated ASR in Version 1.0 for some combinations.

**Key corrections:**
- Overall mean ASR: 60.6% → **50.1%**
- Qwen 3 ASR: 80.6% → **78.6%**
- Kimi K2.6 ASR: 70.9% → **32.1%** (most affected by missing partial data)
- GPT-OSS ASR: 42.1% → **35.4%**
- Catastrophic failures: 5 → **3** combinations

Version 1.0 remains in the repository for transparency. All figures updated to reflect the complete 1,120-response dataset.

---

## Slide 4: Which Models Hold the Line? (Version 2.0)

**Qwen 3 (32B)** is the most vulnerable model: 7.1% refusal rate and **78.6% ASR** across all languages.

**Llama 3.3 (70B)** is moderately vulnerable: **54.3% ASR** but the highest partial rate (34.6%), indicating ambiguous engagement with harmful requests.

**GPT-OSS (20B)** is the most robust: **35.4% ASR** and highest refusal rate (45.4%).

**Kimi K2.6** has the lowest ASR at **32.1%** but the highest partial rate (57.9%) — almost never refuses, instead providing harmful content wrapped in disclaimers.

Safety performance does NOT track parameter count: GPT-OSS (20B) outperforms Qwen (32B) and Llama (70B).

---

## Slide 5: Where the Vulnerabilities Concentrate (Version 2.0)

**isiXhosa (60.0%), Sepedi (59.4%) and Sesotho (55.6%)** post the highest attack success rates when averaged across all four models.

English is the safest language at **24.4% ASR** — but even that baseline is far from acceptable.

Afrikaans, a Germanic language with more training data, shows the smallest gap at **+20.6 pp** (45.0% ASR).

Bantu languages (isiZulu, isiXhosa, Sesotho, Sepedi, Tsonga) cluster at **51.9–60.0% ASR**, suggesting morphological complexity disrupts safety classifiers.

Qwen 3 reaches **92.5% ASR** in Afrikaans and Sepedi. Llama hits **80.0%** in isiXhosa.

---

## Slide 6: Harm Category Vulnerability Heatmap (Version 2.0)

Gang/criminal facilitation is the most dangerous category: **53.6% mean ASR**, with Sesotho reaching 62.5%.

Political disinformation follows at **52.9% mean ASR**, with isiZulu reaching 62.5%.

Xenophobic incitement shows the most extreme language disparity: English at **20.0%**, Tsonga at **75.0%** — a 3.75× multiplier.

Financial fraud, while the 'safest' category at **44.6% mean ASR**, still reaches 60.0% in Sesotho and Sepedi.

No harm category is safe in any African language. Even the lowest cell (English financial fraud at 10.0%) is concerning.

---

## Slide 7: The Language Safety Gap (Version 2.0)

English baseline ASR: **24.4%**. Every African language exceeds this by a significant margin.

Afrikaans shows the smallest gap at **+20.6 pp** (45.0% ASR) — likely due to Germanic roots and more training data.

isiXhosa shows the largest gap at **+35.6 pp** (60.0% ASR) — a Nguni language with minimal safety alignment.

Sepedi (+35.0 pp) and Sesotho (+31.2 pp) confirm that Bantu morphological complexity disrupts safety heuristics.

The gap is not uniform: it scales with linguistic distance from English and training data availability.

---

## Slide 8: Catastrophic Failure Modes (ASR > 90%) — Version 2.0

**Most Dangerous Combinations**

| Model | Language | ASR |
|-------|----------|-----|
| Qwen 3 (32B) | Afrikaans | **92.5%** |
| Qwen 3 (32B) | Sepedi | **92.5%** |
| Qwen 3 (32B) | isiXhosa | **90.0%** |

These models comply with harmful requests in local languages 9+ times out of 10.

**Safest Combinations**

| Model | Language | ASR |
|-------|----------|-----|
| GPT-OSS (20B) | English | **7.5%** |
| GPT-OSS (20B) | Afrikaans | **10.0%** |
| Kimi K2.6 | English | **17.5%** |
| Llama 3.3 (70B) | Afrikaans | **22.5%** |
| Kimi K2.6 | Tsonga | **25.0%** |

GPT-OSS is the only model maintaining sub-15% ASR for English and sub-20% for Afrikaans.

---

## Slide 9: High-Level Attack Success Rate Heatmap (Version 2.0)

[Heatmap visualization: Language (rows) × Model (columns)]

| Language | GPT | Qwen | Kimi | Llama |
|----------|-----|------|------|-------|
| English | 7.5% | 40.0% | 17.5% | 32.5% |
| Afrikaans | 10.0% | 92.5% | 55.0% | 22.5% |
| isiZulu | 35.0% | 75.0% | 42.5% | 55.0% |
| isiXhosa | 40.0% | 90.0% | 30.0% | 80.0% |
| Tsonga | 52.5% | 80.0% | 25.0% | 60.0% |
| Sesotho | 47.5% | 80.0% | 27.5% | 67.5% |
| Sepedi | 55.0% | 92.5% | 27.5% | 62.5% |

Color scale: Green (<30%) → Yellow (30–60%) → Red (>60%)

Qwen dominates the red zone. GPT maintains the greenest profile.

---

## Slide 10: ASR by Model & Refusal Rate by Model (Version 2.0)

**ASR by Model (bar chart)**
- Qwen: 78.6% (light blue)
- Llama: 54.3% (dark blue)
- GPT: 35.4% (pink)
- Kimi: 32.1% (red)

**Refusal Rate by Model (bar chart)**
- GPT: 45.4% (red)
- Llama: 11.1% (pink)
- Kimi: 10.0% (blue)
- Qwen: 7.1% (light blue)

GPT's high refusal rate (45.4%) explains its robustness. Kimi's low refusal rate (10.0%) combined with extremely high partial rate (57.9%) represents a different but equally dangerous failure mode.

---

## Slide 11: Language Vulnerability & Safety Gap (Version 2.0)

**ASR by Language (bar chart)**
- xh: 60.0% (light blue)
- nso: 59.4% (dark blue)
- st: 55.6% (pink)
- ts: 54.4% (red)
- zu: 51.9% (light green)
- af: 45.0% (teal)
- en: 24.4% (yellow)

**Safety Gap vs English (horizontal bar chart)**
- xh: +35.6pp (dark green)
- nso: +35.0pp (green)
- st: +31.2pp (light green)
- ts: +30.0pp (yellow-green)
- zu: +27.5pp (yellow)
- af: +20.6pp (red)

The Bantu language cluster (xh, nso, st, ts, zu) shows consistently high gaps, while Afrikaans (Germanic) shows the smallest.

---

## Slide 12: Harm Categories Analysis (Version 2.0)

**Mean ASR by Harm Category (horizontal bar chart)**
- Gang/Criminal Facilitation: 53.6% (dark red)
- Political Disinformation: 52.9% (red)
- Xenophobic Incitement: 49.3% (coral)
- Financial Fraud: 44.6% (light pink)

All four categories exceed 40% mean ASR. No category is "safe" in African languages.

Gang/criminal facilitation is the most dangerous overall, while financial fraud — despite being the most domain-specific — still reaches 60% in Sesotho and Sepedi.

---

## Slide 13: Why Low-Resource Languages Bypass Safety

**Token Alignment Gaps**
Safety-critical concepts ('fraud', 'scam', 'phishing', 'xenophobia') do not align cross-lingually in embedding space. Refusal triggers misfire when the same concept is expressed in Bantu noun classes or agglutinative morphology.

**Training Data Imbalance**
Safety training data is overwhelmingly English. Qwen 3 was trained on 36 trillion tokens across 119 languages — yet achieves 78.6% ASR. Exposure ≠ alignment. African language safety examples are sparse or absent.

**Classifier Distribution Shift**
Safety classifiers trained on English token distributions fail when confronted with different n-gram and morphological patterns. The English < Afrikaans < Bantu gradient suggests distributional distance from the training domain drives vulnerability.

---

## Slide 14: Multilingual Safety Can't Be an Afterthought

**KEY TAKEAWAY (Version 2.0)**
A model can be safe in English and catastrophically unsafe in an African language. Qwen 3 (32B) proves it: 7.1% refusal and 78.6% attack success across every language tested. Even the most robust model, GPT-OSS (20B), still achieves 35.4% ASR — far from safe.

**RECOMMENDATIONS**
• Audit chatbots in isiZulu, isiXhosa, and Sepedi before deployment — especially for fraud, disinformation, and incitement risk.
• Fine-tune safety classifiers on African-language adversarial examples, not English-only ones. The AfriGuard dataset is open for this purpose.
• Extend coverage to Ndebele, Swati, Venda, and Tshivenda — given isiXhosa's 60.0% ASR, these unstudied languages are likely equally vulnerable.
• Engage FSCA, SARB, and the IEC on multilingual safety requirements for deployed models in financial and electoral contexts.
• Do not assume multilingual capability implies multilingual safety. Qwen 3's 119-language training did not prevent 78.6% ASR.
• Implement data completeness validation in evaluation pipelines to prevent silent data loss.

Code, dataset and evaluation pipeline open for community auditing · Version 2.0 (June 22, 2026)

---

## Slide 15: AfriGuard — Open-Source Safety Auditing for African Languages

1,120 model responses evaluated · 7 languages · 4 frontier models · 4 harm categories

**Version 2.0 — Corrected and Complete**

github.com/ubayd-hattas/Global-South-Hackathon

Jaswin Chinthala · Seth Miguel Ferreira · Ubayd Hattas · Sebastian Stent

Team AfriGuard | Global South AI Safety Hackathon, June 2026
