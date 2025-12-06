# LearnHouse Course & Organization Importer

A powerful command-line tool for importing courses and organizations into LearnHouse with robust error handling, parallel processing, and comprehensive validation.

## Features

### Core Functionality
- **Course Import** - Import complete courses with chapters and activities
- **Organization Import** - Import/update organization settings
- **Image Upload** - Automatic download and upload to server storage
- **Parallel Processing** - 3x faster image uploads with concurrent processing
- **Template Generation** - Quick-start templates for courses and organizations

### Robust & Reliable
- **Retry Logic** - Automatic retry with exponential backoff (3 attempts)
- **Error Handling** - Custom exceptions with actionable error messages
- **Pre-flight Checks** - Validates API, auth, and org access before import
- **URL Validation** - Checks that external resources are accessible
- **Graceful Failures** - Continues on error with comprehensive summary

### User Experience
- **Progress Tracking** - Visual progress bars for long operations
- **Dry-Run Mode** - Preview changes without executing
- **Verbose Logging** - Detailed operation logs for debugging
- **Import Summary** - Complete statistics after import
- **Helpful Tips** - Actionable suggestions for fixing errors

## Installation

### Required Dependencies
```bash
pip install jsonschema requests
```

### Optional Dependencies (Recommended)
```bash
pip install tqdm tenacity
```

**Why optional dependencies?**
- `tqdm` - Provides progress bars (falls back to simple output)
- `tenacity` - Advanced retry logic (falls back to basic retry)

## Quick Start

### 1. Generate a Template
```bash
# Create a course template
python importer.py init-course --output my-course.json

# Create an organization template
python importer.py init-org --output my-org.json
```

### 2. Edit Your Template
Open the generated JSON file and customize it with your content.

### 3. Validate
```bash
python importer.py validate my-course.json
```

### 4. Import
```bash
python importer.py import my-course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123
```

## Commands

### Template Generation

#### `init-course` - Generate Course Template
```bash
python importer.py init-course [--output FILE]
```

Creates a starter course template with examples of all block types.

**Options:**
- `--output, -o` - Output file path (default: course-template.json)

#### `init-org` - Generate Organization Template
```bash
python importer.py init-org [--output FILE]
```

Creates a starter organization template with all configuration options.

**Options:**
- `--output, -o` - Output file path (default: organization-template.json)

---

### Validation

#### `validate` - Validate Course Data
```bash
python importer.py validate FILE [OPTIONS]
```

Validates course JSON against schema.

**Options:**
- `--schema` - Path to custom schema file
- `--verbose, -v` - Show detailed validation information

#### `validate-org` - Validate Organization Data
```bash
python importer.py validate-org FILE [OPTIONS]
```

Validates organization JSON against schema.

**Options:**
- `--schema` - Path to custom schema file
- `--verbose, -v` - Show detailed validation information

---

### Import

#### `import` - Import Course
```bash
python importer.py import FILE [OPTIONS]
```

Imports course data into LearnHouse platform.

**Required Options:**
- `--email` - Admin email for authentication
- `--password` - Admin password for authentication

