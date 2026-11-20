# 人体小课 / anatomy-daily

每天介绍一块骨头或一块肌肉：它在哪儿、长什么样、跟相邻结构怎么联动，以及在常见训练动作（推、拉、蹲、举过顶）里怎么干活。

这是解剖讲解，不是训练计划，也不代替就医。

## 怎么看

- 网页（GitHub Pages）：https://limboooo.github.io/anatomy-daily/
- 每天中午还会在微信推当天那课的要点、位置图、短视频和完整 PDF。网页是更细的交互版：骨头课可以拖动旋转立体模型，也可以点结构、对照图、顺着联动看。

目前已上线：

1. [锁骨](https://limboooo.github.io/anatomy-daily/lessons/01-clavicle.html)
2. [肩胛骨](https://limboooo.github.io/anatomy-daily/lessons/02-scapula.html)
3. [三角肌](https://limboooo.github.io/anatomy-daily/lessons/03-deltoid.html)
4. [肱骨](https://limboooo.github.io/anatomy-daily/lessons/04-humerus.html)
5. [肱二头肌](https://limboooo.github.io/anatomy-daily/lessons/05-biceps.html)
6. [肱三头肌](https://limboooo.github.io/anatomy-daily/lessons/06-triceps.html)
7. [桡骨](https://limboooo.github.io/anatomy-daily/lessons/07-radius.html)
8. [尺骨](https://limboooo.github.io/anatomy-daily/lessons/08-ulna.html)

另外两页：

- [全身骨骼](skeleton.html)：站立的整副骨架，可旋转缩放。点锁骨、肩胛骨、肱骨、桡骨或尺骨进入已有的课，点其他骨头停在本页。
- [肩带联动](shoulder.html)：拖左锁骨、左肩胛骨或左肱骨，另外两块按胸锁、肩锁和肩关节跟着动。单块骨头的查看器仍留在对应课页里。肌肉课没有立体骨头。

## 配图原则

只用公有领域或开放许可的教材，不用 AI 生成的图或模型当教材。来源和许可见 [ATTRIBUTION.md](ATTRIBUTION.md)。

因 Anatomography 影像采用 CC BY-SA 2.1 JP，本仓库的页面文字与编排也以相同许可共享；格雷氏解剖学图版本身是公有领域。锁骨、肩胛骨、肱骨、桡骨和尺骨的立体网格来自 BodyParts3D 4.3，按数据库现行的 CC BY 4.0 再分发。肱骨、桡骨、尺骨是从全身模型里拆出的同一份网格，只平移到各自的中心。

## 技术

纯静态 HTML / CSS / 少量 JS，手机浏览器可直接打开。无需构建步骤。GitHub Pages 从 `main` 分支根目录发布。仓库根目录有 `.nojekyll`，避免 Jekyll 改写路径。

单块骨头用的是仓库里的 `<model-viewer>`（`js/model-viewer.min.js`）。全身骨骼和肩带联动用的是仓库里的 Three.js r170（`js/vendor/three.module.min.js`），不从外网加载。模型是 `models/*.glb`。本地预览请用一个静态服务器，不要直接双击 HTML，否则浏览器会拦住模块脚本：

```bash
python3 -m http.server 8080
```

然后打开：

- http://127.0.0.1:8080/skeleton.html
- http://127.0.0.1:8080/shoulder.html
- http://127.0.0.1:8080/lessons/01-clavicle.html
- http://127.0.0.1:8080/lessons/08-ulna.html

在模型上拖动可以旋转，滚动或捏合可以缩放。肩带那一页要拖在骨头上，旁边的骨头才会跟着动；拖空白处只转动视角。

## 上新课

每上新课，从 `main` 开分支，改完向 `main` 开 PR，等 review。不要自己合并。

- 新增 `lessons/NN-slug.html`。课页要有讲解全文、位置图、细部图、两个转动短视频，以及一份完整 PDF。
- 媒体放进 `media/`，沿用现有英文小写文件名：位置图、全身转动、特写转动、完整 PDF、Gray 图版。
- 更新 `index.html`：该课改为可点的「已上线」。需要时把顶部按钮指到最近一课。没上课的不要挂页面，目录继续写「未开课」。
- 更新 [ATTRIBUTION.md](ATTRIBUTION.md)。
- 只用公有领域或开放许可材料，不用 AI 图或 AI 模型当教材，也不要另写一套解剖事实。

不做自动发布。GitHub Pages 仍从 `main` 根目录发布。
