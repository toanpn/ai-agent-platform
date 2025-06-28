# Chat Sidebar UI Specification

This document outlines the UI specifications for the chat sidebar, which corresponds to the `ChatSidebarComponent`.

## 1. General Layout

- **Node ID:** `15:1763`
- The sidebar is positioned on the left of the screen.
- It has a white background (`#FFFFFF`) and a 1px right border (`#E5E7EB`).
- The sidebar contains a header, a "New Chat" button, a search bar, and the list of past conversations.

## 2. Header

- **Node ID:** `15:1769`
- Contains the title for the conversation list.
- **Title Text:** "Đoạn hội thoại" (Conversations) (`15:1846`)
- **Typography:**
  - **Font:** Inter
  - **Weight:** 600 (Semibold)
  - **Size:** 16px
  - **Color:** `#1F2937`

## 3. New Chat Button

- **Node ID:** `15:1782`
- This button allows users to start a new conversation.
- It is visually distinct and placed below the header.
- It has a 2px bottom border of color `#0EA5E9`.
- **Icon:** A plus icon is displayed to the left of the text.
- **Text:** "New chat" (`15:1832`)
- **Typography:**
  - **Font:** Inter
  - **Weight:** 500 (Medium)
  - **Size:** 16px
  - **Color:** `#0284C7` (a shade of blue)

## 4. Search Bar

- **Node ID:** `15:1848`
- A search input field allows users to filter their conversations.
- **Placeholder Text:** "Search conversations..."
- **Styling:**
  - **Background Color:** `#F3F4F6`
  - **Border Radius:** 6px
  - **Leading Icon:** A search icon (`#9CA3AF`) is present.
- **Typography (Placeholder):**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 14px
  - **Color:** `#ADAEBC`

## 5. Conversation List

- **Node ID:** `15:1771`
- A scrollable list of past conversations.
- Each item in the list is separated by a 1px bottom border (`#F3F4F6`).

### 5.1. List Item (Default State)

- Each item displays the conversation title and the time it was last active.
- **Title Typography:**
  - **Font:** Inter
  - **Weight:** 500 (Medium)
  - **Size:** 14px
  - **Color:** `#111827`
- **Timestamp Typography:**
  - **Font:** Inter
  - **Weight:** 400 (Regular)
  - **Size:** 12px
  - **Color:** `#6B7280`

### 5.2. List Item (Active State)

- **Node ID:** `15:1854`
- The currently selected conversation is highlighted.
- **Background Color:** `#F0F9FF` (a very light blue)
- **Left Border:** A `4px` solid left border of color `#0EA5E9` indicates the active item.
- The typography for title and timestamp remains the same as the default state. 