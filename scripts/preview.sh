#!/bin/sh
# 半山笔记 · 本地预览
# 用法：在仓库根目录执行  sh scripts/preview.sh
# 然后浏览器打开 http://127.0.0.1:4173
#
# 说明：请在你自己的系统终端里运行（桌面右键「在终端中打开」，
# 或用系统自带的终端 App）。这个脚本依赖本机已安装的 node。

cd "$(dirname "$0")/.." || exit 1

NODE_BIN=""
for c in node /usr/bin/node /usr/local/bin/node \
         "$HOME/.workbuddy/binaries/node/versions/22.22.2/bin/node"; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then NODE_BIN="$c"; break; fi
done

if [ -z "$NODE_BIN" ]; then
  echo "没找到 node。你的系统终端里没有装 node 的话，可以先装一个："
  echo "  sudo apt install nodejs npm"
  exit 1
fi

SERVE_JS=""
for p in ./node_modules/serve/build/main.js \
         "$HOME/.workbuddy/binaries/node/workspace/node_modules/serve/build/main.js"; do
  if [ -f "$p" ]; then SERVE_JS="$p"; break; fi
done

if [ -z "$SERVE_JS" ]; then
  echo "本地没找到 serve，正在安装（只需一次）…"
  npm install --no-save serve || exit 1
  SERVE_JS="./node_modules/serve/build/main.js"
fi

echo "→ 预览地址： http://127.0.0.1:4173   （Ctrl+C 停止）"
exec "$NODE_BIN" "$SERVE_JS" -l 4173 .
