# Chat Input UI Specification

This document outlines the UI specifications for the chat input area, which corresponds to the `ChatInputComponent`.

## 1. General Layout

- **Node ID:** `15:1776`
- The chat input component is fixed at the bottom of the chat page.
- It has a white background (`#FFFFFF`) and a 1px top border (`#E5E7EB`).
- It consists of a main text area with action buttons, and a secondary row of formatting helper buttons.

## 2. Message Text Area

- **Node ID:** `15:1879`
- This is the primary input field for the user's message.
- **Placeholder Text:** "Type your message..."
- **Styling:**
  - **Background Color:** `#FFFFFF`
  - **Border:** 1px solid `#D1D5DB`
  - **Border Radius:** 8px
- **Typography (Placeholder):**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 16px
  - **Color:** `#ADAEBC`

## 3. Action Buttons

- **Node ID:** `15:1880`
- A set of buttons is located inside or next to the text area.
- The design includes icons for:
  - Attach File (`15:2062`)
  - Microphone (`15:2065`)
  - Image (`15:2068`)
- **Icon Color:** `#6B7280`

### 3.1. Send Button

- **Node ID:** `15:1965`
- A circular button to send the message.
- **Background Color:** `#0284C7` (Blue)
- **Border Radius:** `9999px` (Circle)
- **Icon:** A send/submit icon.
- **Icon Color:** `#FFFFFF` (White)

## 4. Formatting Toolbar

- **Node ID:** `15:1816`
- A row of helper buttons below the main input area to assist with message formatting.
- **Buttons:** "Code", "Table", "List"
- **Typography:**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 14px
  - **Color:** `#6B7280`
- **Icons:** Each button is accompanied by a corresponding icon.
- **"All agents will respond..." Text:** A small note (`15:1970`) is displayed on the right, informing the user about the agent response behavior.
  - **Typography:** Inter, 400, 12px, color `#6B7280`. 