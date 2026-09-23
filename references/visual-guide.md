# 视觉规范与可复用片段

## 品牌图标与 icon

优先使用项目已有的应用图标、品牌 SVG 或正式 logo。居中显示宽度通常为 96–128 px；保留原始宽高比，不强制把非正方形图拉成正方形。使用仓库相对路径与有意义的 `alt`。不要在正文中重复展示同一图标并称其为“界面预览”。

已有透明图标需检查浅色和深色背景的可读性；确有两套素材时可使用 `<picture>`。徽章里的技术品牌 icon 只标识实际依赖或平台，不暗示官方认证。没有适当素材时保留文字；用户要求新视觉时可制作简单原创 SVG，复杂位图再使用可用的图像生成能力。

默认不在每个标题前添加 emoji。用户明确要求时可使用少量语义一致的图标，同时检查锚点。SVG 应独立可显示，不依赖脚本、外链字体或外部样式表。

## 徽章选择

通常选择 3–6 个对读者有用的状态，复杂项目按需增加；统一 `flat` 或 `flat-square`，本技能默认 `flat-square`。颜色使用项目主色与少量中性色；警示色只表达真实状态。避免彩虹式技术栈、重复统计和无意义口号。

| 徽章 | 添加依据 | 点击目的地 |
| --- | --- | --- |
| Release | 已确认存在可用 GitHub Release | 对应 Releases 页 |
| Version | 已核实本地版本清单，可与 Release 状态不同 | 版本源文件 |
| Build / Checks | 已存在相应工作流及正确文件名、分支 | 对应 Actions 工作流 |
| Downloads | 确有发行附件且该指标对使用者有意义 | Releases；指附件累计下载，不是克隆或源码 ZIP |
| Platform / Runtime | 配置或验证记录支持该范围 | 环境要求或兼容说明 |
| License | 存在适用的项目级许可文件 | 该文件 |
| Stars / Issues / Last Commit | 仓库标识已核实 | 对应仓库页面；Issues 需可用 |
| Forks / Repo Size | 对协作或获取体积有实际参考价值 | 对应仓库页面；通常低优先级 |

未确定远端仓库时可以只用真实的静态信息徽章。缺少 License 或 Release 不必制作醒目警告徽章，正文简洁说明即可。动态徽章依赖外部服务；显示失败时核对标识和状态，不伪造绿色静态“passing”。

## 居中头部片段

下方是排版模板，`{{...}}` 必须在使用时替换或删除，不可原样交付。无 logo、许可或版本时移除对应元素。

```html
<p align="center">
  <img src="{{logo_path}}" width="120" alt="{{project_name}} 项目图标">
</p>

<h1 align="center">{{project_name}}</h1>

<p align="center">{{one_sentence_description}}</p>

<p align="center">
  <a href="{{version_file}}"><img src="https://img.shields.io/badge/version-{{encoded_version}}-2563eb?style=flat-square" alt="项目版本"></a>
  <a href="{{license_file}}"><img src="https://img.shields.io/github/license/{{owner}}/{{repo}}?style=flat-square" alt="项目许可证"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#主要功能">主要功能</a> ·
  <a href="#开发">开发</a>
</p>
```

HTML 品牌区与 Markdown 正文之间留空行。复杂 `<div>` 中的 Markdown 需确认渲染效果；不引入 GitHub 会过滤的 CSS、脚本或布局依赖。HTML 属性内查询参数分隔符写为 `&amp;`；Markdown 图片 URL 中可写 `&`。

## Shields URL 片段

以真实的账号、仓库、工作流和分支替换示例变量；URL 参数必须编码。静态 badge 路径中的连字符按 Shields 规则转义，空格及特殊字符编码，避免标签被误拆分。

```text
https://img.shields.io/github/v/release/{{owner}}/{{repo}}?style=flat-square&display_name=tag
https://img.shields.io/github/downloads/{{owner}}/{{repo}}/total?style=flat-square
https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{workflow}}?branch={{branch}}&style=flat-square
https://img.shields.io/github/stars/{{owner}}/{{repo}}?style=flat-square
https://img.shields.io/github/last-commit/{{owner}}/{{repo}}?style=flat-square
https://img.shields.io/badge/platform-{{encoded_platform}}-555555?style=flat-square
```

需要品牌 icon 时使用当前服务支持的 `logo` 标识并检查显示；不猜测 slug。无网络验证能力时使用普通文字徽章更稳妥。默认 Release 徽章面向正式发布；只有确实以预发布为主要渠道时添加 `include_prereleases`。

## 预览图与图解

截图须来自真实运行画面，注明展示内容和适用版本；示意图明确标为示意。桌面截图可按约 720–960 px 展示，移动端约 240–320 px，实际以可读性和原图尺寸为准。并排对照只用于确实需要比较的少量图片。

多端工程可用 Mermaid 表达模块、数据流和控制流，边和节点采用读者能理解的名称。简单包结构用短目录树即可。没有维护的截图或录屏时省略预览章节，不生成虚构界面补位。

### 多页面截图

有多张真实截图时，可用两至三列 HTML 表格组成紧凑画廊，每张图设置 `alt`、相近显示宽度与简短图注；多行展示需检查窄屏表现，拥挤时减少列数。画廊后说明截图环境与生成方式。截图只能证明展示内容，不能证明性能或实机兼容性。

```html
<table>
  <tr>
    <td align="center"><img src="{{light_screenshot}}" width="240" alt="浅色主题主界面"><br><sub>主界面 · 浅色</sub></td>
    <td align="center"><img src="{{dark_screenshot}}" width="240" alt="深色主题主界面"><br><sub>主界面 · 深色</sub></td>
  </tr>
</table>
```
