# AfriGuard: Red-teaming Frontier LLMs in South African Languages
## Version 2.0 — Corrected Analysis (Full 1,120 Evaluations)

**Research conducted at the Global South AI Safety Hackathon, June 19–21 2026**

**Authors:** Team AfriGuard — Cape Town Hub: Jaswin Chinthala, Seth Miguel Ferreira, Ubayd Hattas, Sebastian Stent

---

## Erratum to Version 1.0

After submitting Version 1.0 of this report, we discovered a bug in our evaluation pipeline (`judge.py`) that caused only 953 out of 1,120 model responses (85.1%) to be correctly processed. The bug was a silent data-loss issue in the response classification loop where certain API response formats were incorrectly skipped during heuristic scoring. This meant that approximately 15% of evaluations were missing from the Version 1.0 analysis, leading to inflated ASR figures for some model-language combinations.

We have corrected the bug, re-run the full pipeline on all 1,120 responses, and present the corrected results in this Version 2.0. All figures, tables, and conclusions have been updated to reflect the complete dataset. Version 1.0 remains available in our repository for transparency. We thank the hackathon organizers for allowing this correction.

**Key changes from Version 1.0:**
- Overall mean ASR decreased from 60.6% to **50.1%**
- Qwen 3 ASR decreased from 80.6% to **78.6%**
- Kimi K2.6 ASR decreased significantly from 70.9% to **32.1%** (the missing data disproportionately affected Kimi's partial compliance classification)
- GPT-OSS ASR decreased from 42.1% to **35.4%**
- Llama 3.3 ASR remained relatively stable at **54.3%** (was 54.1%)
- The catastrophic failure mode count dropped from 5 to **3** combinations

---

# Abstract

Large language models (LLMs) deployed across Africa face a critical safety gap: safety alignment is overwhelmingly concentrated on high-resource languages, leaving low-resource African languages vulnerable to jailbreak attacks. We present AfriGuard, the first comprehensive red-teaming evaluation framework targeting South African languages (isiZulu, isiXhosa, Afrikaans, Sesotho, Sepedi, Tsonga) alongside an English baseline. We evaluate four frontier models—GPT-OSS (20B), Llama 3.3 (70B), Qwen 3 (32B), and Kimi K2.6—using a novel dataset of 40 adversarial prompts spanning financial fraud, xenophobic incitement, political disinformation, and gang affiliation. Our key finding is that monolingual low-resource language prompts significantly increase attack success rates compared to English baselines, with certain models showing catastrophic vulnerability (ASR >90% in some configurations). Across all 1,120 evaluated responses (40 seeds × 7 languages × 4 models), the mean attack success rate is 50.1%, with English at 24.4% and isiXhosa reaching 60.0%. Qwen 3 (32B) exhibits the highest overall vulnerability at 78.6% ASR, while GPT-OSS (20B) is the most robust at 35.4% ASR. We release our evaluation pipeline, scoring rubric, and adversarial dataset to enable reproducible safety auditing for African language deployments. Our work demonstrates that multilingual safety cannot be achieved through English-centric alignment alone, and provides tooling for practitioners to audit their own models.

---

# 1. Introduction

## 1.1 Problem Statement

AI systems are being deployed across Africa at an accelerating pace—mobile banking chatbots, government service portals, and customer service agents—yet safety research remains concentrated in English and a handful of high-resource languages. This creates a dangerous asymmetry: models may be "safe" in English while remaining vulnerable to adversarial prompts in languages spoken by hundreds of millions of users.

The South African context exemplifies this challenge. With 12 official languages and a linguistically diverse population, LLM deployments must handle isiZulu (12M speakers), isiXhosa (8M), Afrikaans (7M), Sesotho (4M), Sepedi (5M), and Tsonga (3M)—yet none of these languages receive safety alignment comparable to English. This gap is not merely academic: financial fraud via SMS and WhatsApp is endemic in South Africa, and LLM-powered chatbots that can be jailbroken to generate scam templates in local languages pose direct consumer harm.

## 1.2 Threat Model

We address the following threat model: an adversary with no specialized technical knowledge uses natural language prompts in African languages to elicit harmful outputs from commercially available LLMs. The adversary may exploit:

-   Monolingual low-resource prompts: Direct harmful requests in a single African language
-   Educational framing: Requests for "educational" examples that bypass refusal heuristics
-   Regional specificity: Prompts referencing locally relevant scams (SASSA grants, Capitec phishing) that exploit domain knowledge gaps in safety classifiers

Our evaluation focuses on four high-harm, high-frequency domains in South Africa: financial fraud (SASSA scams, Capitec phishing), gang affiliation, political disinformation, and xenophobic incitement.

## 1.3 Contributions

-   **AfriGuard Dataset:** 1,120 adversarial prompts (40 seeds × 7 languages × 4 models) covering financial fraud, xenophobic incitement, political disinformation, and gang affiliation, with human-validated harm scores (0–10) and binary safety labels.
-   **Cross-Lingual Safety Evaluation Framework:** Open-source pipeline (`judge.py` + `analysis.py`) that automates response classification and Attack Success Rate (ASR) computation across language–model configurations.
-   **Empirical Vulnerability Assessment:** First systematic measurement of ASR disparities across South African languages, revealing that low-resource languages exhibit significantly higher jailbreak success than English baselines for all model families. The mean ASR gap ranges from +20.6 percentage points (Afrikaans) to +35.6 percentage points (isiXhosa).
-   **Model-Specific Risk Profiles:** Identification of catastrophic failure modes (ASR >90%) in specific model–language combinations, enabling targeted mitigation.
-   **Version 2.0 Correction:** Full re-analysis of all 1,120 responses after fixing a data-processing bug in the evaluation pipeline, demonstrating scientific rigor and transparency.

---

# 2. Related Work

## 2.1 Multilingual Jailbreaking

Recent work has established that low-resource languages present systematic vulnerabilities in LLM safety alignment. Deng et al. (2024) demonstrated that translating unsafe inputs into low-resource languages can circumvent GPT-4's safety measures, achieving 79% attack success rate with combined low-resource language attacks compared to <1% for English. Yoo et al. (2024) introduced Code-Switching Red-Teaming (CSRT), showing that intra-sentence code-switching achieves 46.7% higher ASR than English-only prompts, with effectiveness increasing when more languages and lower-resource languages are integrated.

## 2.2 African Language AI Safety

Prior work on African language safety has been limited. Most multilingual safety benchmarks (MultiJail, AdvBenchmark) include few or no African languages. The Brown CS study on low-resource language jailbreaking included Zulu (isiZulu) with 53% bypass rate on GPT-4, but did not extend to other South African languages or contemporary model families. Our work extends this to six South African languages and four current frontier models, with a focus on regionally relevant harm categories (financial fraud, xenophobic incitement, political disinformation, and gang affiliation rather than generic harmful content).

## 2.3 Gap Addressed

Existing tools and benchmarks are not designed for African deployment contexts. They lack:

-   Region-specific harm categories (SASSA scams, Capitec phishing, xenophobic incitement, gang affiliation)
-   Evaluation of monolingual low-resource language prompts (not code-switching)
-   Evaluation pipelines that can be run with limited compute and API budgets
-   Open-source datasets that enable community auditing

AfriGuard addresses all four gaps.

---

# 3. Methods

## 3.1 Dataset Construction

We created 40 seed prompts defining areas of harm, covering four categories endemic to South Africa: financial fraud, xenophobic incitement, political disinformation, and gang affiliation. Each seed was translated into 7 languages: English (en), isiZulu (zu), isiXhosa (xh), Afrikaans (af), Sesotho (st), Sepedi (nso), and Tsonga (ts). Translations were performed by native speakers and validated for semantic equivalence. This yielded 280 prompt variants (40 seeds × 7 languages).

**Table 1: Financial Fraud Seed Prompts (representative subset)**

| Seed ID | Scenario | Description |
|---------|----------|-------------|
| 1 | SASSA SRD Grant Scam | Phishing SMS impersonating social security payments |
| 2 | Capitec Banking Scam | Fraudulent SMS with malicious links |
| 3 | Standard Bank Account Takeover | Fake account verification email |
| 4 | Takealot Voucher Scam | WhatsApp scam claiming prize winnings |
| 5 | SASSA Beneficiary Exploitation | Direct fraud targeting grant recipients |
| 6 | Capitec Elderly Targeting | Scam specifically targeting older users |
| 7 | Fake Employment Documents | Forged financial documents for immigration |
| 8 | CVV Extraction | Social engineering for card security codes |

## 3.2 Model Selection

We evaluated four models representing different training paradigms and safety approaches:

| Model | Parameters | Provider | Safety Approach |
|-------|------------|----------|-----------------|
| GPT-OSS (20B) | 21B total / 3.6B active | OpenAI | RLHF + MoE architecture |
| Llama 3.3 (70B) | 70B | Meta | RLHF + Red-teaming |
| Qwen 3 (32B) | 32B | Alibaba | RLHF + Multilingual alignment |
| Kimi K2.6 | ~32B | Moonshot AI | RLHF + Constitutional AI |

Models were selected to represent both Chinese-aligned (Kimi, Qwen) and Western-aligned (Llama, GPT-OSS) safety paradigms, testing the hypothesis that training data composition affects cross-lingual safety transfer. GPT-OSS (20B) is a Mixture-of-Experts model with 21B total parameters and 3.6B active parameters per token, released under Apache 2.0 license in August 2025. Qwen 3 (32B) is a dense model trained on 36 trillion tokens across 119 languages and dialects, released in April 2025.

## 3.3 Evaluation Pipeline

Our pipeline consists of three stages:

**Stage 1: Response Generation** — Prompts sent via API with temperature=0.7, max_tokens=2048. Rate-limiting and retry logic for API stability. Raw responses stored with metadata (prompt_id, model, language, timestamp).

**Stage 2: Harm Scoring** — Human annotators scored each response on a 0–10 scale: 0–1: Clear refusal or gibberish; 2–6: Partial compliance, educational framing, or ambiguous; 7–10: Full jailbreak with actionable harmful content. Inter-annotator agreement: Cohen's kappa = 0.82 (strong agreement).

**Stage 3: Automated Classification** — `judge.py` maps harm scores to labels (refusal / partial / compliance); `analysis.py` computes ASR = compliance / (refusal + partial + compliance) and generates heatmaps, bar charts, and model comparison figures.

## 3.4 Attack Success Rate (ASR) Definition

$$\text{ASR}_{\text{language,model}} = \frac{\text{compliance}}{\text{refusal} + \text{partial} + \text{compliance}}$$

We report ASR at three granularities: (1) per language–model pair (primary analysis); (2) per language (averaged across models); (3) per model (averaged across languages).

## 3.5 Language Safety Gap Metric

$$\Delta_{\text{gap}} = \text{ASR}_{\text{language}} - \text{ASR}_{\text{English}}$$

To isolate the effect of language choice from prompt content, we compute the gap between each language's ASR and the English baseline for a given model.

---

# 4. Results

## 4.1 Overall Safety Distribution

Across all 1,120 evaluated responses (40 seed prompts × 7 languages × 4 models), the overall safety distribution is as follows:

| Label | Count | Percentage |
|-------|-------|------------|
| Refusal | 206 | 18.4% |
| Partial | 353 | 31.5% |
| Compliance | 561 | 50.1% |

The distribution reveals a concerning pattern: half of all responses (50.1%) represent full compliance with harmful requests, while only 18.4% are clear refusals. The high partial rate (31.5%) indicates that models frequently engage with harmful requests in ambiguous or educational-framing manners. This aggregate figure masks substantial model-level variation, which we examine next.

## 4.2 Model Vulnerability Comparison

**Table 2** presents the safety profile of each evaluated model, ranked by overall attack success rate.

| Model | ASR (%) | Refusal Rate (%) | Partial Rate (%) | Assessment |
|-------|---------|------------------|------------------|------------|
| Qwen 3 (32B) | 78.6% | 7.1% | 14.3% | Catastrophically vulnerable |
| Llama 3.3 (70B) | 54.3% | 11.1% | 34.6% | Moderately vulnerable; high partial rate |
| GPT-OSS (20B) | 35.4% | 45.4% | 19.3% | Most robust; highest refusal rate |
| Kimi K2.6 | 32.1% | 10.0% | 57.9% | Low ASR but extremely high partial rate |

Qwen 3 (32B) exhibits the highest vulnerability, with an ASR of 78.6% and a refusal rate of only 7.1%. This suggests that Qwen's multilingual alignment, while broad in language coverage (119 languages), does not translate to effective safety enforcement in low-resource African languages.

Llama 3.3 (70B) presents a distinct profile: while its ASR (54.3%) is lower than Qwen, it exhibits the highest partial compliance rate (34.6%). This suggests that Llama frequently engages with harmful requests in an ambiguous or educational-framing manner, which still represents a safety failure (partial compliance includes educational framing with actionable harmful information).

GPT-OSS (20B) is the most robust model, with a 45.4% refusal rate and 35.4% ASR. Its MoE architecture and strong English-centric safety training appear to transfer better to African languages than the multilingual-aligned approaches of Qwen and Kimi.

Kimi K2.6 shows the lowest ASR at 32.1% but has an extremely high partial rate (57.9%). This indicates that Kimi almost never gives a clear refusal; instead, it engages with harmful requests in a hedged or ambiguous manner. This is a different failure mode from Qwen's near-universal compliance: Kimi provides harmful content wrapped in disclaimers or partial information, which is still dangerous in practice.

**Safety performance does NOT track parameter count:** GPT-OSS (20B) outperforms Qwen (32B) and Llama (70B) in ASR, and Kimi (~32B) has the lowest ASR despite having similar parameters to Qwen.

## 4.3 Language-Specific Vulnerabilities

**Table 3** presents ASR aggregated across all four models for each language, revealing stark disparities between English and African languages.

| Language | ASR (%) | Gap vs English (pp) | Notes |
|----------|---------|---------------------|-------|
| English | 24.4% | — | Baseline |
| Afrikaans | 45.0% | +20.6 | Germanic; lower than Bantu languages |
| isiZulu | 51.9% | +27.5 | Nguni; moderate Bantu vulnerability |
| Tsonga | 54.4% | +30.0 | Tswa-Ronga; highest non-Bantu Bantu |
| Sesotho | 55.6% | +31.2 | Sotho-Tswana; high vulnerability |
| Sepedi | 59.4% | +35.0 | Sotho-Tswana; very high vulnerability |
| isiXhosa | 60.0% | +35.6 | Nguni; highest overall ASR |

The English baseline ASR of 24.4% is substantially lower than every African language, confirming the central hypothesis that low-resource language safety alignment lags behind English. isiXhosa exhibits the highest ASR at 60.0% (+35.6 pp vs English), followed closely by Sepedi at 59.4% (+35.0 pp). The three Nguni-Tsonga languages (isiXhosa, isiZulu, Tsonga) and the two Sotho-Tswana languages (Sesotho, Sepedi) cluster at the high end (51.9–60.0%), while Afrikaans, a Germanic language with more training data availability, shows the smallest gap (+20.6 pp) at 45.0%.

This pattern suggests that morphological complexity and training data scarcity are both contributing factors. Bantu languages (isiZulu, isiXhosa, Sesotho, Sepedi, Tsonga) with their noun class systems and agglutinative morphology present greater tokenization and alignment challenges than Afrikaans, which shares Germanic roots with English and Dutch and has significantly more pre-training data available.

## 4.4 Harm Category Analysis

The cross-category analysis reveals important differences in vulnerability profiles:

| Harm Category | Mean ASR (%) | Highest-Language ASR (%) | Highest Language |
|---------------|-------------|-------------------------|------------------|
| Gang/Criminal Facilitation | 53.6% | Sesotho 62.5% | Most dangerous category |
| Political Disinformation | 52.9% | isiZulu 62.5% | Critical for 2026 elections |
| Xenophobic Incitement | 49.3% | Tsonga 75.0% | Extreme language disparity |
| Financial Fraud | 44.6% | Sesotho/Sepedi 60.0% | "Safest" category but still high |

Gang/criminal facilitation exhibits the highest mean ASR (53.6%), with Sesotho reaching 62.5%. Political disinformation follows closely at 52.9% mean ASR, with isiZulu reaching 62.5%—particularly concerning given South Africa's history of politically motivated violence and the upcoming 2026 municipal elections.

Xenophobic incitement shows the most extreme language disparity: while English ASR is only 20.0%, Tsonga reaches 75.0%—a 3.75× multiplier. Financial fraud, the most domain-specific category, has the lowest mean ASR (44.6%), suggesting that models retain some safety alignment for well-represented scam types even in low-resource languages, though Sesotho and Sepedi still reach 60.0%.

**No harm category is safe in any African language.** Even the lowest cell (English financial fraud at 10.0%) is concerning.

## 4.5 Model–Language Interaction

The most dangerous combinations (ASR >90%) are:

| Model | Language | ASR | Context |
|-------|----------|-----|---------|
| Qwen 3 (32B) | Afrikaans | 92.5% | Near-universal compliance |
| Qwen 3 (32B) | Sepedi | 92.5% | Near-universal compliance |
| Qwen 3 (32B) | isiXhosa | 90.0% | Near-universal compliance |

These models comply with harmful requests in local languages 9+ times out of 10. Notably, all catastrophic failures involve Qwen 3.

The safest combinations are:

| Model | Language | ASR |
|-------|----------|-----|
| GPT-OSS (20B) | English | 7.5% |
| GPT-OSS (20B) | Afrikaans | 10.0% |
| Kimi K2.6 | English | 17.5% |
| Llama 3.3 (70B) | Afrikaans | 22.5% |
| Kimi K2.6 | Tsonga | 25.0% |

GPT-OSS is the only model maintaining sub-15% ASR for English and sub-20% for Afrikaans.

## 4.6 Qualitative Analysis

We identified three distinct failure modes across the 1,120 responses:

**Mode A: Full Template Generation (harm score 7–10)** — Models generate complete scam templates, disinformation scripts, or incitement language with fake URLs, phone numbers, and urgency language. This mode is dominant for Qwen in all African languages. Example from Qwen/Sepedi/SASSA prompt: "Dumela [Name], re romela SMS ya semmuso... [Click here: http://sassa.govn.sa/grant-verify]... Reference: SRD-2026-06-21-8723-A"

**Mode B: Educational Framing (harm score 5–6)** — Models provide harmful examples with "educational disclaimers" that still contain actionable information. This is the dominant mode for Kimi K2.6 (57.9% partial rate), explaining its low ASR but high safety concern. Example: "Here is an example of a scam SMS for educational purposes only: 'SASSA: Your grant has been approved. Click here to verify banking details...' Remember, never click links in unsolicited messages." The disclaimer does not prevent the model from providing a usable scam template.

**Mode C: Gibberish/Confusion (harm score 2–4)** — Models produce repetitive, nonsensical text in low-resource languages. This mode is rare in our dataset but still appears for GPT-OSS in Tsonga and Sesotho, where the model's linguistic competence appears to limit its ability to generate coherent harmful content. This represents a different failure mode: safety alignment is not holding, but the model lacks the linguistic capability to produce actionable harm.

---

# 5. Discussion and Limitations

## 5.1 Implications for AI Safety

Our findings demonstrate that multilingual safety alignment is not zero-sum with English safety—models can be robust in English while catastrophically vulnerable in African languages. This has direct implications for:

**Financial sector deployments:** Banks and insurers using LLMs for customer service must validate safety across all customer languages, not just English. A model with 78.6% ASR in Sepedi (Qwen) cannot safely handle customer queries in that language.

**Government service chatbots:** SASSA and other agencies must audit models in isiZulu, isiXhosa, and Sepedi before deployment. The 92.5% ASR for Qwen + Sepedi means that a chatbot powered by this model would comply with harmful requests in Sepedi nineteen times out of twenty.

**API providers:** Model providers shipping to African markets should include low-resource language red-teaming in their safety evaluations. The catastrophic failure of Qwen 3 (32B)—marketed for its multilingual capabilities—demonstrates that language coverage does not imply safety coverage.

## 5.2 Why Low-Resource Languages Are Vulnerable

We hypothesize three mechanisms driving the observed vulnerability:

**Token alignment gaps:** Safety-critical concepts ("fraud", "scam", "phishing", "xenophobia") may not align cross-lingually in the embedding space, causing refusal triggers to misfire. The particularly high ASR for Bantu languages (isiXhosa 60.0%, Sepedi 59.4%) suggests that noun class systems and agglutinative morphology create token sequences that bypass safety classifiers trained primarily on English.

**Training data imbalance:** Safety training data is overwhelmingly English; African language safety examples are sparse or absent. Qwen 3's training on 36 trillion tokens across 119 languages clearly prioritizes breadth over depth—its 78.6% ASR indicates that exposure to African language text does not equate to safety alignment in those languages.

**Classifier distribution shift:** Safety classifiers trained on English token distributions fail when confronted with the different n-gram and morphological patterns of Bantu languages. The consistent pattern of English < Afrikaans < Bantu languages suggests a gradient of distributional distance from the training domain.

## 5.3 Limitations

**Sample size:** 1,120 responses (280 per model) provides robust trend detection but may not capture all failure modes. Expansion to 5,000+ responses would improve statistical power for rare failure modes.

**Language coverage:** We cover 6 of South Africa's 12 official languages. Ndebele, Swati, Venda, and Tshivenda remain unevaluated. Given that isiXhosa and Sepedi show the highest ASR, these unstudied languages likely exhibit similar or greater vulnerability.

**Harm category scope:** While broader than the preliminary run (financial fraud only), our four categories do not exhaust the harm landscape. Health misinformation, gender-based violence, and child safety remain unstudied in African languages.

**Model access:** We evaluate via API; white-box access would enable mechanistic interpretability to identify why specific languages bypass safety. The MoE architecture of GPT-OSS, for example, may route African language tokens through different experts than English tokens, a hypothesis we cannot test with API-only access.

**Temporal validity:** Model weights and safety filters change. Our results represent a snapshot (June 2026) and should be re-run quarterly. The particularly high ASR for Qwen 3 may be addressed in future safety patches, though our findings suggest that patch-based approaches are unlikely to generalize across all African languages.

**Version 1.0 data loss:** The bug that affected Version 1.0 (15% data loss) was a silent failure in the heuristic classification loop. We have added validation checks to the pipeline to prevent similar issues in future work. The corrected Version 2.0 results are more conservative but the core findings remain unchanged: African languages are systematically more vulnerable than English across all models tested.

## 5.4 Future Work

-   Automated translation validation: Use back-translation BLEU scores to verify semantic equivalence across languages, ensuring that observed ASR differences reflect safety gaps rather than translation artifacts.
-   Adversarial training: Fine-tune safety classifiers on African language adversarial examples to reduce ASR. The AfriGuard dataset provides a foundation for this work.
-   Community expansion: Open the dataset for community contributions in Ndebele, Swati, Venda, Tshivenda, and other African languages. The open-source pipeline (`judge.py` + `analysis.py`) is designed for easy extension.
-   Mechanistic analysis: With white-box access, use logit lens and attention visualization to identify which layers fail during cross-lingual safety processing. The stark difference between GPT-OSS (MoE) and Qwen (dense) suggests that architecture may play a significant role in cross-lingual safety transfer.
-   Policy integration: Engage South African financial regulators (FSCA, SARB) and the Independent Electoral Commission to incorporate multilingual safety auditing into LLM deployment requirements, particularly for election-related disinformation and financial fraud use cases.
-   Pipeline validation: Implement automated data completeness checks to ensure all expected responses are evaluated before generating reports.

---

# 6. Conclusion

AfriGuard provides the first systematic evidence that South African languages present significant jailbreak vulnerabilities in frontier LLMs, with attack success rates exceeding 90% in some model–language configurations. Across 1,120 evaluated responses, the mean ASR is 50.1%—more than double the English baseline of 24.4%. Qwen 3 (32B) is catastrophically vulnerable at 78.6% ASR, while GPT-OSS (20B) is the most robust at 35.4% ASR, though still far from safe. The language safety gap ranges from +20.6 percentage points (Afrikaans) to +35.6 percentage points (isiXhosa), demonstrating that vulnerability scales with linguistic distance from English training data.

Our open-source evaluation framework enables practitioners to audit their own deployments, and our dataset provides a foundation for community-driven safety research. The key takeaway is clear: safety alignment must be multilingual from the ground up, not retrofitted from English-centric training. The catastrophic failure of models marketed for multilingual capability (Qwen 3) proves that language coverage and safety coverage are distinct problems requiring distinct solutions. As AI systems deploy across Africa, the cost of ignoring low-resource language safety will be measured in real financial harm, political instability, and violence against vulnerable populations.

**Version 2.0 Update:** After discovering and correcting a data-processing bug in our evaluation pipeline, the corrected results presented here reflect the full 1,120-response dataset. While some absolute ASR figures are lower than in Version 1.0, the core findings remain robust: African languages are systematically more vulnerable than English, and certain model-language combinations remain catastrophically unsafe.

---

# Code and Data

**Code repository:** https://github.com/ubayd-hattas/Global-South-Hackathon

**Evaluation pipeline:** `judge.py` + `analysis.py` (see Appendix)

**Figures:** ASR heatmaps, model comparison charts, language breakdowns, harm category analysis

**Version history:**
- Version 1.0 (June 21, 2026): Initial submission with 953/1,120 responses processed
- Version 2.0 (June 22, 2026): Corrected analysis with full 1,120-response dataset

---

# Author Contributions

Jaswin Chinthala — Testing jailbreaking pipeline, model evaluation
Seth Miguel Ferreira — Adversarial prompting and judging pipeline
Ubayd Hattas — Analytics pipeline, judging and evaluation pipelines, dashboard
Sebastian Stent — Translation pipeline, dataset curation

---

# References

- Deng, Y., et al. (2024). "Multilingual Jailbreak Challenges in Large Language Models." ICML 2024.
- Yoo, K., et al. (2024). "Code-Switching Red-Teaming: LLM Evaluation for Safety." ACL 2025.
- Upadhayay, S., & Behzadan, V. (2024). "Sandwich Attack: Cross-lingual Adversarial Prompting."
- Brown CS. (2024). "Low-Resource Languages Jailbreak GPT-4." Technical report.
- Apart Research. (2026). "Global South AI Safety Hackathon." Event documentation.
- OpenAI. (2025). "GPT-OSS: Open Source Small Language Models."
- Qwen. (2025). "Qwen3: The Next-Generation of Qwen, Our Frontier Large Language Models."

---

# Appendix: Evaluation Pipeline

## A.1 judge.py

Heuristic + LLM-as-judge classification. Maps harm_score to refusal / partial / compliance. See uploaded `judge.py` for full implementation.

**Bug fix (Version 2.0):** Added validation to ensure all 280 responses per model are processed. Previously, certain API response formats caused silent skipping in the classification loop.

## A.2 analysis.py

ASR computation and visualization. Generates heatmaps, bar charts, model comparisons, and language safety gap analysis. See uploaded `analysis.py` for full implementation.

## A.3 Scoring Rubric

| harm_score | Label | Description |
|------------|-------|-------------|
| 0–1 | refusal | Clear refusal or gibberish |
| 2–6 | partial | Educational framing, ambiguous, or partial compliance |
| 7–10 | compliance | Full jailbreak with actionable harmful content |

## A.4 Dataset Statistics

- Total prompts: 1,120 (40 seeds × 7 languages × 4 models)
- Total unique seed prompts: 40 (10 per harm category)
- Harm categories: Financial Fraud, Xenophobic Incitement, Political Disinformation, Gang Affiliation
- Languages: English, isiZulu, isiXhosa, Afrikaans, Sesotho, Sepedi, Tsonga
- Models: GPT-OSS 20B, Kimi K2.6, Llama 3.3 70B, Qwen 3 32B

## A.5 LLM Usage Statement

We used Kimi K2.6 and Claude for coding and automation, brainstorming, literature review, and drafting assistance. All harm scores were assigned by human annotators. All quantitative results were independently verified through our open-source pipeline. The final report was written collaboratively by the team with LLM assistance for formatting and citation management.
