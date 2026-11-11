# 系统组 · 研究札记

四期小组会的中文静态网站：完整正文、论文插图、章节目录、主题筛选和前后期导航。无需数据库、账号或前端依赖，禁用 JavaScript 仍可阅读正文与导航。

- 预定 Sites 地址：https://system-group-notes.primleaf.chatgpt.site （实际部署状态以交付记录为准）
- 公开仓库：https://github.com/haodongwang01/group_meeting
- 内容日期：2026-10-15、2026-10-22、2026-11-04、2026-11-05

## 本地预览

需要 Python 3；预生成的 `dist/` 可以直接托管，无需构建。

```sh
python -m http.server 8080 --directory dist
```

打开 http://localhost:8080 。也可以直接打开 `dist/index.html` 阅读。

## 文件布局

```text
content/meetings.json       日期、标题、摘要、标签、来源与封面
content/YYYY-MM-DD.html     每期完整正文，维护入口
scripts/build.py           标准库构建脚本
scripts/check.py           内部链接、锚点、图片、正文与元数据检查
dist/index.html            首页
dist/meetings/              独立详情页
dist/assets/               共用 CSS、JS、图标与引用插图
dist/credits.html          来源及许可范围
dist/404.html              未找到页面
dist/sitemap.xml           站点地图
.openai/hosting.json       Sites 身份与静态部署目录
```

## 新增一期

1. 新建 `content/YYYY-MM-DD.html`，用具有唯一 `id` 的 `h2`、`h3` 标记章节。正文直接写入 HTML，外部文字必须进行 HTML 转义。
2. 在 `content/meetings.json` 顶部增加记录，保持日期倒序；补充 `date`、`issue`、`title`、`summary`、`tags`、`type`、`source`、`cover`、`notice`。
3. 图片放进 `dist/assets/images/`。使用已有正文中的 `figure > a.zoom > img` 格式，提供有意义的 `alt` 和来源图注。`href`、`src` 从详情页使用 `../assets/images/文件名`。
4. 区分论文结果、组内实验、待验证设想；保留实验条件、关键数字、发言归属和限制。同步更新 `SOURCES.md`。
5. 运行构建和检查：

```sh
python scripts/build.py
python scripts/check.py
node --check dist/assets/site.js
```

构建会更新全部页面、目录、前后期导航和站点地图。更改域名时设置环境变量 `SITE_URL` 后构建。归档期数显示应随新一期更新 `scripts/build.py` 中的数量（或改为自动计算）。

## 发布

将 `dist/` 作为站点根目录。Sites 使用 `.openai/hosting.json` 指定的项目和静态目录；更新已有站点时保留 `project_id`，不要重复创建。使用 Sites 技能的 source helper 同步对应的源码仓库、检查并打包，随后保存版本并部署。站点访问权限应为 `public`。凭证仅通过 helper 的隐藏标准输入传入，不写入代码、日志、Git remote 或仓库。

Sites 源码仓库与本公开 GitHub 仓库是两个远端；发布时同步同一份文件树，并核对公开仓库的文件摘要。Sites archive 放在项目目录之外。公开仓库只包含网页、网页正文和引用插图，不包含原始 DOCX/PDF/TeX/演示文稿。

若使用其他静态平台，直接发布 `dist/`，配置真正的 404 页面，确保 `/meetings/YYYY-MM-DD.html` 可以独立访问；无需 SPA 重写。GitHub 公开仓库本身不自动启用 GitHub Pages。

## 验证与许可

内容核对记录见 [SOURCES.md](SOURCES.md)，验证状态见 [VERIFICATION.md](VERIFICATION.md)。原创代码采用 [MIT](LICENSE)；会议正文、论文图片等引用材料不属于 MIT 授权范围，详见网页来源说明。