**Optional Options:**
- `--url` - LearnHouse API URL (default: http://localhost:1338)
- `--org-id` - Organization ID (default: 1)
- `--verbose, -v` - Show detailed logging
- `--dry-run` - Preview without making changes
- `--skip-preflight` - Skip pre-flight checks

**Example:**
```bash
python importer.py import course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123 \
  --verbose
```

#### `import-org` - Import Organization
```bash
python importer.py import-org FILE [OPTIONS]
```

Imports or updates organization data.

**Required Options:**
- `--email` - Admin email for authentication
- `--password` - Admin password for authentication

**Optional Options:**
- `--url` - LearnHouse API URL (default: http://localhost:1338)
- `--verbose, -v` - Show detailed logging

---

### Utilities

#### `download-images` - Download Images
```bash
python importer.py download-images FILE [OPTIONS]
```

Downloads all images from course data to local directory.

**Options:**
- `--output-dir, -o` - Output directory (default: images/)
- `--force, -f` - Overwrite existing files

#### `publish` - Complete Workflow
```bash
python importer.py publish FILE [OPTIONS]
```

Complete workflow: validate, download images, and import.

**Required Options:**
- `--email` - Admin email
- `--password` - Admin password

**Optional Options:**
- `--url` - API URL
- `--org-id` - Organization ID
- `--images-dir` - Images directory
- `--skip-images` - Skip image download
- `--skip-validation` - Skip validation (not recommended)
- `--verbose, -v` - Detailed logging

---

## Usage Examples

### Basic Import
```bash
python importer.py import course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123
```

### Import with Verbose Logging
```bash
python importer.py import course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123 \
  --verbose
```

### Dry-Run (Preview)
```bash
python importer.py import course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123 \
  --dry-run
```

### Complete Workflow
```bash
python importer.py publish course.json \
  --url http://localhost:1338 \
  --email admin@school.dev \
  --password admin123 \
  --verbose
```

---

## Course JSON Structure

### Minimal Example
```json
{
  "name": "My Course",
  "description": "Course description",
  "about": "Detailed markdown overview",
  "learnings": "Key takeaways",
  "tags": "comma, separated, tags",
  "thumbnail_query": "search term",
  "chapters": [
    {
      "name": "Chapter 1",
      "description": "Chapter description",
      "activities": [
        {
          "name": "Lesson 1",
          "description": "Lesson description",
          "type": "dynamic",
          "blocks": [
            {
              "type": "text",
              "content": "# Hello World\n\nThis is a lesson."
            }
          ]
        }
      ]
    }
  ]
}
```

### Supported Activity Types

#### 1. Video Activity
```json
{
  "name": "Video Title",
  "type": "video",
  "video_subtype": "youtube",
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
  "document_subtype": "pdf",
  "document_url": "https://example.com/document.pdf"
}
```

#### 3. Dynamic Activity
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
    "grading_type": "PERCENTAGE",
    "tasks": [
      {
        "title": "Task Title",
        "description": "Task description",
        "hint": "Helpful hint",
        "assignment_type": "FILE_SUBMISSION",
        "max_grade_value": 50,
        "contents": {}
      }
    ]
  }
}
```

---

## Supported Block Types

### Text Blocks
```json
{
  "type": "text",
  "content": "# Heading\n\nParagraph text with **bold**, *italic*, and `code` formatting."
}
```

Supports: Headings, Bold, Italic, Code, Bullet lists, Numbered lists

### Quiz Blocks
```json
{
  "type": "quiz",
  "questions": [
    {
      "question": "What is the capital of France?",
      "answers": [
        {"answer": "Paris", "correct": true},
        {"answer": "London", "correct": false}
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
    "alignment": "center"
  }
}
```

### Code Blocks
```json
{
  "type": "code_block",
  "content": {
    "code": "def hello():\n    print('Hello, World!')",
    "language": "python"
  }
}
```

### Video Blocks
```json
{
  "type": "video",
  "content": {
    "url": "path/to/video.mp4",
    "title": "Video Title"
  }
}
```

### Table Blocks
```json
{
  "type": "table",
  "content": {
    "headers": ["Column 1", "Column 2"],
    "rows": [
      ["Row 1 Col 1", "Row 1 Col 2"]
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
    "color": "blue"
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
    "style": "primary"
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
    "display": "block"
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
          }
        ]
      }
    ]
  }
}
```

---

## Performance

### Import Speed
- **Small course** (1-5 chapters): ~10-30 seconds
- **Medium course** (5-10 chapters): ~30-90 seconds
- **Large course** (10+ chapters): ~1-3 minutes

### Image Upload Performance
- **Sequential**: ~2-5 seconds per image
- **Parallel (3 workers)**: ~2-5 seconds for 3 images
- **Speedup**: Up to 3x faster

---

## Troubleshooting

### Authentication Failed
```
❌ Authentication failed: Invalid credentials
💡 Tip: Verify your email and password are correct
```

**Solution:** Check your credentials

### Network Error
```
❌ Network error: Network request failed after 3 retries
💡 Tip: Check your internet connection and API server status
```

**Solution:** Verify API server is running and accessible

### Permission Error
```
❌ Failed to create course: No permission to create courses
💡 Tip: Verify you have admin access to organization 1
```

**Solution:** Check user permissions in the organization

### Image Upload Failed
```
⚠️ Failed to download image: HTTP 404
```

**Solution:** Image URL is broken - will fallback to URL

### Pre-flight Check Failed
```
❌ Pre-flight checks failed:
   • Organization 5 not found

💡 Tip: Fix the issues above or use --skip-preflight to bypass checks
```

**Solution:** Fix the organization ID or skip checks

### Common Issues

1. **"Missing required field"**: Check the schema for required fields
2. **"Invalid activity type"**: Must be one of: `video`, `document`, `dynamic`, `assignment`
3. **"Invalid block type"**: Check the list of supported block types above
4. **"Login failed"**: Verify API URL and credentials

---

## Best Practices

### 1. Always Validate First
```bash
python importer.py validate course.json
```

### 2. Use Dry-Run for Testing
```bash
python importer.py import course.json --dry-run
```

### 3. Enable Verbose for Debugging
```bash
python importer.py import course.json --verbose
```

### 4. Use Templates for New Courses
```bash
python importer.py init-course --output my-course.json
```

### 5. Check Pre-flight Before Large Imports
Pre-flight checks are enabled by default and catch issues early.

---

## Files in This Directory

- `course-schema.json` - JSON schema definition for course data structure
- `importer.py` - CLI tool with all commands
- `courses/` - Course data examples and documentation
- `organisation/` - Organization data examples
- `videos/` - Marketing video examples

---

## Schema Validation

The validator uses JSON Schema Draft 7. It checks:
- Required fields
- Data types
- Enum values
- String lengths
- Array constraints
- Custom business rules

---

## API Requirements

- LearnHouse API must be running
- Valid admin credentials
- Organization must exist
- User must have permission to create courses

---

## Notes

- All dates should be in ISO 8601 format (e.g., `2024-12-31T23:59:59Z`)
- URLs should be absolute and accessible
- Images and documents are automatically uploaded to the server
- The importer automatically converts markdown to Tiptap format
- Quiz questions support multiple choice only (for now)

---

## Quick Command Reference

```bash
# Generate templates
python importer.py init-course
python importer.py init-org

# Validate
python importer.py validate course.json

# Import
python importer.py import course.json --email EMAIL --password PASS

# Import with options
python importer.py import course.json \
  --email EMAIL \
  --password PASS \
  --verbose \
  --dry-run

# Complete workflow
python importer.py publish course.json --email EMAIL --password PASS
```

---

**Part of the LearnHouse project**
