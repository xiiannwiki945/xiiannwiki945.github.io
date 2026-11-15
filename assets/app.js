/* 半山笔记 — 交互脚本：主题切换 / 目录高亮 / 站内搜索 */

(function () {
  "use strict";

  var THEME_KEY = "banshan-theme";

  function getStoredTheme() {
    try {
      return window.localStorage.getItem(THEME_KEY);
    } catch (err) {
      return null;
    }
  }

  function storeTheme(value) {
    try {
      window.localStorage.setItem(THEME_KEY, value);
    } catch (err) {
      /* 隐私模式下忽略写入失败 */
    }
  }

  function systemTheme() {
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.setAttribute(
        "aria-label",
        theme === "dark" ? "切换到浅色模式" : "切换到深色模式"
      );
      toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }
  }

  var initial = getStoredTheme();
  applyTheme(initial === "dark" || initial === "light" ? initial : systemTheme());

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-theme-toggle]");
    if (!toggle) return;
    var next =
      document.documentElement.getAttribute("data-theme") === "dark"
        ? "light"
        : "dark";
    applyTheme(next);
    storeTheme(next);
  });

  /* ---------- 文章目录滚动高亮 ---------- */

  function initToc() {
    var links = Array.prototype.slice.call(
      document.querySelectorAll(".toc a[href^='#']")
    );
    if (!links.length || !("IntersectionObserver" in window)) return;

    var headings = links
      .map(function (link) {
        var id = link.getAttribute("href").slice(1);
        return document.getElementById(id);
      })
      .filter(Boolean);

    if (!headings.length) return;

    var setActive = function (id) {
      links.forEach(function (link) {
        link.classList.toggle(
          "is-active",
          link.getAttribute("href") === "#" + id
        );
      });
    };

    var observer = new IntersectionObserver(
      function (entries) {
        var visible = entries
          .filter(function (entry) {
            return entry.isIntersecting;
          })
          .sort(function (a, b) {
            return a.boundingClientRect.top - b.boundingClientRect.top;
          });
        if (visible.length) {
          setActive(visible[0].target.id);
        }
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 }
    );

    headings.forEach(function (heading) {
      observer.observe(heading);
    });
  }

  /* ---------- 站内搜索 ---------- */

  function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function highlightInto(target, text, terms) {
    if (!terms.length) {
      target.appendChild(document.createTextNode(text));
      return;
    }
    var pattern = new RegExp("(" + terms.map(escapeRegExp).join("|") + ")", "gi");
    var parts = text.split(pattern);
    parts.forEach(function (part, index) {
      if (!part) return;
      if (index % 2 === 1) {
        var mark = document.createElement("mark");
        mark.textContent = part;
        target.appendChild(mark);
      } else {
        target.appendChild(document.createTextNode(part));
      }
    });
  }

  function buildSnippet(post, terms) {
    var body = post.body || post.excerpt || "";
    var lower = body.toLowerCase();
    var index = -1;
    for (var i = 0; i < terms.length; i += 1) {
      var found = lower.indexOf(terms[i].toLowerCase());
      if (found !== -1 && (index === -1 || found < index)) {
        index = found;
      }
    }
    if (index === -1) {
      return body.slice(0, 96) + (body.length > 96 ? "…" : "");
    }
    var start = Math.max(0, index - 34);
    var end = Math.min(body.length, start + 116);
    return (start > 0 ? "…" : "") + body.slice(start, end) + (end < body.length ? "…" : "");
  }

  function initSearch() {
    var input = document.getElementById("search-input");
    var list = document.getElementById("search-results");
    var count = document.getElementById("search-count");
    var clear = document.getElementById("search-clear");
    if (!input || !list || !count) return;

    var posts = Array.isArray(window.POSTS) ? window.POSTS : [];

    var renderEmpty = function (message) {
      list.textContent = "";
      var p = document.createElement("p");
      p.className = "empty";
      p.textContent = message;
      list.appendChild(p);
    };

    var search = function () {
      var query = input.value.trim();
      if (clear) {
        clear.classList.toggle("is-visible", query.length > 0);
      }

      var terms = query ? query.split(/\s+/).filter(Boolean) : [];
      list.textContent = "";

      if (!terms.length) {
        count.textContent = "共 " + posts.length + " 篇，输入关键词开始检索";
        return;
      }

      var matches = posts.filter(function (post) {
        var haystack = (post.title + " " + post.tags.join(" ") + " " + post.body).toLowerCase();
        return terms.every(function (term) {
          return haystack.indexOf(term.toLowerCase()) !== -1;
        });
      });

      count.textContent = "找到 " + matches.length + " 篇";

      if (!matches.length) {
        renderEmpty("没有匹配的文章，换个关键词试试。");
        return;
      }

      matches.forEach(function (post) {
        var item = document.createElement("article");
        item.className = "result";

        var title = document.createElement("h2");
        var link = document.createElement("a");
        link.href = post.url;
        highlightInto(link, post.title, terms);
        title.appendChild(link);
        item.appendChild(title);

        var snippet = document.createElement("p");
        snippet.className = "snippet";
        highlightInto(snippet, buildSnippet(post, terms), terms);
        item.appendChild(snippet);

        var meta = document.createElement("div");
        meta.className = "meta-line";
        var date = document.createElement("span");
        date.textContent = post.date;
        meta.appendChild(date);
        post.tags.forEach(function (tag) {
          var tagSpan = document.createElement("span");
          tagSpan.textContent = "#" + tag;
          meta.appendChild(tagSpan);
        });
        item.appendChild(meta);

        list.appendChild(item);
      });
    };

    input.addEventListener("input", search);
    if (clear) {
      clear.addEventListener("click", function () {
        input.value = "";
        input.focus();
        search();
      });
    }

    var params = new URLSearchParams(window.location.search);
    var initialQuery = params.get("q");
    if (initialQuery) {
      input.value = initialQuery;
    }
    search();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initToc();
      initSearch();
    });
  } else {
    initToc();
    initSearch();
  }
})();
