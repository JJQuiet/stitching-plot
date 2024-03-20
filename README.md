# 实现过程

### 环境配置

在项目根目录下建立虚拟环境

```
pip -m venv venv
```

终端进入虚拟环境（以powershell为例）在项目根目录下执行：

```
.\venv\Scripts\Activate.ps1
```

安装依赖包

```
pip install -r requirements.txt
```

### 数据获取

从地图前端如Allmap.ts中获取点位数据，打印到浏览器控制台，复制到data.json文件中

通过百度地图坐标反查或者在地图前端监听地图点击事件打印点坐标，获取到寿县地图四个角的坐标，存入data_edge.txt中

### 得到一张完整地图

修改image_stitching.py中的地图瓦片路径，执行

```
py image_stitching.py
```

### 点位图层

执行

```
py plot_point.py
```

获取到点位图层

最后在photoshop中将点位图层放置到完整地图图层上，再加上标题。

# 关键思路
