# Blog

A static blog for GitHub Pages. No build tools, no frameworks — just HTML, CSS, and a small JS file.

## How it works

1. Drop an HTML file into `posts/`
2. Push to `main`
3. A GitHub Action scans the posts and regenerates `posts.json`
4. The landing page reads `posts.json` and renders the post list

## Post format

Each post is a standalone HTML file. Include these meta tags so the index can pick them up:

```html
<meta name="date" content="YYYY-MM-DD">
<meta name="category" content="your-category">
<meta name="description" content="A short summary.">
<title>Your Post Title</title>
<link rel="stylesheet" href="post.css">
```

File naming convention: `YYYY-MM-DD-slug-title.html`

## Local preview

```
python3 -m http.server
```

Then open `http://localhost:8000`.

## Structure

```
index.html          Landing page
style.css           Landing page styles
app.js              Reads posts.json, renders post list
posts.json          Auto-generated post manifest
posts/              Blog posts and shared post stylesheet
  post.css          Shared styles for posts
  *.html            Individual posts
.github/workflows/  GitHub Action to regenerate posts.json
```
