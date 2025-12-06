# LearnHouse Course Data Schema & Importer Guide

This document explains the structure of the course data JSON files and the capabilities of the importer.

## Overview

The LearnHouse platform supports importing courses defined in JSON format. A course consists of chapters, and each chapter contains activities. Activities can be of different types: Video, Document, Dynamic (Rich Text/Interactive), and Assignment.

## File Structure

```json
{
  "name": "Course Title",
  "description": "Short description",
  "about": "Long description (markdown supported)",
  "learnings": "Key takeaways",
  "tags": "tag1, tag2",
  "thumbnail_query": "search term for image",
  "chapters": [
    {
      "name": "Chapter Title",
      "description": "Chapter description",
      "activities": [
        {
          "name": "Activity Title",
          "type": "video | document | dynamic | assignment",
          // ... type-specific properties
        }
      ]
    }
  ]
}
```

## Activity Types

### 1. Video (`type: "video"`)

*   **`video_subtype`**: `"youtube"` or `"hosted"`
*   **`video_url`**: URL of the video
*   **`blocks`**: Optional array of content blocks (transcript, notes) displayed below the video.

### 2. Document (`type: "document"`)

*   **`document_subtype`**: `"pdf"` or `"doc"`
*   **`document_url`**: URL of the document file.

### 3. Dynamic (`type: "dynamic"`)

This is the most flexible activity type, allowing for rich, interactive content using various "blocks".

*   **`blocks`**: Array of block objects.

#### Supported Block Types

| Type | Description | Properties |
| :--- | :--- | :--- |
| `text` | Rich text content | `content` (markdown string) |
| `image` | Image with caption | `content`: `{ url, alt, caption, alignment }` |
| `callout_info` | Blue info box | `content` (text) |
| `callout_warning` | Yellow warning box | `content` (text) |
| `quiz` | Multiple choice questions | `questions`: `[{ question, answers: [{ answer, correct }] }]` |
| `code_block` | Syntax highlighted code | `content`: `{ code, language }` |
| `table` | Data table | `content`: `{ headers, rows }` |
| `badge` | Colored label | `content`: `{ text, color }` |
| `button` | Link button | `content`: `{ text, url, style }` |
| `flipcard` | Interactive flashcard | `content`: `{ front, back }` |
| `math_equation` | LaTeX equation | `content`: `{ equation, display }` |
| `embedded_video` | Embed within text | `content`: `{ url, title }` |
| `pdf_block` | Embed PDF within text | `content`: `{ url, title }` |
| `web_preview` | Link preview card | `content`: `{ url, title }` |
| `scenarios` | Branching scenarios | `content`: `{ title, scenarios: [...] }` |

### 4. Assignment (`type: "assignment"`)

*   **`assignment`**: Object containing assignment details.
    *   `title`, `description`, `due_date`, `grading_type`
    *   `tasks`: Array of tasks (`FILE_SUBMISSION` or `QUIZ`)

## Example: Dynamic Activity

```json
{
  "name": "Interactive Lesson",
  "type": "dynamic",
  "blocks": [
    {
      "type": "text",
      "content": "# Lesson Title\n\nIntroduction text..."
    },
    {
      "type": "callout_info",
      "content": "Key concept to remember!"
    },
    {
      "type": "quiz",
      "questions": [
        {
          "question": "Review question?",
          "answers": [
            { "answer": "Option A", "correct": true },
            { "answer": "Option B", "correct": false }
          ]
        }
      ]
    }
  ]
}
```

