# poi_score_agent.py 文旅景点综合打分智能体
import pandas
import numpy
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from shapely.geometry import Point, LineString

# ====================== 1. 基础模拟数据（复用交通权重+新增聚类密度、类型偏好） ======================
# 景点坐标 WGS84
poi_points = [
    Point(113.25, 23.12),
    Point(113.27, 23.14),
    Point(113.23, 23.10)
]
poi_raw = gpd.GeoDataFrame({
    "name": ["景区A", "景区B", "休闲乐园"],
    "type": ["自然风景", "人文古迹", "休闲乐园"],
    "geometry": poi_points,
    "cluster_density": [0.62, 0.21, 0.88]  # gis_cluster.py输出：周边配套POI密度0~1
}, crs="EPSG:4326")

# 道路矢量
road_lines = [
    LineString([(113.24,23.11), (113.28,23.15)]),
    LineString([(113.22,23.09), (113.26,23.13)])
]
road_gdf = gpd.GeoDataFrame(geometry=road_lines, crs="EPSG:4326")

# 坐标投影转换 消除距离计算警告
target_proj_crs = "EPSG:4547"
poi_gdf = poi_raw.to_crs(target_proj_crs)
road_gdf = road_gdf.to_crs(target_proj_crs)

# ====================== 2. 复用交通通达权重计算函数 ======================
def calc_traffic_weight(point_geom, roads, max_distance=2000):
    roads["dist"] = roads.geometry.distance(point_geom)
    min_dist = roads["dist"].min()
    decay_weight = numpy.exp(-min_dist / max_distance)
    return decay_weight

# 批量计算交通权重
weight_list = []
for _, row in poi_gdf.iterrows():
    w = calc_traffic_weight(row.geometry, road_gdf)
    weight_list.append(w)
scaler = MinMaxScaler()
poi_gdf["traffic_weight"] = scaler.fit_transform(numpy.array(weight_list).reshape(-1,1))

# ====================== 3. 景点类型偏好分值配置（可根据游客偏好动态调整） ======================
type_score_map = {
    "自然风景": 0.75,
    "人文古迹": 0.65,
    "休闲乐园": 0.90
}
poi_gdf["type_score"] = poi_gdf["type"].map(type_score_map)

# ====================== 4. 多维度加权融合 计算综合推荐得分 ======================
# 权重配比：交通40% / 配套聚类密度35% / 景点类型偏好25%
weight_traffic = 0.4
weight_density = 0.35
weight_type = 0.25

# 0~1原始综合分
poi_gdf["combine_raw"] = (
    weight_traffic * poi_gdf["traffic_weight"]
    + weight_density * poi_gdf["cluster_density"]
    + weight_type * poi_gdf["type_score"]
)
# 映射到0~10分 便于游客直观查看星级
poi_gdf["total_score"] = round(poi_gdf["combine_raw"] * 10, 2)

# 按综合得分降序排序
result_df = poi_gdf[["name", "type", "traffic_weight", "cluster_density", "type_score", "total_score"]].sort_values(by="total_score", ascending=False)

# ====================== 5. Agent输出推荐结果 ======================
print("===== 文旅AI智能体 - 景点综合推荐打分表（降序） =====")
print(result_df.to_string(index=False))
print("\n===== AI Agent 优先推荐TOP1景点 =====")
top1 = result_df.iloc[0]
print(f"推荐景点：{top1['name']}（{top1['type']}），综合评分：{top1['total_score']}/10")
print(f"推荐理由：交通通达权重{round(top1['traffic_weight'],3)}，周边配套密度{top1['cluster_density']}，匹配休闲游玩偏好")

print("\n✅ 文旅多维度空间打分Agent执行完成，可对接前端推荐展示模块")