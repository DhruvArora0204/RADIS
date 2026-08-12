# PROJECT OVERVIEW

## Project Vision
RADIS (Radiology AI Decision Intelligence System) is an AI-assisted radiology platform designed to assist radiologists in analyzing medical imaging studies. The system is positioned as **AI-assisted radiology decision support with mandatory human verification**, NOT an autonomous doctor.

The long-term vision encompasses the entire pipeline from DICOM ingestion to abnormality detection, localization, quantification, urgency prioritization, and structured report generation, culminating in radiologist review.

## MVP Scope
The MVP focuses strictly on:
- **Modality**: Non-contrast Brain CT
- **Initial Findings**:
  1. Intracranial hemorrhage
  2. Midline shift
  3. Cerebral edema
  4. Mass effect

## Target Users
- Radiologists
- Emergency Room (ER) Physicians (as a triage/priority alert system)
- Teleradiology practices

## Problem Statement
The gap between medical image acquisition and actionable clinical review can lead to delayed treatment in acute conditions like intracranial hemorrhage. Existing workflows require manual review of hundreds of slices, which is time-consuming and prone to human error, especially during high-volume periods or fatigue.

## Use Case
A patient with suspected head trauma undergoes a non-contrast head CT. RADIS ingests the DICOM, rapidly flags the presence of a hemorrhage, estimates its volume, and highlights the location. It triggers an "URGENT REVIEW" priority, pushing the study to the top of the radiologist's queue, and generates a preliminary structured report for the radiologist to review and finalize.
