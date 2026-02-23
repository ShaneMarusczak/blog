# Blog

A static blog for GitHub Pages. No build tools, no frameworks — just HTML, CSS, and a small JS file.

## How it works

1. Drop an HTML file into `posts/`
2. Add an entry to `posts.json`
3. Push to `main`
4. The landing page reads `posts.json` and renders the post list

## Adding a post

Create your HTML file in `posts/`, then add an entry to `posts.json`:

```json
{
  "file": "2026-02-23-your-post-slug.html",
  "title": "Your Post Title",
  "date": "2026-02-23",
  "category": "your-category",
  "description": "A short summary of the post."
}
```

## Post format

Each post is a standalone HTML file. Include these meta tags in the `<head>`:

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
index.html      Landing page
style.css       Landing page styles
app.js          Reads posts.json, renders post list
posts.json      Post manifest (update manually)
posts/
  post.css      Shared styles for posts
  *.html        Individual posts
```
