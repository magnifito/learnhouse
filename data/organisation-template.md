# Organization Generation Template

You are an expert educational platform administrator. Your task is to generate a comprehensive organization definition for a learning platform based on the provided organization details and parameters.

**Organization Name:** {{name}}
**Purpose:** {{purpose}}
**Industry:** {{industry}}
**Language:** {{language}}

---

## Output Format

Please provide the output in the following JSON format:

```json
{
  "name": "Organization Name",
  "description": "Short description (max 500 chars)",
  "about": "Detailed organization overview (markdown supported)",
  "slug": "organization-slug",
  "email": "contact@organization.com",
  "label": "Organization Label",
  "default_locale": "en",
  "supported_locales": ["en"],
  "explore": false,
  "logo_image": "https://example.com/logo.png",
  "thumbnail_image": "https://example.com/thumbnail.png",
  "socials": {
    "twitter": "https://twitter.com/org",
    "linkedin": "https://linkedin.com/company/org",
    "facebook": "https://facebook.com/org",
    "youtube": "https://youtube.com/@org",
    "instagram": "https://instagram.com/org",
    "github": "https://github.com/org"
  },
  "links": {
    "website": "https://organization.com",
    "blog": "https://blog.organization.com",
    "support": "https://support.organization.com",
    "privacy": "https://organization.com/privacy",
    "terms": "https://organization.com/terms"
  },
  "scripts": {
    "head": "<script>/* Custom head scripts */</script>",
    "body": "<script>/* Custom body scripts */</script>"
  },
  "previews": {
    "primary": "https://example.com/preview1.jpg",
    "secondary": "https://example.com/preview2.jpg"
  },
  "config": {
    "config_version": "1.3",
    "general": {
      "enabled": true,
      "color": "normal",
      "watermark": true
    },
    "features": {
      "courses": {
        "enabled": true,
        "limit": 10
      },
      "members": {
        "enabled": true,
        "signup_mode": "open",
        "admin_limit": 1,
        "limit": 10
      },
      "usergroups": {
        "enabled": true,
        "limit": 10
      },
      "storage": {
        "enabled": true,
        "limit": 10
      },
      "ai": {
        "enabled": true,
        "limit": 10,
        "model": "gpt-4o-mini"
      },
      "assignments": {
        "enabled": false,
        "limit": 10
      },
      "payments": {
        "enabled": true
      },
      "discussions": {
        "enabled": true,
        "limit": 10
      },
      "analytics": {
        "enabled": true,
        "limit": 10
      },
      "collaboration": {
        "enabled": true,
        "limit": 10
      },
      "api": {
        "enabled": true,
        "limit": 10
      }
    },
    "cloud": {
      "plan": "free",
      "custom_domain": false
    },
    "landing": {}
  }
}
```

## Field Descriptions

### Required Fields

1. **name** (string, required)
   - The full name of the organization
   - Example: "Acme Learning Academy"

2. **slug** (string, required)
   - URL-friendly identifier for the organization
   - Must be unique, lowercase, alphanumeric with hyphens
   - Example: "acme-learning-academy"

3. **email** (string, required)
   - Primary contact email for the organization
   - Must be a valid email address
   - Example: "contact@acme-learning.com"

### Optional Basic Information

4. **description** (string, optional, max 500 chars)
   - Short description shown in listings and previews
   - Keep it concise and compelling
   - Example: "Professional training for marketing and sales teams"

5. **about** (string, optional)
   - Detailed organization overview
   - Supports markdown formatting
   - Can include multiple paragraphs, lists, links
   - Example: "Acme Learning Academy provides comprehensive training..."

6. **label** (string, optional)
   - Short label or tagline for the organization
   - Used in UI displays
   - Example: "Learn. Grow. Succeed."

7. **default_locale** (string, optional, default: "en")
   - Default language/locale code (ISO 639-1 format)
   - Examples: "en", "es", "fr", "de", "bg"

8. **supported_locales** (array, optional, default: ["en"])
   - List of language codes the organization supports
   - Example: ["en", "es", "fr"]

9. **explore** (boolean, optional, default: false)
   - Whether the organization should be discoverable in public explore
   - Set to `true` for public organizations

### Media Assets

10. **logo_image** (string, optional)
    - URL to the organization's logo image
    - Should be square or rectangular, high quality
    - Recommended: PNG with transparent background
    - Example: "https://example.com/logo.png"

11. **thumbnail_image** (string, optional)
    - URL to thumbnail/preview image
    - Used in cards and previews
    - Recommended: 16:9 aspect ratio
    - Example: "https://example.com/thumbnail.jpg"

12. **previews** (object, optional)
    - Additional preview images
    - `primary`: Main preview image
    - `secondary`: Secondary preview image
    - Example: `{"primary": "https://example.com/preview1.jpg", "secondary": "https://example.com/preview2.jpg"}`

### Social Media & Links

13. **socials** (object, optional)
    - Social media profile URLs
    - Supported keys: `twitter`, `linkedin`, `facebook`, `youtube`, `instagram`, `github`
    - Only include platforms the organization uses
    - Example: `{"twitter": "https://twitter.com/acme", "linkedin": "https://linkedin.com/company/acme"}`

14. **links** (object, optional)
    - Important organization links
    - Supported keys: `website`, `blog`, `support`, `privacy`, `terms`
    - Example: `{"website": "https://acme-learning.com", "support": "https://support.acme-learning.com"}`

### Advanced

15. **scripts** (object, optional)
    - Custom JavaScript code to inject
    - `head`: Scripts for `<head>` section
    - `body`: Scripts for `<body>` section
    - Use for analytics, custom tracking, etc.
    - Example: `{"head": "<script>/* analytics */</script>"}`

### Configuration

16. **config** (object, optional)
    - Organization feature configuration
    - **config_version**: Schema version (currently "1.3")
    - **general**: General settings
      - `enabled`: Whether organization is active
      - `color`: Theme color ("normal", "blue", "green", etc.)
      - `watermark`: Show watermark on content
    - **features**: Feature toggles and limits
      - Each feature has `enabled` (boolean) and `limit` (integer)
      - `members.signup_mode`: "open" or "inviteOnly"
      - `ai.model`: AI model to use (e.g., "gpt-4o-mini")
    - **cloud**: Cloud/plan settings
      - `plan`: "free", "standard", or "pro"
      - `custom_domain`: Whether custom domain is enabled
    - **landing**: Landing page customizations (object)

## Instructions

1. **Name & Slug**: Create a clear organization name and URL-friendly slug
2. **Description**: Write a compelling short description (max 500 chars)
3. **About**: Provide detailed markdown overview of the organization
4. **Contact**: Include valid email address
5. **Localization**: Set default and supported locales
6. **Media**: Provide logo and thumbnail URLs (or use placeholder URLs)
7. **Socials**: Include relevant social media profiles
8. **Links**: Add important website links
9. **Config**: Configure features based on organization needs
10. **Explore**: Set `explore: true` if organization should be publicly discoverable

---

**Generate the JSON now.**

