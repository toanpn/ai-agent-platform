# Figma Design Spec: Login & Register

This document outlines the UI, styling, and component specifications for the Login and Register pages based on the Figma designs.

- **Login Page:** [Figma Link](https://www.figma.com/design/kmpH5SSFN0841bVtAFTvqF/AlibabaxHackathon?node-id=12-197)
- **Register Page:** [Figma Link](https://www.figma.com/design/kmpH5SSFN0841bVtAFTvqF/AlibabaxHackathon?node-id=12-277)

## 1. Global Styles

### 1.1. Colors

- **Primary Background:** `#F3F4F6` (Light Gray)
- **Primary Blue (Active, Links):** `#0EA5E9`
- **Primary Blue Gradient (Buttons):** Linear gradient from `#0EA5E9` to `#0C4A6E`
- **Primary Text:** `#111827` (Almost Black)
- **Secondary Text / Labels:** `#374151` (Dark Gray)
- **Tertiary Text / Subtitles:** `#6B7280` (Gray)
- **Placeholder Text:** `#ADAEBC`
- **Inactive/Muted Text:** `#64748B`
- **Borders / Dividers:** `#D1D5DB` / `#E5E7EB`
- **White:** `#FFFFFF`
- **Error/Accent (Google):** `#EF4444`
- **Accent (Microsoft):** `#3B82F6`

### 1.2. Typography

- **Font Family:** `Inter`
- **Headings (H1):** Bold (700), 30px
- **Subheadings:** Regular (400), 16px
- **Buttons / Tabs:** Medium (500) / Semi-bold (600), 14px/16px
- **Input Labels:** Medium (500), 14px
- **Input Text:** Regular (400), 16px
- **Body/Links:** Regular (400), 14px

### 1.3. Layout

- The main content is centered on the page.
- The login/register form container has a fixed width of `448px`.
- Consistent spacing and gaps are used (e.g., 20-24px between form elements).

## 2. Components

### 2.1. Logo & Branding

- **Logo:** A circular logo with a blue gradient and a white icon inside.
- **Application Name:** "KiotViet AI Agent Platform" (Bold, 30px, `#111827`).
- **Slogan:** "Empowering your business with intelligent automation" (Regular, 16px, `#6B7280`).

### 2.2. Form Container

- **Background:** White (`#FFFFFF`)
- **Border Radius:** `12px`
- **Shadow:** `box-shadow: 0px 10px 15px 0px rgba(0, 0, 0, 0.1), 0px 4px 6px 0px rgba(0, 0, 0, 0.1)`

### 2.3. Tabs (Login/Register)

- A tabbed interface to switch between the Login and Register forms.
- **Active Tab:** Text is `Semi-bold (600)` with a primary blue color (`#0EA5E9`) and a blue bottom border.
- **Inactive Tab:** Text is `Regular (400)` with a muted gray color (`#64748B`).

### 2.4. Input Fields

- **Fields:** Full Name (Register), Email Address, Password, Confirm Password (Register).
- **Label:** `Medium (500)`, `14px`, `#374151`.
- **Input Container:**
    - Background: White (`#FFFFFF`)
    - Border: `1px solid #D1D5DB`
    - Border Radius: `8px`
    - Padding: Left-padding to accommodate icon.
- **Input Text:** `Regular (400)`, `16px`, placeholder color `#ADAEBC`.
- **Icons:**
    - Placed inside the input field on the left.
    - Color: `#9CA3AF` (Gray).
    - Icons used: User, Email, Lock, Eye (for password visibility).

### 2.5. Buttons

- **Primary Action Button ("Sign in" / "Register")**
    - Background: Linear gradient from `#0EA5E9` to `#0C4A6E`.
    - Text: "Sign in" or "Register", White (`#FFFFFF`), `Medium (500)`, `14px`.
    - Border Radius: `8px`.
    - Full-width.
- **Social Login Buttons (Google / Microsoft)**
    - Background: White (`#FFFFFF`).
    - Border: `1px solid #D1D5DB`.
    - Text: "Google" or "Microsoft", Dark Gray (`#374151`), `Medium (500)`, `14px`.
    - Border Radius: `8px`.
    - Contains the respective service logo.
    - Split into two buttons, each taking up half the width with a gap.

### 2.6. Other Form Elements

- **"Remember me" Checkbox:** A standard checkbox with the label "Remember me" (`Regular (400)`, `14px`, `#374151`).
- **"Forgot password?" Link:** A text link on the right side of the "Remember me" checkbox.
    - Text: "Forgot password?", `Medium (500)`, `14px`, Primary Blue (`#0284C7`).
- **Divider:**
    - A horizontal line with text "or continue with" in the middle.
    - Line color: `#E5E7EB`.
    - Text color: `#9CA3AF`.

### 2.7. Footer

- **Copyright:** "© 2023 KiotViet AI Agent Platform. All rights reserved."
- **Links:** "Terms", "Privacy", "Help", "Contact".
- **Style:** All footer text is `Regular (400)`, `14px`, `#6B7280`. 