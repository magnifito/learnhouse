# Course Generation Template

You are an expert educational content creator. Your task is to generate a comprehensive course structure and content for a learning platform based on the provided topic and parameters.

**Topic:** {{topic}}
**Target Audience:** {{audience}}
**Tone:** {{tone}}
**Language:** {{language}}

---

## Output Format

Please provide the output in the following JSON format:

```json
{
  "name": "Course Title",
  "description": "Short description (max 150 chars)",
  "about": "Detailed course overview (markdown supported)",
  "learnings": "Key takeaways (bullet points)",
  "tags": "comma, separated, tags",
  "thumbnail_query": "search term for unsplash image",
  "chapters": [
    {
      "name": "Chapter 1 Title",
      "description": "Chapter description",
      "activities": [
        {
          "name": "Activity Title",
          "description": "Activity description",
          "type": "video",
          "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
          "blocks": [
             {
                "type": "text",
                "content": "Detailed explanation text..."
             },
             {
                "type": "quiz",
                "questions": [
                    {
                        "question": "Question text?",
                        "answers": [
                            {"answer": "Option A", "correct": true},
                            {"answer": "Option B", "correct": false}
                        ]
                    }
                ]
             }
          ]
        }
      ]
    }
  ]
}
```

## Instructions

1.  **Title & Description**: Create a catchy title and a concise description.
2.  **About**: Write a compelling overview of what the course covers.
3.  **Learnings**: List 3-5 key skills or concepts students will gain.
4.  **Tags**: Provide 3-5 relevant tags.
5.  **Thumbnail**: Suggest a search query for Unsplash to find a relevant cover image.
6.  **Structure**: Break the course down into 2-4 logical chapters.
7.  **Activities**: Each chapter should have 2-3 activities.
    -   **Video**: Use `video` type. Use placeholder `https://www.youtube.com/watch?v=dQw4w9WgXcQ`.
    -   **Quiz**: Include at least one `quiz` block in some activities.
8.  **Blocks**:
    -   `text`: detailed explanation.
    -   `quiz`: list of questions with answers (mark correct ones).

---

**Generate the JSON now.**
