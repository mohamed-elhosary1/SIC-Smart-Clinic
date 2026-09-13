---
name: Clinical Intelligence
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#444651'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#002d48'
  on-tertiary: '#ffffff'
  tertiary-container: '#004469'
  on-tertiary-container: '#56b3f9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#cce5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d31'
  on-tertiary-fixed-variant: '#004b73'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  data-tabular:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

The design system projects clinical precision, operational authority, and reassuring calm. Engineered for hospital administrators, triage nurses, and medical practitioners, the aesthetic balances high-density information architecture with serene, sterile visual breathing room. 

The design style is **Corporate / Modern** elevated by clinical minimalism:
- **Tone:** Methodical, infallible, swift, and strictly functional.
- **Atmosphere:** Controlled hospital lighting—bright, crisp, glare-free, and legible under high-stress operating environments.
- **Visual Discipline:** Zero decorative illustrations, no organic non-functional gradients, and no ambiguous iconography. Visual priority is dictated entirely by triage urgency, diagnostic state, and operational workflow.

## Colors

The color palette is built on clinical trust, rapid state identification, and high contrast against bright medical tablet and workstation displays.

### Primary & Functional Accents
- **Primary Hospital Blue (`#1E3A8A`):** Anchors navigation, critical calls-to-action, active sidebar states, and authoritative visual elements.
- **Medical Teal (`#0D9488`):** Serves as secondary validation, specialized clinical tooling, diagnostics metrics, and interactive confirmation.
- **Regular Routine (`#0284C7`):** Represents routine ambulatory appointments, regular priority queues, and standard patient communication.

### Canvas & Surface
- **Canvas / App Background:** `#F8FAFC` (Slate-50) creates a soft, clinical off-white canvas that reduces eye fatigue across long 12-hour shifts.
- **Cards & Data Surfaces:** `#FFFFFF` (Pure White) provides crisp separation for patient charts, vitals streams, and tabular records.
- **Borders & Dividers:** `#E2E8F0` delivers clear structural boundaries without visual noise.

### Clinical Triage & State Matrix
Status indicators must never rely on color alone; always pair these values with standard medical icons or explicit text tokens:
- **Emergency / Critical (`#DC2626`):** Immediate life-safety alerts, acute triage, abnormal lab flags, code blue logs. Surface tint: `#FEF2F2`.
- **Pending / Warning (`#D97706`):** Awaiting lab results, unverified insurance, pending prescription authorization. Surface tint: `#FFFBEB`.
- **In Progress (`#3B82F6`):** Ongoing examination, surgery in room, infusion delivering. Surface tint: `#EFF6FF`.
- **Completed / Stable (`#16A34A`):** Discharged, negative pathology, administered dose, stable vitals. Surface tint: `#F0FDF4`.

### Typography Colors
- **Primary Text (`#0F172A`):** Maximum contrast for patient identifiers, diagnostic codes, and primary data figures.
- **Muted Text (`#64748B`):** Secondary metadata, timestamps, units of measurement, and table column headers.

## Typography

Typography prioritizes rapid clinical scan speeds and total elimination of ambiguity between characters (e.g., `0` vs `O`, `1` vs `l`).

- **Display & Section Headers:** **Hanken Grotesk** provides an authoritative, modern, and clean presence for department designations, analytical dashboard totals, and modal headers.
- **Body, Inputs & Labels:** **Inter** ensures uniform glyph weights, high legibility at micro-scales, and exceptional performance across dense electronic health records (EHR).
- **Tabular Figures (`tnum`):** All vital signs, timestamps, dosage amounts, and bed numbers must enforce `font-feature-settings: "tnum" 1, "cv05" 1` to align column decimals perfectly and prevent layout shifting during real-time telemetry streaming.
- **Uppercase Restraint:** Uppercase styling is strictly reserved for micro badge labels (`label-sm`), medical units (e.g., `BPM`, `MG/DL`), and standard code nomenclature (e.g., `ICD-10`).

## Layout & Spacing

The layout employs a responsive 12-column fluid grid system optimized for information-dense enterprise workflows.

### Breakpoints & Grid Rules
- **Desktop (≥ 1280px):** 12 columns, 24px (`gutter-desktop`) gutters, 32px (`margin-desktop`) outer canvas padding. Persistent 260px navigation sidebar with optional collapsible secondary sub-rail (e.g., patient record tree).
- **Tablet / Clinical Workstation (768px - 1279px):** 8 columns, 16px (`gutter`) gutters, 24px outer margins. Navigation collapses to an icon rail (72px).
- **Mobile Handheld (< 768px):** 4 columns, 16px gutters, 16px (`margin`) outer margins. Navigation moves to a bottom app bar or slide-over drawer.

### Spacing Cadence
- Use `space-xs` (4px) strictly for micro element relations (tag icons, status dots next to text).
- Use `space-sm` (8px) for compact data row padding, segmented controls, and button internal vertical clearance.
- Use `space-md` (12px) for table cell padding, form input clusters, and list item spacing.
- Use `space-lg` (20px) for standard card content interior padding.
- Use `space-xl` (32px) for dashboard module separation and header-to-workspace gaps.

