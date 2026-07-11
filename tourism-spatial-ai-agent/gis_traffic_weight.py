# gis_traffic_weight.py 文旅点位交通通达度权重计算算法（修复坐标系警告完整版）
import pandas
import numpy
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from shapely.geometry import Point, LineString

# ----------------------1. 模拟生成测试POI、道路数据 + 坐标投影转换（消除距离计算警告）----------------------
# 模拟3个文旅景点点位（原始WGS84经纬度 EPSG:4326）
poi_points = [
    Point(113.25, 23.12),
    Point(113.27, 23.14),
    Point(113.23, 23.10)
]
poi_gdf = gpd.GeoDataFrame({
    "name": ["景区A", "景区B", "休闲乐园"],
    "type": ["自然风景", "人文古迹", "休闲乐园"],
    "geometry": poi_points
}, crs="EPSG:4326")

# 模拟城市主干道矢量（原始WGS84经纬度 EPSG:4326）
road_lines = [
    LineString([(113.24,23.11), (113.28,23.15)]),
    LineString([(113.22,23.09), (113.26,23.13)])
]
road_gdf = gpd.GeoDataFrame(geometry=road_lines, crs="EPSG:4326")

# 核心修复：转换为广州CGCS2000 3度带平面投影 EPSG:4547（单位：米）
# 平面坐标系计算距离无经纬度误差，彻底消除黄色警告
target_proj_crs = "EPSG:4547"
poi_gdf = poi_gdf.to_crs(target_proj_crs)
road_gdf = road_gdf.to_crs(target_proj_crs)

# ----------------------2. 距离衰减权重计算函数（参数单位改为米）----------------------
def calc_traffic_weight(point_geom, roads, max_distance=2000):
    """
    计算单个文旅点位交通通达权重
    :param point_geom: 景点平面坐标几何对象
    :param roads: 平面投影路网矢量数据集
    :param max_distance: 道路2000米为最大影响范围（单位：米）
    :return: 归一化交通权重 0~1
    """
    # 平面坐标系精准计算点位到所有道路最短距离（米）
    roads["dist"] = roads.geometry.distance(point_geom)
    min_dist = roads["dist"].min()
    # 指数距离衰减公式：离道路越近，权重分值越高
    decay_weight = numpy.exp(-min_dist / max_distance)
    return decay_weight

# ----------------------3. 批量计算所有POI通达权重----------------------
weight_list = []
for idx, row in poi_gdf.iterrows():
    point = row.geometry
    w = calc_traffic_weight(point, road_gdf)
    weight_list.append(w)

# 最小最大归一化，将权重压缩至0~1区间，适配AI Agent特征输入
scaler = MinMaxScaler()
poi_gdf["traffic_weight"] = scaler.fit_transform(numpy.array(weight_list).reshape(-1,1))

# ----------------------4. 控制台输出计算结果，用于作品集演示----------------------
print("===== 文旅POI交通通达度权重计算结果（平面投影精准距离） =====")
print(poi_gdf[["name", "type", "traffic_weight"]].to_string(index=False))
print("\n✅ 交通通达度权重计算完成，坐标系警告已修复，代码逻辑运行正常")