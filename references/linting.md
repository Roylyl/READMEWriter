# README lint

校验器使用 Python 3.9+ 标准库；只读取文档、链接目标和可选证据记录，不联网、不运行文档中的命令、不修改文件。未传 `--repo` 时读取本地 Git origin 识别 GitHub 仓库。

在目标仓库中运行，脚本路径使用实际安装的技能目录：

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/readme-writer/scripts/validate_readme.py" README.md --root .
```

在 READMEWriter 本仓库可运行：

```sh
python3 scripts/validate_readme.py README.md --root . --format json
python3 scripts/validate_readme.py README.md --root . --evidence evidence.json
```

第二条仅在已经创建相应证据记录时使用。任意目标文档均可通过位置参数指定；`--root` 默认该文档所在目录，校验子目录文档时显式传仓库根目录。

## 检查项

| 诊断代码 | 含义 |
| --- | --- |
| missing-file / missing-image | Markdown / HTML 引用的本地文件或图片不存在 |
| path-case | 路径大小写与目录项不同，包括 macOS 默认文件系统 |
| invalid-anchor | 本页或本地 Markdown 标题锚点、HTML id/name 不存在 |
| duplicate-h1 / missing-h1 | 多个一级标题为错误；缺少一级标题为警告 |
| undefined-reference | 完整或折叠引用式链接缺少定义 |
| placeholder | 未替换的双花括号变量、常见待办标记或模板变量 |
| local-absolute-path | 常见本机目录、Windows 盘符/UNC 或 file URL 泄漏 |
| badge-repo-mismatch | GitHub Shields 徽章的 owner/repo 与期望仓库不一致 |
| badge-repo-unverified | 存在 GitHub 徽章但无法确定目标仓库，给出警告 |
| outside-root / root-relative-link | 本地目标越出根目录为错误；网站根路径无法离线核实，给出警告 |
| evidence-* / claim-not-found | 证据格式、引用、摘录、哈希或声明存在性问题 |

返回码：`0` 无错误，`1` 有错误（或 `--strict` 下有警告），`2` 命令参数无效。`--format json` 输出稳定的诊断数组，包含代码、严重度、行号和消息；证据诊断定位于 README 第一行并附带 claim id。

`--repo owner/repo` 显式指定仓库。第三方徽章可用重复的 `--allow-badge-repo owner/repo` 放行。模板说明文档可用 `--ignore placeholder`，但应在评审说明理由，不为最终 README 静默忽略错误。

## 支持范围与限制

支持常见 Markdown 内联链接、带空格的尖括号 URL、平衡括号 URL、引用式链接、嵌套徽章图片，以及 HTML 的 href、src、srcset。支持 ATX、Setext、HTML 标题、中文标题、重复标题序号和显式 HTML 锚点。代码块中的示例链接不作为真实链接检查；占位符和本机路径仍检查代码示例。

这是面向常见 GitHub README 的轻量解析器，不是完整 CommonMark/GFM 引擎。复杂转义、扩展 Markdown、模板语法、跨行 HTML 代码块、含逗号的 srcset 数据 URL 等需人工复核；锚点算法在罕见 Unicode 或复杂内联 HTML 下可能与 GitHub 不同。不会验证 HTTP 链接可用性、远端锚点、徽章数值/查询参数有效性、图片像素内容，也不会判断目录树或普通反引号文本是否真的是文件引用。

本机路径检测只覆盖文档中列出的常见模式，不能代替密钥或隐私扫描。lint 通过不能证明 README 中的功能与测试结论真实；继续按 [证据规范](evidence-guide.md) 评审声明。
