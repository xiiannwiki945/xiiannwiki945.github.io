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
    │   └── search-index.js         # 搜索索引（脚本会自动加条目）
    └── scripts/
        └── new_post.py            # 发文助手：一条命令生成文章并同步全站
```

## 发一篇新文章（网页操作，无需本地环境）

仓库 → **Actions → New post → Run workflow**，填标题 / 文件名 / 标签 / 摘要，点运行。
工作流会自动生成文章骨架并同步首页、归档、搜索索引和 RSS。

运行完之后还差两步（都在网页编辑器里完成：仓库里打开文件，点铅笔图标编辑）：

1. 打开 `<slug>.html`，在 `prose` 区块写正文，补齐右侧目录链接
2. 打开 `assets/search-index.js`，把这条的 `body` 换成正文纯文本

每次编辑提交后 Actions 自动重新构建，约 1 分钟上线。

## 发一篇新文章（本地命令行）

用仓库自带的发文助手，一条命令生成文章并同步首页、归档、搜索索引和 RSS：

```bash
python3 scripts/new_post.py \
    --title "文章标题" \
    --slug my-post \
    --tags Hugo,随笔 \
    --excerpt "一句话摘要"
```

它会做四件事：生成 `my-post.html`（正文留了 TODO 占位）、在 `index.html` 和 `archive.html` 插入条目、
在 `assets/search-index.js` 加索引、在 `feed.xml` 加 RSS 项并更新发布时间。

剩下手动做的只有两步：

1. 打开 `my-post.html`，在 `prose` 区块里写正文；有小节就把 `<h2 id="sec-1">` 和右侧目录的
   `<a href="#sec-1">` 补上
2. 把 `assets/search-index.js` 里这条的 `body` 换成正文纯文本（搜索摘要取自这里）

然后：

```bash
git add -A && git commit -m "post: 文章标题" && git push
```

Actions 构建约 1 分钟自动上线。

## 图片和视频

统一放在 `media/日期-用途/` 文件夹里，例如 `media/20261115-screenshot/`。

上传（网页即可）：仓库页面 → **Add file → Upload files**，把文件拖进去 → Commit changes。

在文章 `prose` 区块里引用：

```html
<figure>
  <img src="media/20261115-screenshot/demo.png" alt="截图说明" loading="lazy">
  <figcaption>图注：这张图说明什么</figcaption>
</figure>
```

视频用 `<video>` 标签（推荐 MP4，单个文件别超过 50MB，仓库总大小建议控制在 1GB 内）：

```html
<video controls preload="metadata" src="media/20261115-demo/clip.mp4" style="width:100%;border-radius:4px;"></video>
```

更长的视频建议传 YouTube 后嵌入（占位小、不占仓库、播放由 YouTube 承担）：

```html
<iframe src="https://www.youtube.com/embed/视频ID"
        title="视频标题" loading="lazy"
        style="width:100%;aspect-ratio:16/9;border:0;border-radius:4px;"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen></iframe>
```

视频 ID 就是链接 `youtube.com/watch?v=**dQw4w9WgXcQ**` 里 `v=` 后面那一段（11 位）。
建议上传时把可见性设为「不公开（Unlisted）」——只有拿到嵌入链接的人能看，不上推荐、不出现在频道页。

图片建议先压缩再传（每张 500KB 内），页面加载快很多。

## 部署


push 到 `main` 后由 `.github/workflows/pages.yml` 自动构建发布（GitHub Actions，Source 需设为 GitHub Actions）。

## 许可

文章内容版权归作者所有；样式与结构可自由取用。
