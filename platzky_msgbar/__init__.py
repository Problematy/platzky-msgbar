"""
Platzky msgbar plugin - displays a customizable message bar at the top of web pages.

This plugin injects HTML/CSS into Flask responses to show a fixed notification bar
with markdown support, custom styling, and XSS/CSS injection protection.
"""

from platzky_msgbar.entrypoint import process as process
