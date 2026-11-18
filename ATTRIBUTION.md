# 来源与许可

本课的图、短视频和立体模型只使用公有领域或开放许可教材，不用 AI 生成的图或模型当教材。

## 立体骨模型（BodyParts3D 4.3）

作者：The Database Center for Life Science（ライフサイエンス統合データベースセンター，DBCLS）/ BodyParts3D

数据版本：4.3（清单抬头为 `Data Version 4.3`、`Objects set 4.3`、`Tree version FMA3.0`）

下载：Anatomography 的 `https://lifesciencedb.jp/bp3d/download.cgi`，对照 `get-info.cgi?version=4.3&cmd=concept-objfiles-list` 里的 FMA 对照表，以及同一版本的 obj2FMA 表。

| 课程 | 文件 | 表示 ID | 概念 | 英文名 | 源 OBJ SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 锁骨 | FJ6347 | BP23283 | FMA13323 | Left clavicle | `7bd988c1e54e9696d581e4be2e94f5de9cc08c00260dcf88aba42cc21f0b533f` |
| 肩胛骨 | FJ3279 | BP23279 | FMA13396 | Left scapula | `87cebf8702718e03dd10afbee87a50abce47139802ff305c749b33f40d451fda` |

4.3 清单把左锁骨写成 `FJ3237+FJ6347`，两份 OBJ 的表示 ID 都是 BP23283，包围盒几乎重合，顶点平均距离约 0.26 mm，是同一块骨头的先后版本，不是两截拼在一起。页面使用较新的 FJ6347（文件时间 2014-01-31）。较早一份 FJ3237 的 SHA-256 是 `a7eda265732db6c87ab0fb8c8f78a274882ceca59510991b0e7b32078c08152f`，没有并进模型。

仓库里的 `models/clavicle-left.glb` 与 `models/scapula-left.glb` 只做了这些变换：包围盒中心移到原点、毫米换成米、转到 glTF 的 Y 轴向上（肩胛骨背面朝向默认相机，锁骨的 S 形放在水平面里）、重算平滑法线，并加上象牙色材质。顶点没有平滑、减面或重塑。转换步骤记在 `tools/build_bone_glbs.py`。

许可：生命科学数据库归档在 2025-02-27 把 BodyParts3D 的利用许诺更新为 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。归档站要求的署名是：

> BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International

这两个 GLB 按该许可再分发。CC BY 4.0 不允许在演绎物上再加更严的条款，所以模型文件本身不改成 CC BY-SA。

## 全身骨骼与肩带（BodyParts3D 4.3）

`models/skeleton.glb` 和 `models/shoulder-left.glb` 用的是同一版 4.3 元素网格，署名同上：

> BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International

肩带三块，文件头里的标识和源 OBJ 的 SHA-256：

| 骨头 | 文件 | 表示 ID | 概念 | 英文名 | 源 OBJ SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 左锁骨 | FJ6347 | BP23283 | FMA13323 | Left clavicle | `7bd988c1e54e9696d581e4be2e94f5de9cc08c00260dcf88aba42cc21f0b533f` |
| 左肩胛骨 | FJ3279 | BP23279 | FMA13396 | Left scapula | `87cebf8702718e03dd10afbee87a50abce47139802ff305c749b33f40d451fda` |
| 左肱骨 | FJ6373 | BP24066 | FMA23131 | Left humerus | `fe3987aa1ce56130acc913ef5b7299000ae56ffa6d3f35e0e0c0b205ab457efe` |

全身那一份一共 254 个元素，左右成对，外加颅骨、下颌、舌骨、胸骨三块、24 根肋骨、第 1 到第 10 肋软骨、7 节颈椎、12 节胸椎、5 节腰椎、骶骨、上肢带和游离上肢骨、髋骨、游离下肢骨、腕骨、跗骨、掌骨、跖骨、指骨、趾骨、足部籽骨和牙齿。逐条的文件号、表示 ID、概念和 SHA-256 在 `models/skeleton-sources.json`。4.3 清单里没有单独的尾骨元素。椎间盘没有收进来，它们不是骨头。肋软骨收进来，是为了让肋弓连到胸骨，点下去会标明是软骨。

同一块骨头若有两份重叠的 FJ，保留编号较大的那份，和锁骨课选用 FJ6347 而不是较早的 FJ3237 是同一条规则。有几份较新的右侧指骨、趾骨文件重心落在身体左侧，已丢掉，留下位于右侧的那份。左髋骨用较新的骨性部分 FJ6398（FMA236884），不再叠上较早的 FJ3288。

