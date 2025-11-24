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

The `message` field is required. If you don't provide it, the plugin configuration will fail validation.

## Security

The plugin implements comprehensive security measures to protect against injection attacks:

### XSS Protection
- Only safe HTML tags are allowed: `a`, `strong`, `em`, `b`, `i`, `code`, `br`, `span`
- Dangerous content like `<script>` tags, `javascript:` URLs, and event handlers are stripped
- Links are restricted to safe protocols: `http`, `https`, `mailto`

### CSS Injection Protection
- All CSS configuration values (colors, sizes, fonts) are validated using Pydantic
- Colors must be valid hex, rgb/rgba, hsl/hsla, or named colors
- Sizes must follow the pattern: `number + unit` (px, em, rem, %, vh, vw)
- Font families cannot contain dangerous characters or CSS functions like `url()`
- Invalid values are automatically rejected and replaced with safe defaults

All security protections are always active and cannot be disabled.