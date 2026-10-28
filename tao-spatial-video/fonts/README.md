# 字体（自动下载，不随仓库分发）

`python3 make_video.py setup --fonts` 会按 `../assets.json` 下载并逐个核对 sha256：

| 文件 | 用途 | 来源 |
|---|---|---|
| Poppins-BlackItalic.ttf / Poppins-SemiBold.ttf | 英文产品名、数字 | google/fonts（SIL OFL） |
| NotoSansCJKsc-Regular/Medium/Bold/Black.otf | 中文（版本 2.004） | notofonts/noto-cjk 标签 Sans2.004（SIL OFL） |

素材渲染时 Chromium 只加载这个目录里的字体（私有 fontconfig），不用系统字体，所以任何机器上文字都一样。
哈希不符会直接报错：说明字体版本变了，成片会和基准不一致。