变换只有这些：源坐标是毫米，+X 为左、+Y 为后、+Z 为上；换成 glTF 的米、+Y 向上、+Z 朝前（默认相机看见脸）；再把整副模型的包围盒中心移到原点。肩带文件用这三块骨头自己的包围盒中心，关节之间的相对位置不变。法线按面重算。顶点没有平滑、减面或重塑。步骤在 `tools/build_skeleton_glbs.py`。

肩带页面把三块骨头串在胸锁关节、肩锁关节和肩关节上。拖一块时，相邻的角度一起变，并限制在日常活动范围里，所以内侧端留在胸骨附近，肱骨头留在关节盂里。

Anatomography 查看器页面仍显示较早的 [CC BY-SA 2.1 JP](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en) 标志，并写明详细以归档站许诺为准。该页要求同时标注：

> BodyParts3D, Copyright 2008 ライフサイエンス統合データベースセンター licensed by CC 表示-継承 2.1 日本

课程页两行署名都保留。

## Anatomography / BodyParts3D 图像

作者：Anatomography（Life Science Database / BodyParts3D）

许可：[CC BY-SA 2.1 JP](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)

本课使用的原图（维基共享资源）：

- [Clavicle - anterior view](https://commons.wikimedia.org/wiki/File:Clavicle_-_anterior_view.png)
- [Clavicle - lateral view](https://commons.wikimedia.org/wiki/File:Clavicle_-_lateral_view.png)
- [Clavicle - animation](https://commons.wikimedia.org/wiki/File:Clavicle_-_animation.gif)
- [Clavicle - close-up - animation](https://commons.wikimedia.org/wiki/File:Clavicle_-_close-up_-_animation.gif)
- [Scapula - posterior view](https://commons.wikimedia.org/wiki/File:Scapula_-_posterior_view.png)
- [Scapula - lateral view](https://commons.wikimedia.org/wiki/File:Scapula_-_lateral_view.png)
- [Scapula - anterior view](https://commons.wikimedia.org/wiki/File:Scapula_-_anterior_view.png)
- [Scapula - animation](https://commons.wikimedia.org/wiki/File:Scapula_-_animation.gif)
- [Left scapula - close-up - animation](https://commons.wikimedia.org/wiki/File:Left_scapula_-_close-up_-_animation.gif)

位置图上的中文标注为本课所加。转动 GIF 已转成 H.264 MP4，便于在网页和微信中播放。

## 格雷氏解剖学（1918）

艺术家：Henry Vandyke Carter

来源：Gray's Anatomy, 1918，公有领域

- [Gray200](https://commons.wikimedia.org/wiki/File:Gray200.png) 锁骨
- [Gray201](https://commons.wikimedia.org/wiki/File:Gray201.png) 胸锁关节
- [Gray202](https://commons.wikimedia.org/wiki/File:Gray202.png) 左肩胛骨肋面
- [Gray203](https://commons.wikimedia.org/wiki/File:Gray203.png) 左肩胛骨背面

## 页面上的三维查看器

`js/model-viewer.min.js` 是 [@google/model-viewer 4.4.0](https://github.com/google/model-viewer/tree/v4.4.0) 的官方打包文件，从 `https://unpkg.com/@google/model-viewer@4.4.0/dist/model-viewer.min.js` 原样放入仓库，只删掉了末尾指向不存在的 `.map` 的一行。GitHub Pages 不需要构建，也不从外网加载这段脚本。

随包的 `js/model-viewer.LICENSE` 是 Apache License 2.0。打包文件开头另有 Google LLC 的 BSD-3-Clause 声明，其中的 Three.js 部分为 MIT（Copyright 2010-2026 Three.js Authors）。这些声明都留在文件里。

全身骨骼和肩带联动另外用了 [Three.js r170.0](https://github.com/mrdoob/three.js/releases/tag/r170) 的 `build/three.module.min.js`，原样放在 `js/vendor/three.module.min.js`，许可证全文是 `js/vendor/three.LICENSE`（MIT，Copyright © 2010-2024 three.js authors）。页面不从 CDN 加载它。关节运动是本仓库自己的 `js/shoulder-view.js`，不是模型自带的动画。

## 页面文字

因使用了 CC BY-SA 2.1 JP 的影像，本仓库中的讲解文字与页面编排亦按 [CC BY-SA 2.1 JP](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en) 共享。上面两个 GLB 文件单独适用 CC BY 4.0。
