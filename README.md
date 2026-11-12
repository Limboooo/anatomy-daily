# 人体小课 / anatomy-daily

每天介绍一块骨头或一块肌肉：它在哪儿、长什么样、跟相邻结构怎么联动，以及在常见训练动作（推、拉、蹲、举过顶）里怎么干活。

这是解剖讲解，不是训练计划，也不代替就医。

## 怎么看

- 网页（GitHub Pages）：https://limboooo.github.io/anatomy-daily/
- 每天中午还会在微信推当天那课的要点、位置图、短视频和一页 PDF。网页是更细的交互版，可以拖动旋转立体骨头、点结构、对照图、顺着联动看。

目前已上线：

1. [锁骨](https://limboooo.github.io/anatomy-daily/lessons/01-clavicle.html)
2. [肩胛骨](https://limboooo.github.io/anatomy-daily/lessons/02-scapula.html)

## 配图原则

只用公有领域或开放许可的教材，不用 AI 生成的图或模型当教材。来源和许可见 [ATTRIBUTION.md](ATTRIBUTION.md)。

因 Anatomography 影像采用 CC BY-SA 2.1 JP，本仓库的页面文字与编排也以相同许可共享；格雷氏解剖学图版本身是公有领域。锁骨和肩胛骨的立体网格来自 BodyParts3D 4.3，按数据库现行的 CC BY 4.0 再分发。

## 技术

纯静态 HTML / CSS / 少量 JS，手机浏览器可直接打开。无需构建步骤。GitHub Pages 从 `main` 分支根目录发布。仓库根目录有 `.nojekyll`，避免 Jekyll 改写路径。

立体查看器用的是仓库里的 `<model-viewer>`（`js/model-viewer.min.js`），模型是 `models/*.glb`。本地预览请用一个静态服务器，不要直接双击 HTML，否则浏览器会拦住模块脚本：

```bash
python3 -m http.server 8080
```

然后打开 http://127.0.0.1:8080/lessons/01-clavicle.html 和 http://127.0.0.1:8080/lessons/02-scapula.html 。在模型上拖动可以旋转，滚动或捏合可以缩放。
