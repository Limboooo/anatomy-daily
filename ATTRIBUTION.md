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

## 页面文字

因使用了 CC BY-SA 2.1 JP 的影像，本仓库中的讲解文字与页面编排亦按 [CC BY-SA 2.1 JP](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en) 共享。上面两个 GLB 文件单独适用 CC BY 4.0。
