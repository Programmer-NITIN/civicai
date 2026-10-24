# Accessibility Statement — CivicAI

## Compliance Target

CivicAI is designed to meet **WCAG 2.1 Level AA** standards. This document describes every accessibility feature implemented across the frontend and how it is verified.

---

## 1. Perceivable

### 1.1 Text Alternatives
- All decorative elements use `aria-hidden="true"` (brand icon, step indicators).
- All images include `alt` text describing the civic issue photograph.
- Upload area has descriptive `aria-label` for screen readers.

### 1.2 Adaptable
- Semantic HTML5 elements are used throughout: `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`.
- A single `<h1>` with logical `<h2>` → `<h3>` hierarchy for screen reader heading navigation.
- `<fieldset>` with `<legend>` elements group related form controls.
- All form inputs have associated `<label>` elements with `for` attributes.

### 1.3 Distinguishable
- High contrast light theme: dark text (#0B1C30) on light background (#F8FAFC).
- Status colours (green/orange/red) are always paired with text labels (NORMAL/HIGH/URGENT/CRITICAL).
- Font sizes use relative units (rem/clamp) for user zoom support.

---

## 2. Operable

### 2.1 Keyboard Accessible
- All interactive elements (buttons, selects, inputs, links) are natively focusable.
- Every interactive element has a visible `focus-visible` outline (2px solid).
- Chat widget opens/closes with keyboard; focus is managed appropriately.
- Image upload area is keyboard-accessible with Enter/Space activation.
- Tab order follows logical reading order.

### 2.2 Skip Navigation
- A "Skip to Main Content" link appears as the first focusable element.
- Targets `#main-content` which has the `<main>` role.

### 2.3 Enough Time
- No time-limited interactions. All forms have no submission deadline.

### 2.4 Seizures and Physical Reactions
- `@media (prefers-reduced-motion: reduce)` disables all CSS animations and transitions.
- No flashing content or auto-playing video.

---

## 3. Understandable

### 3.1 Readable
- `<html lang="en">` declares the page language for screen readers.
- All text uses clear, professional language.

### 3.2 Predictable
- Navigation is consistent across all pages (Report/Track/Directory).
- Form submission follows standard patterns.

### 3.3 Input Assistance
- Form errors are displayed in a dedicated error banner with `role="alert"` and `aria-live="assertive"`.
- Required fields are validated before submission.
- Phone input has pattern validation with clear error messages.
- Chat input has `maxlength="500"` with clear placeholder.

---

## 4. Robust

### 4.1 Compatible
- All ARIA attributes use valid roles, states, and properties.
- `aria-expanded` tracks the chat widget state.
- `aria-describedby` links form inputs to helper text.
- Screen reader announcements via `aria-live="polite"` announcer.
- `role="dialog"` on chat widget with proper labeling.

---

## ARIA Live Regions

| Region | Type | Purpose |
|--------|------|---------|
| `#sr-announcer` | `polite` | Announces navigation, file upload, and pipeline completion |
| `#chat-feed` | `polite` | Announces new chat messages |
| `#form-error` | `assertive` | Announces form validation errors immediately |

---

## Testing

Accessibility is verified through:

1. **Automated tests** — `tests/test_accessibility.py` (30+ assertions)
   - Skip link existence and target
   - ARIA live regions
   - ARIA labels on all landmarks
   - Form labels and describedby associations
   - Heading hierarchy (single H1)
   - Semantic HTML (lang, meta, viewport)
   - Reduced motion CSS support
   - Focus-visible styles

2. **Manual testing checklist:**
   - [ ] Tab through entire page without mouse
   - [ ] Verify skip link appears on first Tab press
   - [ ] Screen reader announces complaint submission results
   - [ ] Chat widget is keyboard operable
   - [ ] Enable reduced motion in OS and verify no animations
   - [ ] Zoom to 200% and verify layout integrity

---

## Assistive Technology Tested

- NVDA 2024.2 + Chrome
- Windows Narrator + Edge
- VoiceOver + Safari (macOS)

---

## Contact

For accessibility feedback, please file an issue or email accessibility@civicai.amc.gov.in.
