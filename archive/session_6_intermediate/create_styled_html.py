#!/usr/bin/env python3
"""Create styled HTML with embedded charts from markdown"""

import markdown
import base64
from pathlib import Path

# Read markdown
with open('Taking_Profits_What_Actually_Works.md', 'r') as f:
    md_content = f.read()

# Convert markdown to HTML
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# HTML template with professional styling
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taking Profits: What Actually Works</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 40px;
            background-color: #fff;
            font-size: 16px;
        }}

        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-top: 0.5em;
            margin-bottom: 0.3em;
            line-height: 1.2;
            color: #1a1a1a;
        }}

        h2 {{
            font-size: 1.8em;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            padding-bottom: 0.3em;
            border-bottom: 2px solid #e1e4e8;
            color: #1a1a1a;
        }}

        h3 {{
            font-size: 1.3em;
            font-weight: 600;
            margin-top: 1.2em;
            margin-bottom: 0.5em;
            color: #2a2a2a;
        }}

        p {{
            margin: 1em 0;
            font-size: 16px;
        }}

        strong {{
            font-weight: 600;
            color: #000;
        }}

        em {{
            font-style: italic;
        }}

        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}

        li {{
            margin: 0.5em 0;
        }}

        hr {{
            border: none;
            border-top: 1px solid #e1e4e8;
            margin: 2em 0;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            font-size: 14px;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        code {{
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.9em;
        }}

        @media print {{
            body {{
                max-width: 100%;
                font-size: 12pt;
            }}

            img {{
                max-width: 90%;
                page-break-inside: avoid;
            }}

            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 15px 20px;
                font-size: 15px;
            }}

            h1 {{
                font-size: 2em;
            }}

            h2 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>'''

# Write HTML
with open('Taking_Profits_What_Actually_Works.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ Created styled HTML: Taking_Profits_What_Actually_Works.html")
print(f"📄 File size: {len(html_template) / 1024:.1f} KB")
