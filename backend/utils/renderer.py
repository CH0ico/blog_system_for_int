#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown rendering helpers with sanitization.
"""

import markdown2
import bleach

# Allow basic formatting, code blocks, tables and images.
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'p', 'pre', 'code', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'ul', 'ol', 'li', 'br', 'hr', 'table', 'thead', 'tbody',
    'tr', 'th', 'td', 'img'
]
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'span': ['class'],
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
}
ALLOWED_PROTOCOLS = list(bleach.sanitizer.ALLOWED_PROTOCOLS) + ['data']


def render_markdown(content: str) -> str:
    """Convert Markdown to sanitized HTML."""
    if not content:
        return ''

    html = markdown2.markdown(
        content,
        extras=[
            'fenced-code-blocks',
            'tables',
            'strike',
            'cuddled-lists',
            'code-friendly',
            'break-on-newline',
            'header-ids',
            'spoiler',
        ],
    )
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return cleaned
