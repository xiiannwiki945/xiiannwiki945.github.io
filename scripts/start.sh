#!/bin/sh
# 半山笔记 · 开始写作
#
# 双击运行（或右键「以程序运行」）；也可以复制这一行到终端：
#   sh ~/banshan-blog/scripts/start.sh
#
# 它会用文件管理器打开仓库所在目录，你右键任意 .html「用其他程序打开」即可编辑。
# 若已安装 VS Code，会直接用它打开整个仓库。

REPO="$HOME/banshan-blog"

if [ ! -d "$REPO" ]; then
  echo "没找到仓库目录：$REPO"
  echo "先执行： git clone https://github.com/xiiannwiki945/xiiannwiki945.github.io.git \"$REPO\""
  exit 1
fi

# 1) 有 VS Code 就用它打开整个仓库
for c in code codium; do
  if command -v "$c" >/dev/null 2>&1; then
    exec "$c" "$REPO"
  fi
done

# 2) 没有 VS Code：打开目录，让用户自己选编辑器
if command -v nautilus >/dev/null 2>&1; then
  exec nautilus "$REPO"
elif command -v nemo >/dev/null 2>&1; then
  exec nemo "$REPO"
elif command -v thunar >/dev/null 2>&1; then
  exec thunar "$REPO"
else
  exec xdg-open "$REPO"
fi
