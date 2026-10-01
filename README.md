<p align="center">
  <img src="assets/logo.svg" width="120" height="120" alt="READMEWriter项目图标">
</p>

<h1 align="center">READMEWriter</h1>

<p align="center">面向Codex的README写作技能，让项目介绍更清晰，让读者更快上手。</p>

<p align="center">
  <a href="SKILL.md"><img src="https://img.shields.io/badge/type-Codex%20Skill-142C47?style=flat-square" alt="类型：Codex Skill"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0--only-2563eb?style=flat-square" alt="技能包许可：GPL-3.0-only"></a>
  <a href="references/writing-guide.md"><img src="https://img.shields.io/badge/language-简体中文-28B7A0?style=flat-square" alt="默认语言：简体中文"></a>
  <a href="https://github.com/Roylyl/READMEWriter/stargazers"><img src="https://img.shields.io/github/stars/Roylyl/READMEWriter?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/Roylyl/READMEWriter/commits"><img src="https://img.shields.io/github/last-commit/Roylyl/READMEWriter?style=flat-square" alt="最近提交"></a>
</p>

<p align="center">
  <a href="#项目介绍">项目介绍</a> ·
  <a href="#快速入门">快速入门</a> ·
  <a href="#主要功能">主要功能</a> ·
  <a href="#使用示例">使用示例</a> ·
  <a href="#自定义写作风格">自定义写作风格</a> ·
  <a href="#许可证">许可证</a>
</p>

## 项目介绍

READMEWriter帮助Codex编写、重构和优化GitHub项目的README。它从项目已有资料出发，组织项目用途、主要功能和快速入门，让读者迅速了解项目，并找到开始使用的路径。

适合为新项目编写README、整理开源项目的展示页面，也适合统一多个仓库的文档风格。应用、命令行工具、库、浏览器扩展、硬件工程和技能项目都可以使用。

默认使用简体中文，也可以指定其他语言。正文以自然、具体的介绍为主，配合图标、徽标、导航和必要的使用示例，避免空章节和长篇铺垫。

## 快速入门

### 1. 获取项目

下载仓库源码，或使用Git克隆：

```sh
git clone https://github.com/Roylyl/READMEWriter.git
cd READMEWriter
```

### 2. 安装到Codex

将以下文件和目录复制到Codex的`skills/readme-writer/`目录：

```text
readme-writer/
├── SKILL.md
├── LICENSE
├── OUTPUT-LICENSING.md
├── agents/
├── references/
└── scripts/
```

默认技能目录是用户目录下的`.codex/skills/`；设置了`CODEX_HOME`时，使用该目录下的`skills/`。技能目录名为`readme-writer`，显示名称为READMEWriter。

也可以在仓库根目录执行对应系统的命令。以下命令会覆盖目标目录中的同名文件，更新时请先保留自己的定制内容。

Windows/PowerShell：

```powershell
$skillRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillDestination = Join-Path $skillRoot 'skills/readme-writer'
New-Item -ItemType Directory -Path $skillDestination -Force | Out-Null
foreach ($entry in @('SKILL.md', 'LICENSE', 'OUTPUT-LICENSING.md', 'agents', 'references', 'scripts')) {
    Copy-Item -LiteralPath $entry -Destination $skillDestination -Recurse -Force
}
```

macOS/Linux：

```sh
skill_destination="${CODEX_HOME:-$HOME/.codex}/skills/readme-writer"
mkdir -p "$skill_destination"
cp SKILL.md LICENSE OUTPUT-LICENSING.md "$skill_destination/"
cp -R agents references scripts "$skill_destination/"
```

### 3. 在项目中使用

安装后，在Codex中打开需要编写README的项目，输入：

```text
使用技能$readme-writer，优化当前项目的README。
重点介绍项目用途、主要功能和快速入门，完善徽标与导航。
```

生成的README通常包含项目介绍、主要功能和快速入门；配置、截图、使用示例、开发说明与许可证按项目需要添加。小项目可以保持精简，复杂项目通过链接提供更多资料。

## 主要功能

- 项目介绍：提炼项目定位、用途与适用场景，让读者快速理解项目价值。
- 快速入门：整理必要环境、安装方式、最少配置和启动示例，优先提供普通用户的使用路径。
- 功能整理：用具体行为和用途描述核心能力，合并重复内容，减少空泛宣传。
- 徽标与导航：按项目补齐许可、版本、平台、分发和仓库信息，统一样式并对应到实际入口。
- 视觉展示：复用项目图标与真实截图，整理首屏、图注和页面阅读顺序。
- 多类型适配：提供15类项目的选材参考，根据项目规模安排内容，不强制套用固定模板。
- 风格统一：默认采用简洁中文、短段落、清晰步骤和必要表格，也支持指定语言、读者和篇幅。

## 使用示例

### 为新项目编写README

```text
使用技能$readme-writer，为当前项目编写README。
面向第一次接触项目的用户，介绍项目用途、核心功能和最短上手步骤。
```

### 精简已有README

```text
使用技能$readme-writer，精简当前README。
将快速入门提前，合并重复说明，保留必要配置与使用示例。
```

### 完善项目展示

```text
使用技能$readme-writer，优化README的首屏展示。
复用已有图标，完善适用徽标与导航，并整理真实截图和图注。
```

### 统一多个项目的风格

```text
使用技能$readme-writer，统一这些项目的README风格。
保持各项目的功能与安装方式，统一首屏、标题、徽标样式和快速入门的组织方式。
```

## 自定义写作风格

调用时可以指定目标读者、语言、篇幅和需要保留的内容，例如“面向普通用户”“输出英文README”“保持精简”“保留现有截图和下载入口”。

需要长期调整风格时，修改技能目录中的对应文件：

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 调整写作重点与整体工作方式 |
| [写作规范](references/writing-guide.md) | 调整正文结构、表达和快速入门写法 |
| [视觉规范](references/visual-guide.md) | 调整图标、徽标、导航和截图布局 |
| [项目分类](references/project-profiles.md) | 参考不同类型项目适合介绍的内容 |
| [默认提示词](agents/openai.yaml) | 调整技能显示说明和调用提示 |

日常写作直接使用技能即可。`scripts/`提供可选的文档辅助工具，不是使用READMEWriter的前提。

## 许可证

READMEWriter技能包采用[GPL-3.0-only](LICENSE)。Copyright © 2026 Roylyl。

使用READMEWriter编写或改写README，不会仅因此要求你的项目或README采用GPL。生成内容遵循其实际内容和项目授权安排；复制技能包或第三方内容时，遵循对应许可。详见[生成内容许可政策](OUTPUT-LICENSING.md)。
