# Agent Participants List UI Specification

This document outlines the UI specifications for the "Agent Participants List" sidebar, which appears on the right side of the chat interface. This may correspond to a new component or an adaptation of components from the `agent-management` feature.

## 1. General Layout

- **Node ID:** `15:1765`
- The sidebar is positioned on the right of the screen.
- It has a white background (`#FFFFFF`) and a 1px left border (`#E5E7EB`).
- It contains a header and a scrollable list of agent detail cards.

## 2. Header

- **Node ID:** `15:1817`
- **Title Text:** "Danh sách trợ lý" (List of assistants) (`15:1884`)
- **Typography:**
  - **Font:** Inter
  - **Weight:** 600 (Semibold)
  - **Size:** 16px
  - **Color:** `#1F2937`

## 3. Agent Card

- Each agent in the list is displayed in a detailed card.
- **Border Radius:** 8px
- The border and header background color of the card are themed based on the agent's specialty.

### 3.1. Card Header

- Contains the agent's avatar, name, and privacy status.
- **Avatar:**
  - **Size:** 40x40px
  - **Shape:** Circular
- **Agent Name Typography:**
  - **Font:** Inter
  - **Weight:** 500 (Medium)
  - **Size:** 16px
  - **Color:** `#111827`
- **Privacy Tag ("Private"):**
  - **Background:** `#DCFCE7` (Green theme)
  - **Text Color:** `#166534`
  - **Typography:** Inter, 400, 12px
  - **Border Radius:** `9999px`

### 3.2. Card Body

- Contains details about the agent's specialties and capabilities.

- **Section Title Typography ("Specialties", "Capabilities"):**
  - **Font:** Inter
  - **Weight:** 500 (Medium)
  - **Size:** 12px
  - **Color:** `#6B7280`

- **Specialty Tags:**
  - Pill-shaped tags (`border-radius: 9999px`).
  - Colors match the agent's theme.

- **Capabilities List:**
  - An unordered list of agent skills.
  - **Leading Icon:** A green checkmark (`#22C55E`).
  - **Text Typography:** Inter, 400, 12px, Color: `#4B5563`.

### 3.3. Agent Card Color Variants

#### a) Marketing Specialist (Purple Theme)

- **Node ID:** `15:1819`
- **Card Border:** 1px solid `#DDD6FE`
- **Header Background:** `#F5F3FF`
- **Specialty Tag Background:** `#EDE9FE`
- **Specialty Tag Text Color:** `#5B21B6`

#### b) Financial Advisor (Blue Theme)

- **Node ID:** `15:1820`
- **Card Border:** 1px solid `#BAE6FD`
- **Header Background:** `#F0F9FF` (Note: Figma shows `#M4ZDJK` which is a light blue, likely `#F0F9FF`)
- **Specialty Tag Background:** `#E0F2FE`
- **Specialty Tag Text Color:** `#075985`

#### c) Data Analyst (Green Theme)

- **Node ID:** `15:1821`
- **Card Border:** 1px solid `#BBF7D0`
- **Header Background:** `#F0FDF4`
- **Specialty Tag Background:** `#DCFCE7`
- **Specialty Tag Text Color:** `#166534` 