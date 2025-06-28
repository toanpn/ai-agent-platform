# Chat Page UI Specification

This document outlines the UI specifications for the main chat page, based on the Figma design.

## 1. Overall Layout

- The chat page is the central part of the screen, sitting between the conversations sidebar on the left and the agent participants list on the right.
- It has a light grey background (`#F9FAFB`).
- The layout consists of a header, the chat message history, suggested prompt buttons, and the chat input area at the bottom.

## 2. Header

- **Node ID:** `15:1773`
- A header is displayed at the top of the chat page.
- It is separated from the content below by a 1px bottom border (`#E5E7EB`).

### 2.1. Chat Title

- **Node ID:** `15:1937`
- The title of the current chat session is displayed on the left.
- **Text:** "E-commerce Strategy"
- **Typography:**
  - **Font:** Inter
  - **Weight:** 600 (Semibold)
  - **Size:** 20px
  - **Color:** `#1F2937`

### 2.2. Header Buttons

- **Node IDs:** `15:1940`, `15:1941`
- On the right side of the header, there are action buttons.
- The design shows two icon buttons. These could be for actions like "Share" or "More options".
- **Icon Color:** `#4B5563`

## 3. Chat Messages Area

- **Node ID:** `15:1774`
- This area contains the scrollable list of all messages in the conversation.
- It has a flexible height to fill the space between the header and the input area.
- Messages from the user and the agents are aligned differently. User messages on the right, agent messages on the left.

*See `chat-message-spec.md` for details on individual message styling.*

## 4. Suggested Prompts

- **Node ID:** `15:1775`
- Below the chat history, a set of buttons with suggested user prompts can be displayed.
- These buttons help guide the user on what to ask next.

### 4.1. Button Styling

- **Node IDs:** `15:1875`, `15:1876`, `15:1877`, `15:1878`
- **Background Color:** `#F3F4F6`
- **Border Radius:** `9999px` (pill-shaped)
- **Typography:**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 14px
  - **Color:** `#1F2937`
- **Padding:** Provides ample space around the text, e.g., `12px 16px`. 