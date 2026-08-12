# MEDICAL SAFETY & ETHICS

## Core Principle
**RADIS is an AI-assisted decision support system, NOT an autonomous diagnostic tool.**

## AI Limitations & Human-in-the-Loop
- The system is designed to *assist* the radiologist by triaging and pre-populating findings.
- A licensed radiologist or qualified healthcare professional must ALWAYS review and verify the AI-generated findings and reports before they are used for clinical decision-making.
- The system cannot and will not autonomously prescribe treatment.

## Uncertainty Handling
- AI models are probabilistic. The system will use predefined confidence thresholds.
- Findings below a "high confidence" threshold will not be presented as definitive.
- If the overall study confidence is low, the system will explicitly state: `"AI unable to confidently characterize this study. Manual radiologist review required."`

## Data Privacy (MVP Scope)
- The MVP relies on public, de-identified datasets (e.g., RSNA, CQ500).
- No actual patient PHI (Protected Health Information) will be used during development.
- The UI will explicitly avoid displaying dummy PHI to reinforce the focus on imaging findings.
- External APIs (like closed-source LLMs) will NOT be sent any raw imaging data or patient identifiers.

## Prototype Disclaimer
The following disclaimer will be visible in the application UI at all times:
> **AI-assisted decision support only. This system is a research prototype and is not a substitute for a licensed radiologist or qualified healthcare professional. AI-generated findings and reports require professional verification before clinical use.**
