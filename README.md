# 半山笔记

个人博客，托管于 GitHub Pages：**https://xiiannwiki945.github.io/**

一套纯静态站点：零框架、零构建依赖、零后端。所有页面、样式、脚本都在仓库里，改完 push 即上线。

## 特性

- **深色模式**：跟随系统 + 右上角手动切换，切换不闪白
- **站内搜索**：`assets/search-index.js` 本地索引，纯前端检索，查询不出本机
- **文章目录**：右侧吸顶目录，滚动时高亮当前小节；窄屏自动移到正文上方
- **RSS**：`feed.xml`，换域名时改里面的绝对链接即可
- **SEO**：每页带 canonical / Open Graph / twitter card
- **响应式**：移动端单列布局，无横向滚动

## 目录结构

```
├── index.html                  # 首页（文章列表）
├── hugo-github-pages.html      # 文章
├── writing-workflow.html       # 文章
├── content-as-files.html       # 文章
├── tags.html / archive.html / about.html / search.html
├── feed.xml                    # RSS
└── assets/
    ├── style.css               # 全部样式（亮/暗两套变量）
    ├── app.js                  # 主题切换 / 目录高亮 / 搜索
    └── search-index.js         # 搜索索引（发新文章要更新）
```

## 发一篇新文章

1. 复制任意一个文章 html，改标题、日期、标签和正文
2. `index.html` 列表和 `archive.html` 里各加一条
3. `assets/search-index.js` 里加一条索引（title / url / date / tags / body）
4. `feed.xml` 里加一个 `<item>`
5. `git add -A && git commit -m "post: 标题" && git push`，Actions 构建约 1 分钟自动上线

## 部署

push 到 `main` 后由 `.github/workflows/pages.yml` 自动构建发布（GitHub Actions，Source 需设为 GitHub Actions）。

## 许可

文章内容版权归作者所有；样式与结构可自由取用。
