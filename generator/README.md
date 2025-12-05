# LearnHouse Course Generator & Importer

This directory contains tools for creating, validating, and importing course data into the LearnHouse platform.

## Overview

The generator tools provide a complete workflow for course creation:

1. **Create** course data in JSON format (following the schema)
2. **Validate** the JSON against the schema
3. **Import** the validated course into LearnHouse

## Files

- `schema.json` - JSON schema definition for course data structure
- `validator.py` - Validates course data JSON files against the schema
- `importer.py` - CLI tool with commands to download images and import course data
- `example1/course_data_from_example.json` - Complete example demonstrating all platform features

## Installation

The scripts require Python 3 and the following packages:

```bash
pip install jsonschema requests
```

## Quick Start

**Note:** All commands should be run from the `generator/` directory, or use the full path `generator/importer.py` when running from the project root.

### 1. Download Images (Optional)

If your course contains images from external URLs (like Unsplash), you can download them locally:

From the `generator/` directory:
```bash
cd generator
python3 importer.py download-images example1/course_data_from_example.json
```

Or from the project root:
```bash
python3 generator/importer.py download-images generator/example1/course_data_from_example.json
```

This will:
- Extract all image URLs from the course data
- Download them to an `images/` directory
- Create an `image_mapping.json` file mapping URLs to local files

Options:
```bash
python3 importer.py download-images course.json --output-dir images --force
python3 importer.py download-images course.json --mapping-file my_mapping.json
```

### 2. Validate Your Course Data

**Always validate your course data before importing.** You can use either:

**Option A: Using the importer CLI (recommended)**

From the `generator/` directory:
```bash
python3 importer.py validate example1/course_data_from_example.json
```

With verbose output:
```bash
python3 importer.py validate example1/course_data_from_example.json --verbose
```

**Option B: Using the standalone validator**
```bash
python3 validator.py example1/course_data_from_example.json
```

### 3. Import Course Data

Import a validated course into LearnHouse:

From the `generator/` directory:
```bash
python3 importer.py import example1/course_data_from_example.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123 \
  --org-id 1
```

**Note:** The import command automatically validates your course data before importing. If validation fails, the import will be aborted. Use `--skip-validation` to bypass (not recommended).

## JSON Schema

The course data must follow the structure defined in `schema.json`. Here's a summary:

### Top-Level Structure

```json
{
  "name": "Course Title",
  "description": "Short description",
  "about": "Detailed markdown overview",
  "learnings": "Key takeaways",
  "tags": "comma, separated, tags",
  "thumbnail_query": "search term",
  "chapters": [...]
}
```

### Chapters

Each chapter contains:

```json
{
  "name": "Chapter Title",
  "description": "Chapter description",
  "activities": [...]
}
```

### Activities

Activities can be one of four types:

#### 1. Video Activity

```json
{
  "name": "Video Title",
  "type": "video",
  "video_subtype": "youtube",  // or "hosted"
  "video_url": "https://www.youtube.com/watch?v=...",
  "blocks": [
    {
      "type": "text",
      "content": "Video description or transcript"
    }
  ]
}
```

#### 2. Document Activity

```json
{
  "name": "Document Title",
  "type": "document",
  "document_subtype": "pdf",  // or "doc"
  "document_url": "https://example.com/document.pdf"
}
```

#### 3. Dynamic Activity

Dynamic activities support rich content with multiple block types:

```json
{
  "name": "Lesson Title",
  "type": "dynamic",
  "blocks": [
    {
      "type": "text",
      "content": "# Heading\n\nParagraph with **bold** and *italic* text"
    },
    {
      "type": "quiz",
      "questions": [
        {
          "question": "What is the answer?",
          "answers": [
            {"answer": "Option A", "correct": true},
            {"answer": "Option B", "correct": false}
          ]
        }
      ]
    }
  ]
}
```

#### 4. Assignment Activity

```json
{
  "name": "Assignment Title",
  "type": "assignment",
  "assignment": {
    "title": "Assignment Title",
    "description": "Assignment description",
    "due_date": "2024-12-31T23:59:59Z",
    "grading_type": "PERCENTAGE",  // or "ALPHABET", "NUMERIC"
    "tasks": [
      {
        "title": "Task Title",
        "description": "Task description",
        "hint": "Helpful hint",
        "assignment_type": "FILE_SUBMISSION",  // or "QUIZ", "FORM", "OTHER"
        "max_grade_value": 50,
        "contents": {}
      }
    ]
  }
}
```

## Supported Block Types

Dynamic activities support the following block types:

### Text Blocks

```json
{
  "type": "text",
  "content": "# Heading\n\nParagraph text with **bold**, *italic*, and `code` formatting.\n\n- Bullet list\n- Items\n\n1. Numbered list\n2. Items"
}
```

Supports:
- Headings (`#`, `##`, `###`, `####`)
- Bold (`**text**`)
- Italic (`*text*`)
- Code (`\`code\``)
- Bullet lists (`-` or `*`)
- Numbered lists (`1.`, `2.`, etc.)

### Quiz Blocks

```json
{
  "type": "quiz",
  "questions": [
    {
      "question": "What is the capital of France?",
      "answers": [
        {"answer": "Paris", "correct": true},
        {"answer": "London", "correct": false},
        {"answer": "Berlin", "correct": false}
      ]
    }
  ]
}
```

### Callout Blocks

```json
{
  "type": "callout_info",
  "content": "This is an informational callout"
}
```

```json
{
  "type": "callout_warning",
  "content": "This is a warning callout"
}
```

### Image Blocks

