# UI/UX PLAN

## User Flow
1. **Login**: User authenticates (mocked for MVP).
2. **Dashboard**: View a worklist of studies (uploaded vs processed vs finalized).
3. **Upload**: User drags and drops a DICOM ZIP file.
4. **Processing State**: UI shows a progress spinner for AI inference.
5. **Study View (Main UI)**:
   - Viewer in the center.
   - Findings on the right.
   - Report drafting on the bottom or a separate tab.
6. **Interaction**: User clicks on a finding -> Viewer jumps to the corresponding slice and highlights the bounding box.
7. **Reporting**: User switches to the Report tab, reviews the generated text, edits, and clicks "Finalize".

## Main UI Layout
```text
┌───────────────────────────────────────────────────────────┐
│ RADIS                         Study ID        AI Status    │
├───────────────┬───────────────────────────┬───────────────┤
│               │                           │               │
│ STUDY INFO    │                           │ AI FINDINGS   │
│               │       CT VIEWER           │               │
│ Modality      │                           │               │
│ Body region   │       CT IMAGE            │ Hemorrhage    │
│ Slice count   │                           │ 94%           │
│               │                           │               │
│               │                           │ Midline shift │
│               │                           │ 87%           │
│               │                           │               │
├───────────────┴───────────────────────────┴───────────────┤
│ Slice: 63/128      Window/Level      Zoom      Pan        │
├───────────────────────────────────────────────────────────┤
│ FINDINGS | ASSESSMENT | REPORT | AUDIT                    │
└───────────────────────────────────────────────────────────┘
```

## Viewer Features
- Will likely integrate an existing lightweight viewer library or build a custom HTML5 canvas viewer if the slices are pre-rendered to PNG/JPEG by the backend for the MVP.
- Essential controls: Scroll to navigate slices, Window/Level adjustments (crucial for CT).

## AI Findings Presentation
- Clearly display confidence.
- Present a visual explanation (bounding box or heatmap).
- Group findings logically.

## Accessibility & Radiologist Workflow
- Dark mode by default (standard for radiology workstations).
- High contrast text.
- Keyboard shortcuts for navigating slices (Up/Down arrows).