## Elevation & Depth

Visual depth is achieved through surgical, low-contrast layering instead of heavy ambient shadows. The interface must look anchored and architectural rather than floating.

### 1. Structural Outlines
Every card, drawer, and table is bounded by a crisp 1px solid border (`#E2E8F0`). In light mode, boundaries rely on borders before shadows.

### 2. Ambient Elevation Levels
- **Level 0 (Base):** App canvas background (`#F8FAFC`), no elevation.
- **Level 1 (Surfaces & Cards):** Pure White (`#FFFFFF`) with 1px border (`#E2E8F0`) and subtle contact shadow: `box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)`.
- **Level 2 (Dropdowns, Flyouts & Toolbars):** `#FFFFFF` with `box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.
- **Level 3 (Modals & Triage Sheets):** `#FFFFFF` framed by a 1px border (`#CBD5E1`) over a darkened backdrop blur (`rgba(15, 23, 42, 0.45)`, `backdrop-filter: blur(4px)`). Shadow: `box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.06)`.

## Shapes

The design uses balanced, controlled rounded geometry (`roundedness: 2`). This choice humanizes the clinical workspace while preserving the structural rigidity required for dense data tables.

- **Micro Shapes (4px / `rounded-sm`):** Checkboxes, triage color tags, inline micro-badges.
- **Form Controls & Actionables (8px / `rounded-md`):** Text fields, select menus, standard action buttons, and segmented control tabs.
- **Containers & Panels (12px / `rounded-lg`):** Patient data cards, vitals charts, lab result summaries, callout panels.
- **Parent Modals & Workspaces (16px / `rounded-xl`):** Flyout drawers, diagnostic modals, primary dashboard panel wrappers.
- **Pills (`rounded-full`):** Exclusively reserved for status chips, triage urgency pills, and round avatar initials.

## Components

### Buttons
- **Primary:** Background `#1E3A8A`, text `#FFFFFF`, border none, 8px border radius. Hover: `#172554`. Focus: 2px ring `#0D9488` with 2px white offset.
- **Secondary / Subtle:** Background `#F1F5F9`, text `#0F172A`, border 1px solid `#CBD5E1`. Hover: `#E2E8F0`.
- **Medical / Action Teal:** Background `#0D9488`, text `#FFFFFF`. Reserved for final execution commands (e.g., "Confirm Prescription", "Begin Consultation"). Hover: `#0F766E`.
- **Destructive / Emergency:** Background `#DC2626`, text `#FFFFFF`. Hover: `#B91C1C`.
- **Sizes:** Height 36px (compact default for high-density tools) with 12px horizontal padding; 44px (touch/mobile devices) with 16px horizontal padding.

### Clinical Status Chips & Badges
Badges use 100% border-radius (`rounded-full`), `label-sm` (11px semi-bold uppercase), an inline 6px status dot, and low-saturation backgrounds:
- **Emergency:** Text `#DC2626`, background `#FEF2F2`, dot `#DC2626`.
- **Routine / Regular:** Text `#0284C7`, background `#F0F9FF`, dot `#0284C7`.
- **In Progress:** Text `#2563EB`, background `#EFF6FF`, dot `#3B82F6`.
- **Completed:** Text `#16A34A`, background `#F0FDF4`, dot `#16A34A`.
- **Pending:** Text `#B45309`, background `#FFFBEB`, dot `#D97706`.

### Inputs & Form Elements
- **Text Inputs & Dropdowns:** 36px height, white background, 1px solid border `#E2E8F0`, 8px border radius. Placeholder `#94A3B8`. Focus state shifts border to `#1E3A8A` with a 1px ring in `#1E3A8A`.
- **Validation State:** Errors swap the border to `#DC2626` accompanied by an inline error message in `body-sm` with a medical warning icon.

### Checkboxes & Radios
- Size 16px × 16px. Inactive: border 1.5px solid `#CBD5E1`, background white. Active: background `#1E3A8A`, border `#1E3A8A`, checkmark icon white.

### Data Tables (Clinical Core)
- **Header Row:** Background `#F8FAFC`, border-bottom 1px solid `#E2E8F0`, text `label-md` `#64748B`, uppercase, height 40px.
- **Data Rows:** Background `#FFFFFF`, height 48px (dense) or 56px (expanded), border-bottom 1px solid `#F1F5F9`. Hover row: `#F8FAFC`. Active/Selected row: `#EFF6FF` with a 2px left border in `#1E3A8A`.
- **Numeric Data:** Right-aligned with tabular figures enabled.

### Cards & Patient Summaries
- Pure white `#FFFFFF` surface with 1px border `#E2E8F0` and `rounded-lg` (12px).
- Internal header section separated by a subtle 1px border `#F1F5F9` with explicit metadata slots (e.g., Medical Record Number [MRN], Age, Sex, Attending Physician).