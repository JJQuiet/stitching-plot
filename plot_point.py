from PIL import Image
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.pyplot as plt
import numpy as np
import json

# 百度地图反查坐标
lng_min, lng_max = 116.47336815598118, 117.09858879092577
# 画布尺寸
width, height = 8704, 12800
edge_data = {
    "left_vertical": [
        [0, 32.681013624774415],
        [908, 32.62570201054958],
        [2177, 32.54859735618937],
        [3311, 32.47954352790317],
        [5046, 32.373727813700874],
        [6893, 32.26094766246598],
        [8613,32.15591296989717],
        [12800, 31.899750472480704]
    ]
}
# 纬度转换为y坐标，为了避免纬度跨度过大，这里分成多个区间是从而减小纬度与距离的非线性关系导致的误差
def lat_to_y(lat,name):
    left_vertical = edge_data["left_vertical"]
    a, b, c, d = None, None, None, None
    # 寻找比给定纬度 x 小且最接近的纬度值 a
    for i in range(len(left_vertical) - 1):
        if left_vertical[i][1] > lat >= left_vertical[i + 1][1]:
            a, b = left_vertical[i][1], left_vertical[i][0]
            c, d = left_vertical[i + 1][1], left_vertical[i + 1][0]
            break
    # 计算表达式的值
    result = 0
    if a is not None and c is not None:
        result = b + (lat - a) / (c - a) * (d - b)
        result = int(result)
    return result

# 转换函数
def lnglat_to_xy(lng, lat,name):
    lng = float(lng)
    lat = float(lat)
    #region 方法一
    # x = (lng - lng_min) / (lng_max - lng_min) * width
    # y = (lat - lat_min) / (lat_max - lat_min) * height
    # return x, y  
    # endregion
    #region 方法二   
    x = (lng - lng_min) / (lng_max - lng_min) * width
    # y = height - lat_to_y(lat,name)
    y = lat_to_y(lat,name)
     
    return int(x),y
    #endregion
def filter_points():
    # Load the JSON data from the file
    file_path = './data.json'
    # Read the JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    filtered_points = []
    alarm_points = []
    evacuate_points = []
    civil_defense_engineering_points = []
    for group in data:
        for point in group:
            if point.get('status') == '防空警报点':
                alarm_points.append(point)
            elif ( point.get('status') == '保障点' or point.get('status') == '集结点' or point.get('status') == '经济目标' )or( point.get('status') == '疏散地域' and point.get('value') )or( point.get('status') == '隐蔽地域' and point.get('value')):
                evacuate_points.append(point)
            elif point.get('status') == '人防点':
                civil_defense_engineering_points.append(point)
    return [alarm_points,evacuate_points,civil_defense_engineering_points]
filtered_points = filter_points()  # 获取过滤后的点。为了体现函数功能模块化，写函数，再在这里调用

name_map = ['防空警报点','疏散点','人防点']
# 绘制点
for i,points in enumerate(filtered_points):
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)  # 通过调整figsize和dpi来控制最终图像的像素大小
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis('on')  # 显示坐标轴
    points_array = []
    for point in points:
        try:
            # 尝试将字符串转换为浮点数
            if point['value'][0] == '':
                x = 0
            else:
                x = float(point['value'][0])
            if point['value'][1] == '':
                y = 0
            else:
                y = float(point['value'][1])
            points_array.append([x, y])
        except ValueError:
            # 如果转换失败，打印错误并继续处理下一个点
            print(f"无法转换：{point['value']}，跳过该点。")
    points_arr = np.array(points_array)
    #region 距离判断
    # 计算每个点与其他点的欧氏距离
    distances = np.sqrt(((points_arr[:, np.newaxis, :] - points_arr) ** 2).sum(axis=2))
    # 计算y轴距离的绝对值
    y_distances_abs = np.abs(points_arr[:, np.newaxis, 1] - points_arr[:, 1])
    # 设置阈值  这个值是通过在百度地图坐标反查两个人防点的纬度差值得到的
    threshold = 0.000608 
    # 找出y轴距离绝对值超过阈值的点对位置
    exceed_threshold_indices = y_distances_abs > threshold
    # 对于这些点对，将它们之间的距离设置为一个较大的值,大于distances数组中的任何其他值
    extra_distance = distances.max() + 1  # 确保大于所有现有距离的值
    distances[exceed_threshold_indices] = extra_distance
    #endregion 
    # 忽略距离为0的情况（即点与其自身的距离）
    distances[distances == 0] = np.inf
    # 找到每个点最近邻的索引
    nearest_neighbors = np.argmin(distances, axis=1)
    count = 0
    for j,point in enumerate(points):
        # 创建画布
        x,y = point['value'][0],point['value'][1]
        if x== '' or y== '':
            continue
        count += 1
        x, y = lnglat_to_xy(x, y,point)
        # 绘制点
        ax.plot(x, y, 'o', color='red')
        # 绘制文本
        # 检查最近邻的x坐标与当前点比较，来决定文本的对齐方式
        text_horizontal_deviation = 0
        text_vertical_deviation = 4
        if points_arr[nearest_neighbors[j]][0] > float(point['value'][0]):
            ha = 'right'
            text_horizontal_deviation = -4
        else:
            ha = 'left'
            text_horizontal_deviation = 4
        ax.text(x+text_horizontal_deviation, y+text_vertical_deviation, point['name'], fontsize=12, ha=ha)
        # 加载并绘制Logo
        try:
            # 使用rfind从右侧找到第一个'/'的位置
            pos = point['symbol'].rfind('/')
            # 使用切片操作截取这个位置之后的所有字符
            # rfind如果没有找到匹配项会返回-1，在这种情况下，s[pos+1:]将返回整个字符串
            logo_path = './icon/' + point['symbol'][pos+1:] if pos != -1 else point['symbol']
            logo = Image.open(logo_path)
            logo = np.array(logo)
            imagebox = OffsetImage(logo, zoom=0.3)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.6, -0.2))
            ax.add_artist(ab)
        except Exception as e:
            print(f"Error loading logo for {point['name']}: {e}")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    try:
        plt.savefig('./'+name_map[i]+'图层.tif', dpi=100,transparent=True) # 保存的图像分辨率为8704x12800
    except Exception as e:
        print(f"Error saving the image: {e}")
    plt.close()
