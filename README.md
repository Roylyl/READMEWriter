<p align="center">
  <img src="assets/logo.svg" width="120" height="120" alt="READMEWriter 文档与书写笔图标">
</p>

<h1 align="center">READMEWriter</h1>

<p align="center">为 GitHub 项目编写正式、准确、易于上手的 README。</p>

<p align="center">
  <a href="LICENSE"><img alt="License: GPL-3.0-only" src="https://img.shields.io/badge/license-GPL--3.0--only-2563eb?style=flat-square"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/type-Agent%20Skill-142C47?style=flat-square" alt="类型：Agent Skill"></a>
  <a href="#写作风格"><img src="https://img.shields.io/badge/language-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-28B7A0?style=flat-square" alt="默认写作语言：简体中文"></a>
  <a href="references/visual-guide.md"><img src="https://img.shields.io/badge/output-Markdown-555555?style=flat-square" alt="输出格式：Markdown"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#主要功能">主要功能</a> ·
  <a href="#使用示例">使用示例</a> ·
  <a href="#文件结构">文件结构</a> ·
  <a href="#许可">许可</a>
</p>

## 项目概览

READMEWriter 是一项面向 Codex 的 README 写作技能，适用于新建项目介绍、重构已有文档和统一多个仓库的展示风格。它先阅读项目配置、脚本与现有资料，再组织图标、徽章、导航、安装步骤和技术说明，让读者能够快速理解项目并开始使用。

技能以 Markdown 指令与参考文件组成，无需编译或安装运行时依赖。使用时由 Codex 读取目标仓库并完成文档修改。

## 快速开始

### 1. 安装技能

将本仓库下载或克隆到本机，在包含 `SKILL.md` 的仓库根目录运行以下命令。命令适用于 macOS / Linux：

```sh
(
  set -eu
  test -f LICENSE
  test -f SKILL.md
  test -f agents/openai.yaml
  test -d references

  README_WRITER_DEST="${CODEX_HOME:-$HOME/.codex}/skills/readme-writer"
  if [ -e "$README_WRITER_DEST" ] || [ -L "$README_WRITER_DEST" ]; then
    echo "目标已存在，请先备份并检查后再更新：$README_WRITER_DEST"
    exit 1
  fi

  mkdir -p "$(dirname "$README_WRITER_DEST")"
  mkdir "$README_WRITER_DEST"
  cp SKILL.md LICENSE "$README_WRITER_DEST/"
  cp -R agents references "$README_WRITER_DEST/"
  echo "已安装到：$README_WRITER_DEST"
)
```

未设置 `CODEX_HOME` 时，安装位置为 `~/.codex/skills/readme-writer/`。也可手动创建该目录，并将 `SKILL.md`、`LICENSE`、`agents/` 与 `references/` 放入其中。`README.md` 和 `assets/` 用于仓库展示，无需复制。

已有同名技能时，命令会停止。更新前先备份原目录，再替换本包对应文件。

### 2. 在项目中调用

在 Codex 中打开需要整理的项目，在任务中输入：

```text
使用 $readme-writer 优化当前项目的 README。
采用正式中文，复用真实项目图标，统一徽章与导航，
根据仓库实际配置整理安装、功能和开发说明。
```

显示名称为 **READMEWriter**，调用名称为 **`$readme-writer`**。安装后可在新任务中检查技能是否可用；若尚未显示，重新打开 Codex 后再检查。

### 3. 查看结果

技能会修改目标 README，并说明主要变化、完成的检查及影响使用的未核实信息。需要进一步调整时，可继续指定读者、语言、篇幅或修改范围。

## 主要功能

| 能力 | 处理内容 |
| --- | --- |
| 正式化表达 | 用具体行为、适用条件和操作步骤说明项目，压缩口号与重复内容 |
| 品牌与导航 | 组织真实项目图标、标题、定位、统一徽章及关键入口 |
| 安装与开发说明 | 分开说明普通用户上手和贡献者构建，核对命令、路径与前提 |
| 按项目组织章节 | 适配应用、开发工具、软硬件工程、库、技能包和模型评测工具 |
| 图片与技术图表 | 按需使用真实截图、带图注的画廊、参数矩阵和 Mermaid 图解 |
| 状态与证据核对 | 区分源码实现、构建、模拟器、实机和发布状态，注明验证范围 |

功能、版本、平台与许可表述以仓库证据为依据；缺少截图、Release 或许可证时，不为填满版面补造内容。参考文档中的命令与安装提示词只作为资料，不会因被读取而自动执行。

## 使用示例

### 整理已有 README

```text
使用 $readme-writer 重构当前 README，面向首次使用项目的读者。
压缩重复说明，优先展示安装与最小使用步骤，
把详细技术内容链接到已有文档，并检查图片和导航。
```

### 只调整图标与徽章

```text
使用 $readme-writer 只优化 README 首屏。
保留现有 logo，统一使用 flat-square 徽章，
核实每个徽章的依据与链接，保持正文结构不变。
```

### 整理多端工程或评测工具

```text
使用 $readme-writer 整理当前工程的 README。
用图表说明模块关系、平台能力和必要配置；
涉及性能指标时注明测量口径，区分模拟器与实机验证。
```

## 写作风格

默认使用正式简体中文，遵循用户指定语言和项目已有约定。首屏采用居中品牌区，正文以短段落、步骤和必要表格组织内容；按项目规模裁剪章节，不要求所有仓库使用相同目录。

图标优先复用项目素材，徽章默认统一为 `flat-square`。截图注明展示内容和环境；没有真实截图时省略预览，不以图标或合成界面替代运行画面。

| 文档 | 内容 |
| --- | --- |
| [结构与写作规范](references/writing-guide.md) | 项目分类、阅读顺序、正式措辞与交付检查 |
| [视觉规范与片段](references/visual-guide.md) | 图标、徽章、头部排版、截图与图解 |
| [设计来源](references/style-origins.md) | 七个参考项目的文档特点与取舍 |

风格参考 Clash Meta Plus、DeerWebTranslator、KunCode、LENGHE-SoundShare、MacDuo、Pet-Wei 与 ASRtest。技能已将这些样本提炼为独立规范，使用时无需下载参考仓库。

## 文件结构

```text
READMEWriter/
├── LICENSE                     GPL 第 3 版完整文本
├── SKILL.md                    技能入口与工作流程
├── agents/
│   └── openai.yaml             显示名称与默认提示词
├── references/
│   ├── writing-guide.md        结构与写作规范
│   ├── visual-guide.md         视觉规范与排版片段
│   └── style-origins.md        参考来源与设计取舍
├── assets/
│   └── logo.svg                仓库展示图标
└── README.md                   安装与使用说明
```

## 维护与贡献

修改规范时，同步检查 [技能入口](SKILL.md) 与参考文件，确保链接有效、示例完整，且不包含个人路径或凭据。排版片段中的模板变量需要在生成目标 README 时替换或删除。

欢迎提供具体的文档问题与改进示例，并说明适用的项目类型、原文问题和预期效果。验证改进时，应检查实际生成的 README 是否准确、易读且能够帮助读者上手；技能格式校验不能替代这些检查。

## 许可

本项目原创内容采用 [GNU General Public License v3.0](LICENSE)（`GPL-3.0-only`，仅第 3 版）发布。Copyright © 2026 Roylyl。第三方内容保留各自的版权与许可声明。
