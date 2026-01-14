# Rich Email Formatting Guide for Graph Mail MCP Server

This guide helps AI assistants create professional, well-formatted emails using the Microsoft Graph API through the MCP server.

## Table of Contents
1. [Content Types](#content-types)
2. [HTML Formatting](#html-formatting)
3. [Common Patterns](#common-patterns)
4. [Best Practices](#best-practices)
5. [Examples](#examples)

## Content Types

### Text vs HTML
- **`text`**: Plain text only. Use `\n` for line breaks. No formatting support.
- **`html`**: Rich formatting with HTML tags. **Recommended for professional emails.**

**Important**: When using `html` content type, `\n` characters are ignored. Use `<br>` or `<p>` tags for line breaks.

## HTML Formatting

### Basic Text Formatting
```html
<b>Bold text</b> or <strong>Bold text</strong>
<i>Italic text</i> or <em>Italic text</em>
<u>Underlined text</u>
<span style="color: #0066cc;">Colored text</span>
<span style="font-size: 16px;">Sized text</span>
```

### Line Breaks and Paragraphs
```html
Line 1<br>Line 2                    <!-- Single line break -->
<p>Paragraph 1</p>
<p>Paragraph 2</p>                  <!-- Paragraphs with spacing -->
```

### Lists
```html
<!-- Unordered (bulleted) list -->
<ul>
  <li>First item</li>
  <li>Second item</li>
  <li>Third item</li>
</ul>

<!-- Ordered (numbered) list -->
<ol>
  <li>Step 1</li>
  <li>Step 2</li>
  <li>Step 3</li>
</ol>
```

### Links
```html
<a href="https://example.com">Click here</a>
<a href="mailto:user@example.com">Email us</a>
```

### Tables
Use tables for structured data and layout:
```html
<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Header 1</th>
    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Header 2</th>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">Data 1</td>
    <td style="border: 1px solid #ddd; padding: 8px;">Data 2</td>
  </tr>
</table>
```

### Headings
```html
<h1>Main Heading</h1>
<h2>Subheading</h2>
<h3>Minor Heading</h3>
```

### Horizontal Lines
```html
<hr>  <!-- Horizontal rule / separator -->
```

## Common Patterns

### Professional Email Structure
```html
<p>Dear [Name],</p>

<p>I hope this email finds you well.</p>

<p>[Main content paragraph 1]</p>

<p>[Main content paragraph 2]</p>

<p>Best regards,<br>
[Your Name]</p>
```

### Email with Bullet Points
```html
<p>Hello [Name],</p>

<p>Here are the key points from our discussion:</p>

<ul>
  <li>Point 1: Description</li>
  <li>Point 2: Description</li>
  <li>Point 3: Description</li>
</ul>

<p>Please let me know if you have any questions.</p>

<p>Best regards,<br>[Your Name]</p>
```

### Action Items or Steps
```html
<p>Hi [Name],</p>

<p>To complete the setup, please follow these steps:</p>

<ol>
  <li>Download the attachment</li>
  <li>Run the installation wizard</li>
  <li>Restart your computer</li>
  <li>Verify the installation</li>
</ol>

<p>Let me know if you encounter any issues.</p>

<p>Thanks,<br>[Your Name]</p>
```

### Meeting Summary
```html
<p>Hi Team,</p>

<p>Here's a summary of today's meeting:</p>

<table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px; width: 30%; font-weight: bold;">Topic</td>
    <td style="border: 1px solid #ddd; padding: 8px;">Project Timeline</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Decision</td>
    <td style="border: 1px solid #ddd; padding: 8px;">Move launch to Q2</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Action Items</td>
    <td style="border: 1px solid #ddd; padding: 8px;">
      <ul style="margin: 0; padding-left: 20px;">
        <li>Update project plan - John</li>
        <li>Notify stakeholders - Sarah</li>
      </ul>
    </td>
  </tr>
</table>

<p>Next meeting: [Date and Time]</p>

<p>Best,<br>[Your Name]</p>
```

### Signature Block
```html
<p>Best regards,</p>

<table style="font-family: Arial, sans-serif; font-size: 12px;">
  <tr>
    <td style="padding-right: 15px; border-right: 2px solid #0066cc;">
      <strong style="font-size: 14px; color: #0066cc;">[Your Name]</strong><br>
      <span style="color: #666;">[Your Title]</span><br>
      <span style="color: #666;">[Company Name]</span>
    </td>
    <td style="padding-left: 15px;">
      <span style="color: #666;">📧 [email@company.com]</span><br>
      <span style="color: #666;">📱 [Phone Number]</span><br>
      <span style="color: #666;">🌐 <a href="https://company.com">company.com</a></span>
    </td>
  </tr>
</table>
```

## Best Practices

### Inline CSS Only
❌ **Don't use**: `<style>` blocks or external stylesheets
```html
<!-- DON'T DO THIS -->
<style>
  .myclass { color: blue; }
</style>
<p class="myclass">Text</p>
```

✅ **Do use**: Inline styles
```html
<p style="color: blue;">Text</p>
```

### Email Client Compatibility
- **Use tables for layout** instead of modern CSS (flexbox, grid)
- **Avoid**: `position: absolute`, `float`, complex CSS
- **Test across clients**: Outlook, Gmail, mobile apps render differently
- **Keep it simple**: Simpler HTML = better compatibility

### Performance and Size
- Keep HTML reasonably sized (< 100KB recommended)
- Don't embed large images as base64 (use attachments instead)
- Minimize nested tables (max 3 levels deep)

### Accessibility
- Use semantic HTML (`<h1>`, `<p>`, `<ul>` instead of styled `<div>`)
- Provide alt text for images: `<img src="..." alt="Description">`
- Use sufficient color contrast
- Make links descriptive: "View the report" not "Click here"

## Examples

### Example 1: Simple Professional Email
```html
<p>Dear John,</p>

<p>Thank you for your inquiry about our services. I'd be happy to provide you with more information.</p>

<p>Our team specializes in:</p>
<ul>
  <li><b>Cloud Migration</b> - Seamless transition to Azure</li>
  <li><b>Security Audits</b> - Comprehensive vulnerability assessments</li>
  <li><b>24/7 Support</b> - Always available when you need us</li>
</ul>

<p>Would you be available for a call next week to discuss your specific needs?</p>

<p>Best regards,<br>
<b>Sarah Johnson</b><br>
Senior Solutions Architect</p>
```

### Example 2: Status Update with Table
```html
<p>Hi Team,</p>

<p>Here's this week's project status update:</p>

<table style="border-collapse: collapse; width: 100%; margin: 15px 0;">
  <tr style="background-color: #f2f2f2;">
    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Component</th>
    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Status</th>
    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Owner</th>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 10px;">Frontend</td>
    <td style="border: 1px solid #ddd; padding: 10px; color: #28a745;">✓ Complete</td>
    <td style="border: 1px solid #ddd; padding: 10px;">Alice</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 10px;">Backend API</td>
    <td style="border: 1px solid #ddd; padding: 10px; color: #ffc107;">⚠ In Progress</td>
    <td style="border: 1px solid #ddd; padding: 10px;">Bob</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 10px;">Testing</td>
    <td style="border: 1px solid #ddd; padding: 10px; color: #dc3545;">✗ Not Started</td>
    <td style="border: 1px solid #ddd; padding: 10px;">Carol</td>
  </tr>
</table>

<p>Overall, we're on track for the Q1 deadline. Let me know if you have questions.</p>

<p>Thanks,<br>Project Manager</p>
```

### Example 3: Event Invitation
```html
<h2 style="color: #0066cc;">You're Invited!</h2>

<p>Hello,</p>

<p>We're excited to invite you to our upcoming webinar:</p>

<table style="background-color: #f9f9f9; padding: 20px; margin: 15px 0; width: 100%; border-left: 4px solid #0066cc;">
  <tr>
    <td>
      <p style="margin: 0 0 10px 0;"><b style="font-size: 18px;">Building Scalable Cloud Applications</b></p>
      <p style="margin: 5px 0;"><b>📅 Date:</b> March 15, 2024</p>
      <p style="margin: 5px 0;"><b>⏰ Time:</b> 2:00 PM - 3:30 PM EST</p>
      <p style="margin: 5px 0;"><b>📍 Location:</b> Virtual (Zoom link will be sent)</p>
      <p style="margin: 5px 0;"><b>🎤 Speaker:</b> Dr. Jane Smith, Cloud Architect</p>
    </td>
  </tr>
</table>

<p><b>What you'll learn:</b></p>
<ul>
  <li>Design patterns for cloud-native applications</li>
  <li>Best practices for microservices architecture</li>
  <li>Cost optimization strategies</li>
</ul>

<p>
  <a href="https://example.com/register" style="display: inline-block; padding: 12px 30px; background-color: #0066cc; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Register Now</a>
</p>

<p>Limited spots available. Register early to secure your seat!</p>

<p>See you there,<br>The Events Team</p>
```

## Quick Reference Card

| Want to... | Use this HTML |
|------------|---------------|
| Bold text | `<b>text</b>` or `<strong>text</strong>` |
| Italic text | `<i>text</i>` or `<em>text</em>` |
| Line break | `<br>` |
| New paragraph | `<p>text</p>` |
| Bullet list | `<ul><li>item</li></ul>` |
| Numbered list | `<ol><li>item</li></ol>` |
| Link | `<a href="url">text</a>` |
| Colored text | `<span style="color: #0066cc;">text</span>` |
| Heading | `<h2>Heading</h2>` |
| Horizontal line | `<hr>` |
| Table | `<table><tr><td>cell</td></tr></table>` |

## AI Assistant Guidelines

When creating email drafts:

1. **Always use HTML format** (`body_type: "html"`) for professional emails
2. **Structure emails properly** with greetings, body, and closing
3. **Use appropriate formatting**:
   - Lists for multiple items
   - Tables for structured data
   - Bold/italic for emphasis
   - Headings for sections
4. **Keep emails concise** but well-formatted
5. **Test for readability** - avoid over-formatting
6. **Include proper spacing** between paragraphs (`<p>` tags)
7. **Use professional signatures** when appropriate

Remember: Well-formatted emails create better impressions and improve communication effectiveness!
