document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("posts");

  fetch("posts.json")
    .then((res) => {
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    })
    .then((posts) => {
      if (!posts.length) {
        container.innerHTML =
          '<p class="empty-state">No posts yet.</p>';
        return;
      }

      posts.sort((a, b) => b.date.localeCompare(a.date));

      const list = document.createElement("ul");
      list.className = "post-list";

      for (const post of posts) {
        const li = document.createElement("li");
        li.className = "post-item";

        const dateStr = formatDate(post.date);
        const category = post.category
          ? `<span class="dot">&middot;</span><span class="category">${escapeHtml(post.category)}</span>`
          : "";

        const link = document.createElement("a");
        link.href = "posts/" + encodeURIComponent(post.file);

        link.innerHTML =
          `<div class="post-title">${escapeHtml(post.title)}</div>` +
          `<div class="post-meta">${escapeHtml(dateStr)}${category}</div>` +
          (post.description ? `<div class="post-description">${escapeHtml(post.description)}</div>` : "");

        li.appendChild(link);
        list.appendChild(li);
      }

      container.innerHTML = "";
      container.appendChild(list);

      document.querySelectorAll(".post-item").forEach((item) => {
        item.addEventListener("mouseover", () => {
          item.classList.add("boxShadow");
        });
      });

      document.querySelectorAll(".post-item").forEach((item) => {
        item.addEventListener("mouseleave", () => {
          item.classList.remove("boxShadow");
        });
      });
    })
    .catch(() => {
      container.innerHTML =
        '<p class="error-state">Could not load posts. If running locally, use a local server:<br><code>python3 -m http.server</code></p>';
    });
});

function formatDate(dateStr) {
  if (!dateStr) return "";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr;
  const months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  const m = parseInt(parts[1], 10);
  if (m < 1 || m > 12) return dateStr;
  return `${months[m - 1]} ${parseInt(parts[2], 10)}, ${parts[0]}`;
}

function escapeHtml(str) {
  const el = document.createElement("span");
  el.textContent = str;
  return el.innerHTML;
}
