# 系统组 · 研究札记

系统组会议与汇报的中文静态网站，收录核心思想、主讲人与成员 idea、可展开的论文图与数据，以及章节目录和前后期导航。禁用 JavaScript 仍可阅读和展开补充资料。

- 网站地址：https://haodongwang01.github.io/group_meeting/
- 公开仓库：https://github.com/haodongwang01/group_meeting
- 内容日期：2026-10-15、2026-10-22、2026-11-04、2026-11-05、2026-11-18

## 组员周报

[查看本周周报](https://haodongwang01.github.io/group_meeting/weekly/) · [填写说明](content/weekly/README.md) · [Markdown 模板](content/weekly/TEMPLATE.md)

每人每周一份 Markdown，提交至 `content/weekly/周一日期/姓名.md`。归档自 2026 年 11 月 23 日开始，按北京时间划周。每次推送和每周一 00:07 的定时工作流都会构建当周页面。复核历史构建时可用环境变量 `WEEKLY_AS_OF` 指定该次发布的北京日期。周报中的材料链接请使用完整的 HTTP 或 HTTPS 地址。

## 本地预览

需要 Python 3；预生成的 `dist/` 可以直接托管，无需构建。

```sh
python -m http.server 8080 --directory dist
```

打开 http://localhost:8080 。也可以直接打开 `dist/index.html` 阅读。

## 文件布局

```text
content/meetings.json       日期、标题、摘要、标签、来源与封面
content/YYYY-MM-DD.html     每期核心思想与 idea，维护入口
scripts/build.py           标准库构建脚本
scripts/check.py           内部链接、锚点、图片、正文与元数据检查
dist/index.html            首页
dist/meetings/              独立详情页
dist/assets/               共用 CSS、JS、图标与引用插图
dist/credits.html          来源及许可范围
dist/404.html              未找到页面
dist/sitemap.xml           站点地图
.github/workflows/pages.yml GitHub Pages 自动构建与发布
```

## 新增一期

1. 新建 `content/YYYY-MM-DD.html`，用具有唯一 `id` 的 `h2`、`h3` 标记章节。正文直接写入 HTML，外部文字必须进行 HTML 转义。
2. 在 `content/meetings.json` 顶部增加记录，保持日期倒序；补充 `date`、`issue`、`title`、`summary`、`tags`、`type`、`source`、`cover`、`notice`，以及 `speaker`（主讲人）、`contribution_label`（贡献类型）、`contributors`（贡献者）。
3. 图片放进 `dist/assets/images/`。使用已有正文中的 `figure > a.zoom > img` 格式，提供有意义的 `alt` 和来源图注。`href`、`src` 从详情页使用 `../assets/images/文件名`。
4. 正文先写简短的核心思想；每个 idea 用独立卡片列出提出者、具体做法与优先验证事项。区分研究方向、完整方案和讨论建议，不能把整理时补充的实验步骤当作成员原话。详细数据和原图放进原生 `details`，保留实验条件、关键数字和限制。归属不明时向会议组织者核实，同步更新 `SOURCES.md`。
5. 运行构建和检查：

```sh
python scripts/build.py
python scripts/check.py
node --check dist/assets/site.js
```

构建会更新全部页面、目录、前后期导航、归档期数和站点地图。更改域名时设置环境变量 `SITE_URL` 后构建。新增研究主题时，同步更新首页筛选按钮；归档日期范围也应随记录更新。

## 发布

在仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。每次推送到 `main`，工作流 **Publish meeting notes** 都会重新构建、校验并发布 `dist/`。需要重新发布时，可以在 Actions 页面手动运行这个工作流。

GitHub Pages 将网站挂载到 `/group_meeting/`。独立文章的公开路径为 `/group_meeting/meetings/YYYY-MM-DD.html`。发布目录只包含网页和引用插图。

## 验证与许可

内容核对记录见 [SOURCES.md](SOURCES.md)，验证状态见 [VERIFICATION.md](VERIFICATION.md)。原创代码采用 [MIT](LICENSE)；会议正文、论文图片等引用材料不属于 MIT 授权范围，详见网页来源说明。
