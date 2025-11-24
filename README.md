# Msgbar Plugin

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

## Configuration Options

All styling fields are optional. If not provided, the plugin will use fallback values from your Platzky theme configuration or built-in defaults.

### Optional Styling Fields

- **`background_color`** (string): CSS color value for the bar background
  - Falls back to Platzky's `primary_color` from database
  - Default: `#245466`
  - Accepts: hex (#RGB, #RRGGBB), rgb/rgba, hsl/hsla, named colors

- **`text_color`** (string): CSS color value for the text
  - Falls back to Platzky's `secondary_color` from database
  - Default: `white`
  - Accepts: hex, rgb/rgba, hsl/hsla, named colors

- **`font_family`** (string): CSS font-family value
  - Falls back to Platzky's `font` from database
  - Default: `'Arial', sans-serif`
  - Max length: 200 characters

- **`font_size`** (string): CSS font-size value
  - Default: `14px`
  - Accepts: number + unit (px, em, rem, %, vh, vw)

- **`bar_height`** (string): Height of the message bar
  - Default: `30px`
  - Accepts: number + unit (px, em, rem, %, vh, vw)

### Complete Configuration Example

```json
"plugins": [
    {
        "name": "msgbar",
        "config": {
            "message": "Visit [our website](https://example.com) for more info!",
            "background_color": "#ff5733",
            "text_color": "#ffffff",
            "font_family": "'Courier New', monospace",
            "font_size": "16px",
            "bar_height": "40px"
        }
    }
]
```

### Platzky Theme Integration

If your Platzky configuration includes theme settings in `site_content`, the plugin will automatically use them:

```json
{
  "site_content": {
    "primary_color": "#123456",
    "secondary_color": "#abcdef",
    "font": "Roboto"
  }
}
```

This allows the message bar to match your site's overall theme without additional configuration.

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