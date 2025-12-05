# LinkedIn HTML Structure Guide

## Common Post Container Patterns

LinkedIn uses several different HTML structures depending on the page type and feed version. Here are the most common patterns:

### 1. Company Page Posts (`/company/*/posts/`)

```html
<div class="feed-shared-update-v2" data-urn="urn:li:activity:1234567890">
  <div class="feed-shared-actor">
    <!-- Company name, logo -->
  </div>
  <div class="feed-shared-update-v2__description-wrapper">
    <div class="feed-shared-update-v2__description">
      <!-- Post text content here -->
    </div>
  </div>
  <div class="feed-shared-update-v2__content">
    <!-- Images, videos, links -->
  </div>
</div>
```

**Key Identifier:** `data-urn="urn:li:activity:*"`

### 2. User Activity Feed (`/in/*/activity/`)

```html
<li class="profile-creator-shared-feed-update__container">
  <div class="occludable-update" data-id="urn:li:activity:1234567890">
    <div class="feed-shared-actor">
      <!-- User info -->
    </div>
    <div class="feed-shared-update-v2__description">
      <!-- Post content -->
    </div>
  </div>
</li>
```

**Key Identifier:** `data-id="urn:li:activity:*"` or parent `<li>` with specific class

### 3. Feed Posts (General)

```html
<div class="feed-shared-update-v2 feed-shared-update-v2--minimal-padding" 
     data-urn="urn:li:activity:1234567890">
  <!-- Post content -->
</div>
```

## Unique Identifiers

### URN (Uniform Resource Name)

LinkedIn uses URNs to uniquely identify posts:

- Format: `urn:li:activity:1234567890123456789`
- Found in: `data-urn` or `data-id` attributes
- **Most reliable** way to distinguish posts

### Example URN Attributes

```html
data-urn="urn:li:activity:7123456789012345678"
data-id="urn:li:activity:7123456789012345678"
data-occludable-job-id="urn:li:activity:7123456789012345678"
```

## Content Selectors

### Post Text/Description

1. Primary: `.feed-shared-update-v2__description`
2. Wrapper: `.feed-shared-update-v2__description-wrapper`
3. Alternative: `.update-components-text`
4. Commentary: `.feed-shared-update-v2__commentary`

### Post Author/Actor

- `.feed-shared-actor`
- `.update-components-actor`

### Post Timestamp

- `time` element
- `.update-components-actor__sub-description`
- Often contains relative time like "2d ago"

## Nested Structure Issues

### Problem: Multiple Matches

Some selectors like `[class*="feed-shared-update-v2"]` may match:
1. The main post container
2. Nested elements within posts (e.g., shared posts, quoted posts)

### Solution: Use Most Specific Selector

```javascript
// Best - uses unique URN
'[data-urn*="urn:li:activity"]'

// Good - specific class
'div.feed-shared-update-v2'

// Avoid - too broad
'[class*="feed-shared"]'
```

## Repost Detection

### Repost Indicators

```html
<!-- Reposted content has this structure -->
<div class="feed-shared-actor">
  <span>
    <span>John Doe</span> reposted this
  </span>
</div>
```

**Text pattern:** "reposted this" near the beginning of the post

## Special Cases

### 1. Image Posts

May have minimal text in description, main content in image caption

### 2. Shared/Quoted Posts

Contains nested `feed-shared-update-v2` structures

### 3. Polls

Special structure with `.feed-shared-poll`

### 4. Documents/PDFs

Uses `.feed-shared-document`

## Best Practices for Scraping

1. **Use URN attributes** as the primary identifier
2. **Check for `data-urn` or `data-id`** to ensure unique posts
3. **Target specific classes** like `div.feed-shared-update-v2` (not wildcards)
4. **Avoid selecting nested elements** by checking parent structure
5. **Deduplicate by URN** before processing content

## Debug Commands

### Inspect Post Containers in Browser Console

```javascript
// Find all posts with URNs
document.querySelectorAll('[data-urn*="urn:li:activity"]')

// Find posts by class
document.querySelectorAll('div.feed-shared-update-v2')

// Get URNs of all posts
Array.from(document.querySelectorAll('[data-urn*="urn:li:activity"]'))
  .map(el => el.getAttribute('data-urn'))
```

### Check for Duplicates

```javascript
// Count posts
console.log('Posts found:', document.querySelectorAll('[data-urn*="urn:li:activity"]').length)

// Get unique URNs
const urns = Array.from(document.querySelectorAll('[data-urn*="urn:li:activity"]'))
  .map(el => el.getAttribute('data-urn'))
console.log('Unique URNs:', new Set(urns).size)
```

## Version Differences

LinkedIn occasionally updates their HTML structure. Common variations:

- `feed-shared-update-v2` (current)
- `occludable-update` (older)
- `profile-creator-shared-feed-update__container` (user profiles)

Always use multiple fallback selectors to handle different versions.

