# b4uLeave Plugin

## Overview

The msgbar plugin displays a message bar above the whole page.

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

If you omit `message`, it defaults to:

```html
<p>'This is a default notification message.'</p>
```