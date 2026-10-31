# 代码与日子

写编程，也写生活的个人博客，发布在 GitHub Pages（Jekyll 部署，不用手动加工作流）。

## 怎么发新文章（不用写代码）

1. 在 GitHub 网页上打开这个仓库，进入 `_posts/` 文件夹。
2. 点 **Add file → Create new file**。
3. 文件名按这个格式写：`年-月-日-英文代号.md`，例如 `2026-11-02-my-new-post.md`。
4. 把下面这段复制到文件开头，再往下写正文（Markdown 格式）：

```markdown
---
title: "文章标题"
date: 2026-11-02
category: 编程
excerpt: "一句话简介，会显示在首页卡片上。"
minutes: "约 4 分钟"
---

正文从这里开始。

## 小标题这样写

正文、列表、引用都用 Markdown 写。
```

`category` 只能写 `编程` 或 `生活`，这样首页筛选才分得开。
`image` 是可选的，有配图时再加一行，例如 `image: /assets/images/desk.webp`。

5. 点 **Commit changes** 提交。等 1–2 分钟，GitHub Pages 会自动用 Jekyll 重新生成网站，首页和归档里就会出现这篇文章。

## 改文章、删文章

- 改文章：在 `_posts/` 里打开那篇文章，点铅笔图标编辑，提交即可。
- 删文章：在文章页面点右上角 `...` → Delete file，提交即可。

## 本地文件说明

- `_posts/`：所有文章的 Markdown 文件。
- `_layouts/`：页面模板（首页和文章页共用同一套样式）。
- `assets/style.css`：博客样式，`assets/images/`：配图。
- `index.html`：首页，自动列出 `_posts/` 里的文章。
