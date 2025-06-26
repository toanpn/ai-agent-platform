# Agent List UI - Figma Design Breakdown

This document breaks down the UI components and layout for the Agent List page based on the Figma design.

## 1. Overall Layout

- The primary layout consists of a fixed left sidebar and a main content area.
- The main content area has a header at the top, followed by a toolbar/filter section, the agent list, and finally, a pagination control at the bottom.
- The agent list is displayed in a responsive grid, showing 3 cards per row on a standard desktop view.

## 2. Component Breakdown

### 2.1. Page Header

-   **Title**: "Danh sách trợ lý ảo" (List of virtual assistants)
    -   **Font**: Inter, Bold (700), 24px
-   **Subtitle**: "Quản lý và thiết lập trợ lý ảo của riêng bạn" (Manage and set up your own virtual assistants)
    -   **Font**: Inter, Regular (400), 16px
-   **"Create Agent" Button**:
    -   **Label**: "Tạo Agent"
    -   **Style**: Solid blue background (`#0284C7`), white text, 6px border radius.
    -   **Font**: Inter, Medium (500), 14px.
    -   **Icon**: A plus `(+)` icon precedes the text.

### 2.2. Toolbar & Filters

A container with a white background, 8px border-radius, and a light gray border. It contains the following elements from left to right:

-   **Search Input**:
    -   **Placeholder**: "Search agents..."
    -   **Style**: Standard input with a 6px border radius and a light gray border.
    -   **Icon**: A search icon is positioned on the left.
-   **Department Filter**:
    -   **Type**: Dropdown (Select)
    -   **Default Text**: "All Departments"
-   **Status Filter**:
    -   **Type**: Dropdown (Select)
    -   **Default Text**: "All Status"
-   **View Toggle**:
    -   **Functionality**: Two icon buttons to switch between Grid and List view.
    -   **Style**: The active view's button has a light blue background (`#F0F9FF`).
-   **Export Button**:
    -   **Style**: An icon-only button, presumably for exporting the agent list.

### 2.3. Agent Card (Grid View)

This is a reusable component representing a single agent.

-   **Container**:
    -   **Style**: White background, 8px border-radius, light gray border (`#E5E7EB`), and slight shadow.
    -   **Spacing**: Internal padding appears to be ~20px.
-   **Card Header**:
    -   **Avatar/Icon**: A circular icon with a background color specific to the agent's category (e.g., light blue `#E0F2FE` for Sales).
    -   **Agent Name**: (e.g., "Sales Assistant")
        -   **Font**: Inter, Medium (500), 16px.
    -   **Status Tag**: A pill-shaped tag indicating visibility.
        -   **"Public" Tag**: Light green background (`#DCFCE7`), dark green text (`#166534`).
        -   **"Private" Tag**: Light yellow background (`#FEF9C3`), dark yellow text (`#854D0E`).
        -   **Font**: Inter, Regular (400), 12px.
    -   **More Options Menu**: A vertical ellipsis (3-dots) icon on the far right for actions like "Edit" or "Delete".
-   **Card Body**:
    -   **Description**: A brief summary of the agent's function.
        -   **Font**: Inter, Regular (400), 14px, Gray color (`#4B5563`).
    -   **Metadata**: A section with key-value pairs.
        -   **Labels** (`Department:`, `Created:`): Gray text (`#6B7280`), 14px.
        -   **Values** (`Sales`, `Mar 15, 2023`): Darker gray text (`#374151`), 14px.

### 2.4. Pagination

-   **Container**: Sits at the bottom of the page, spanning the width of the content area.
-   **Info Text**: Displays the current item range, e.g., "Hiển thị 6 trong tổng số 12" (Showing 6 of 12).
    -   **Font**: Inter, Regular (400), 14px.
-   **Navigation Controls**:
    -   **Buttons**: Previous/Next arrow buttons and numbered page buttons.
    -   **Style**: The active page button has a light blue background (`#F0F9FF`) and a blue border. Disabled buttons have reduced opacity (0.5).

## 3. Visuals & Interaction Notes

-   **Hover States**: Although not explicitly detailed, standard hover effects (e.g., subtle shadow increase on cards, background color change on buttons) should be implemented to provide user feedback.
-   **Reusable Components**:
    -   The **Agent Card** is a primary reusable component.
    -   The **Status Tag** is a smaller, reusable component.
    -   The **Filter Dropdowns** and **Pagination Controls** are also designed for reuse. 