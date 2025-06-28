# Chat Message UI Specification

This document outlines the UI specifications for individual chat messages, which corresponds to the `ChatMessageComponent`.

## 1. General Structure

- Messages are displayed in a list, with user and agent messages visually distinct.
- Each message block typically consists of an avatar, the message bubble, and a timestamp.

## 2. User Message

- **Node ID:** `15:1813`
- User messages are aligned to the **right** side of the chat area.

### 2.1. Avatar

- **Node ID:** `15:1874`
- The user's avatar is displayed to the right of the message bubble.
- **Size:** 32x32px
- **Shape:** Circular (Border Radius: 9999px)

### 2.2. Message Bubble

- **Node ID:** `15:1873`
- The container for the user's text.
- **Background Color:** `#0284C7` (Blue)
- **Border Radius:** 8px
- **Box Shadow:** `0px 1px 2px 0px rgba(0, 0, 0, 0.05)`
- **Typography:**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 16px
  - **Color:** `#FFFFFF` (White)

## 3. Agent Message

- **Node IDs:** `15:1810` (Marketing), `15:1811` (Finance), `15:1812` (Data)
- Agent messages are aligned to the **left** side of the chat area.

### 3.1. Avatar

- **Node ID:** `15:1867`
- The agent's avatar is displayed to the left of the message bubble.
- **Size:** 32x32px
- **Shape:** Circular

### 3.2. Message Bubble

- The agent message bubble has a header containing the agent's name and specialty, and a body for the message content.
- **Text Typography (all agents):**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 16px
  - **Color:** `#1F2937`
- **Timestamp:** Displayed below the bubble.
  - **Typography:** Inter, 400, 12px, Color: `#6B7280`

### 3.3. Agent Color Variants

Agents are color-coded based on their specialty.

#### a) Marketing Specialist (Purple)

- **Bubble Background:** `#EDE9FE`
- **Agent Name Typography:**
  - **Weight:** 500 (Medium)
  - **Size:** 16px
  - **Color:** `#6D28D9`
- **Specialty Tag ("Marketing"):**
  - **Background Color:** `#DDD6FE`
  - **Text Color:** `#5B21B6`

#### b) Financial Advisor (Blue)

- **Bubble Background:** `#E0F2FE`
- **Agent Name Typography:**
  - **Weight:** 500 (Medium)
  - **Size:** 16px
  - **Color:** `#0369A1`
- **Specialty Tag ("Finance"):**
  - **Background Color:** `#BAE6FD`
  - **Text Color:** `#075985`

#### c) Data Analyst (Green)

- **Bubble Background:** `#DCFCE7`
- **Agent Name Typography:**
  - **Weight:** 500 (Medium)
  - **Size:** 16px
  - **Color:** `#15803D`
- **Specialty Tag ("Analytics"):**
  - **Background Color:** `#BBF7D0`
  - **Text Color:** `#166534`

## 4. System Message

- **Node ID:** `15:1809`
- A centered message to provide information about the conversation status.
- **Example Text:** "Assigning specialized agents to this conversation"
- **Styling:**
  - **Background:** `#E5E7EB`
  - **Border Radius:** `9999px` (pill-shaped)
  - **Typography:** Inter, 400, 12px, Color: `#4B5563` 