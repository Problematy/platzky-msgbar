# b4uLeave Plugin

## Overview

The msgbar plugin displays a message bar above the whole page with support for Markdown formatting and built-in XSS protection.

## Installation

```sh
pip install platzky-msgbar
```

## Usage

```json
"plugins": [
    {
        "name": "msgbar",
        "config": {
            "message": "Your custom message goes here"
        }
    }
]
```

### Markdown Support

The message field supports Markdown formatting including links:

```json
{
    "message": "Visit [our website](https://example.com) for more info!"
}
```

You can also use link attributes:

```json
{
    "message": "[Click here](https://example.com){:target=\"_blank\" rel=\"noopener\"}"
}
```

If you omit `message`, it defaults to:

```
This is a default notification message.
```

## Security

The plugin automatically sanitizes all message content to prevent XSS attacks:

- Only safe HTML tags are allowed: `a`, `strong`, `em`, `b`, `i`, `code`, `br`, `span`
- Dangerous content like `<script>` tags, `javascript:` URLs, and event handlers are stripped
- Links are restricted to safe protocols: `http`, `https`, `mailto`

This protection is always active and cannot be disabled.