```json
{
  "type": "image",
  "content": {
    "url": "https://example.com/image.jpg",
    "alt": "Alt text",
    "caption": "Image caption",
    "alignment": "center"  // or "left", "right"
  }
}
```

### Code Blocks

```json
{
  "type": "code_block",
  "content": {
    "code": "def hello():\n    print('Hello, World!')",
    "language": "python"  // javascript, typescript, python, java, etc.
  }
}
```

### Table Blocks

```json
{
  "type": "table",
  "content": {
    "headers": ["Column 1", "Column 2", "Column 3"],
    "rows": [
      ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
      ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
    ]
  }
}
```

### Badge Blocks

```json
{
  "type": "badge",
  "content": {
    "text": "New Feature",
    "color": "blue"  // or "green", "red", etc.
  }
}
```

### Button Blocks

```json
{
  "type": "button",
  "content": {
    "text": "Click Here",
    "url": "https://example.com",
    "style": "primary"  // or "secondary"
  }
}
```

### Flipcard Blocks

```json
{
  "type": "flipcard",
  "content": {
    "front": "Question or term",
    "back": "Answer or definition"
  }
}
```

### Math Equation Blocks

```json
{
  "type": "math_equation",
  "content": {
    "equation": "E = mc^2",
    "display": "block"  // or "inline"
  }
}
```

### Embedded Video Blocks

```json
{
  "type": "embedded_video",
  "content": {
    "url": "https://www.youtube.com/watch?v=...",
    "title": "Video Title"
  }
}
```

### PDF Blocks

```json
{
  "type": "pdf_block",
  "content": {
    "url": "https://example.com/document.pdf",
    "title": "PDF Document Title"
  }
}
```

### Web Preview Blocks

```json
{
  "type": "web_preview",
  "content": {
    "url": "https://example.com",
    "title": "Website Preview"
  }
}
```

### Scenario Blocks (Interactive)

```json
{
  "type": "scenarios",
  "content": {
    "title": "Interactive Scenario",
    "scenarios": [
      {
        "id": "1",
        "text": "You're at a crossroads. What do you do?",
        "imageUrl": "",
        "options": [
          {
            "id": "opt1",
            "text": "Go left",
            "nextScenarioId": "2"
          },
          {
            "id": "opt2",
            "text": "Go right",
            "nextScenarioId": "3"
          }
        ]
      },
      {
        "id": "2",
        "text": "You went left and found treasure!",
        "imageUrl": "",
        "options": [
          {
            "id": "opt3",
            "text": "Finish",
            "nextScenarioId": null
          }
        ]
      }
    ]
  }
}
```

## Command Reference

### Validator

```bash
python3 validator.py <file> [options]

Options:
  --schema PATH    Custom schema file (default: schema.json)
  --verbose, -v    Show detailed validation information
```

### Importer CLI

The importer provides multiple commands:

#### Import Command

```bash
python3 importer.py import <file> [options]

Required:
  --email EMAIL        Admin email for authentication
  --password PASSWORD  Admin password for authentication

Optional:
  --url URL           API URL (default: http://localhost:1338)
  --org-id ID         Organization ID (default: 1)
  --skip-validation   Skip JSON validation (not recommended)
```

#### Validate Command

```bash
python3 importer.py validate <file> [options]

Optional:
  --schema PATH       Custom schema file (default: schema.json)
  --verbose, -v       Show detailed validation information
```

#### Download Images Command

```bash
python3 importer.py download-images <file> [options]

Optional:
  --output-dir DIR    Output directory for images (default: images/)
  --mapping-file FILE Mapping file path (default: image_mapping.json)
  --force, -f         Re-download existing images
```

## Example Workflow

All commands should be run from the `generator/` directory:

1. **Create your course JSON** following the schema
2. **Download images** (optional):
   ```bash
   cd generator
   python3 importer.py download-images my_course.json
   ```
3. **Validate it**:
   ```bash
   python3 importer.py validate my_course.json --verbose
   ```
4. **Import it** (validation runs automatically before import):
   ```bash
   python3 importer.py import my_course.json \
     --url http://localhost:1338 \
     --email admin@school.dev \
     --password admin123
   ```

## Complete Example

See `example1/course_data_from_example.json` for a complete example that demonstrates:
- All activity types (video, document, dynamic, assignment)
- All block types
- Complex nested structures
- Best practices

## Troubleshooting

### Validation Errors

If validation fails, check:
- All required fields are present
- Activity types match their required fields (e.g., `video` activities need `video_url`)
- Block types use correct structure
- JSON is valid (no syntax errors)

### Import Errors

If import fails:
- Ensure the API server is running
- Verify credentials are correct
- Check that the organization ID exists
- Review error messages for specific field issues

### Common Issues

1. **"Missing required field"**: Check the schema for required fields
2. **"Invalid activity type"**: Must be one of: `video`, `document`, `dynamic`, `assignment`
3. **"Invalid block type"**: Check the list of supported block types above
4. **"Login failed"**: Verify API URL and credentials

## Schema Validation

The validator uses JSON Schema Draft 7. It checks:
- Required fields
- Data types
- Enum values
- String lengths
- Array constraints
- Custom business rules (e.g., video activities must have video_url)

## API Requirements

- LearnHouse API must be running
- Valid admin credentials
- Organization must exist
- User must have permission to create courses

## Notes

- All dates should be in ISO 8601 format (e.g., `2024-12-31T23:59:59Z`)
- URLs should be absolute and accessible
- Images and documents should be hosted externally or uploaded separately
- The importer automatically converts markdown to Tiptap format
- Quiz questions support multiple choice only (for now)

