# Decision Log

**Decision:** Project Scope Restricted to Non-contrast Brain CT
**Date:** 2026-08-11
**Reason:** Ensures the MVP is tractable and focuses on a high-clinical-value, acute condition (Intracranial Hemorrhage and related findings like midline shift).
**Alternatives considered:** General CT covering chest/abdomen, or multi-modality (MRI + CT).
**Consequences:** Simplifies dataset selection, limits preprocessing pipelines to CT (Hounsfield Units), and focuses clinical logic.

**Decision:** Use Python + FastAPI (Backend) and Next.js (Frontend)
**Date:** 2026-08-11
**Reason:** FastAPI is standard for ML/AI wrapping and async operations. Next.js provides a robust, professional UI capable of handling complex state and medical viewers.
**Alternatives considered:** Django, Flask, plain React.
**Consequences:** Need to manage clear API boundaries and potentially CORS/Proxy setups for local development.

**Decision:** Phase-by-Phase Execution Strategy
**Date:** 2026-08-11
**Reason:** Prevents overwhelming complexity and ensures each module (Data, Model, Backend, Frontend) is validated before integration.
**Alternatives considered:** Agile sprints, monolithic development.
**Consequences:** Must strictly update `CURRENT_PHASE.md` and only work on the defined phase.
