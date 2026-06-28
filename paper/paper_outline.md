# SAFE: Structured Agentic Feedback Engine for Controlled Program Repair

## Abstract
Brief overview of the advantages of structured feedback over naive prompting in LLM-based APR.

## 1. Introduction
- The rise of LLMs in software engineering.
- Limitations of naive prompting (hallucinations, non-minimal patches).
- The "SAFE" approach: Localization, Classification, Strategy, and Minimal Patching.

## 2. Methodology
- **Dataset**: QuixBugs Python benchmark.
- **Baseline**: Full-context naive prompting.
- **SAFE Pipeline**:
    - Execution & Error Capture
    - Error Classification
    - Context Analysis (Snippet extraction)
    - Repair Strategy Selection
    - Localized Prompting
    - AST-based Integration
- **Model**: Local DeepSeek-Coder:6.7b-instruct.

## 3. Experimental Setup
- Description of metrics: Patch Minimality, Syntax Reliability, Prompt Efficiency, Hallucination Rate.
- Hardware/Software environment (Ollama on D: drive).

## 4. Results
- **Repair Success**: Comparable success rates.
- **Patch Minimality**: SAFE significantly reduces the number of modified lines.
- **Syntax Reliability**: SAFE produces fewer broken generations.
- **Prompt Efficiency**: Localized context reduces prompt size.
- **Hallucination reduction**: Targeted strategies minimize fake code generation.

## 5. Discussion
- Analysis of specific bug categories where SAFE excels.
- Trade-offs between full-context and localized repair.

## 6. Related Work
- Comparison with DynaFix, TRACE, and MGDebugger.

## 7. Conclusion
- Summary of SAFE's contributions to stable and resource-efficient program repair.
