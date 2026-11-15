#!/bin/sh
# 打开半山笔记仓库（需已安装 VS Code）
#
# 安装 VS Code（任选其一）：
#   1) 图形化：打开「软件中心 / App Center」搜 Visual Studio Code，点安装
#   2) 命令行：sudo snap install code --classic
#   3) 或用系统自带的文本编辑器 / Typora 直接打开 .html 文件，一样能写
#
# 用法： sh scripts/open.sh

REPO="$(cd "$(dirname "$0")/.." && pwd)"

if command -v code >/dev/null 2>&1; then
  exec code "$REPO"
fi

if command -v codium >/dev/null 2>&1; then
  exec codium "$REPO"
fi

echo "还没找到 VS Code。请先看上面注释里的安装方式，或者直接用你喜欢的编辑器打开："
echo "  $REPO"
exit 1
