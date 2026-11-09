---
title: "博客又加了两样东西：匿名评论，和一个免费域名"
date: 2026-11-09
category: 编程
excerpt: "评论不用 GitHub 账号也能留了；另外申请了 nickxu.eu.org，等批复后博客就能换上自己的域名。"
minutes: "约 5 分钟"
---

博客上线一周多，陆续补了两样东西：评论区，和一个属于自己的域名。两件事都不大，但都踩了点坑，记下来。

## 一、评论：从 Giscus 换成 Waline

博客一开始装的是 Giscus，评论存在 GitHub Discussions 里。装好就能用，但有个问题：留言必须用 GitHub 账号登录，没有 GitHub 账号的人留不了言。

所以换成了 Waline。现在文章底下的评论框只填昵称就能留，匿名也可以。Waline 部署在 Vercel 上，数据存在 Neon 的 Postgres 数据库里，评论管理在它自己的后台。

换的过程中踩了一个坑，值得单独说：Vercel 新项目默认开了部署保护（Deployment Protection），匿名访问会返回 401。也就是说，评论框在我自己登录着的浏览器里看着一切正常，但外面的人既留不了言，阅读数也计不上。关掉保护之后，匿名请求才真正通了。

教训很简单：部署完一个对外的服务，一定要用没登录的请求验一遍，不能只看自己浏览器里的效果。

## 二、域名：申请了 nickxu.eu.org

真正免费的顶级域名基本已经没了。Freenom 当年那批 .tk、.ml 免费域名，2023 年就停了免费注册。剩下的免费选择，都是二级域名。

我选了 EU.org：一个从 1996 年做到现在的非营利组织，免费、没有有效期，域名用自己的名字注册，DNS 自己管。比起借来的 github.io 地址，它更像自己的东西，换托管也不用换地址。

申请过程有一点绕：EU.org 不接受 Gmail 做验证邮箱，所以先注册了一个 Outlook 邮箱 nickxuu@outlook.com 专门用来收验证邮件。联系人建好之后，在 Cloudflare 上加了 nickxu.eu.org 站点，拿到的 NS 是 kyle.ns.cloudflare.com 和 meadow.ns.cloudflare.com，申请号 20261108171145-arf-40387，NS 检查都通过了。

现在的状态是等人工审核，几天到几周，批了会发邮件到 Outlook 邮箱。批下来之后要做的事有两件：Cloudflare 里加 DNS 记录指向 GitHub Pages，博客仓库里加一个 CNAME 文件，然后验证。有一点要注意：在 EU.org 批下来之前，不要点 Cloudflare 里的“我已更新 NS”。

---

**评论先用起来，域名慢慢等——博客是越用越像自己的东西。**
