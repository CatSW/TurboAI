---
title: skill-markdown-encapsulation
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
description: "Previene il troncamento dell'output markdown tramite la regola dell'envelope a 10 backtick"
version: 1.2.0
audience: LLM
mode: Channel C
---

# Robust Markdown Emission (10-Backtick Rule)

When requested to output, generate, or modify any Markdown document that contains internal code blocks, data structures, or diagrams (such as JSON, XML, YAML, or Mermaid), you must **prevent UI parser truncation**:
1. Always encapsulate the entire generated Markdown output inside a strict outer fence of exactly 10 backticks.
2. This ensures the chat UI renders a single continuous code block, allowing the user to safely and transparently use the standard "Copy" button.
