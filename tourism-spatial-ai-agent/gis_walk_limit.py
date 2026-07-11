# gis_walk_limit.py 分人群单日步行体力约束筛选模块
# 适配多代家庭：区分成人/老人/儿童步行耐受上限，剔除单日超步行负荷景点
import pandas
import numpy
import geopandas as gpd
from shapely.geometry import Point

# ----------------------1. 标准统一POI数据集（字段完全对齐规范文档）----------------------
poi_raw_data = [
    {
        "name": "景区A",
        "type": "自然风景",
        "traffic_weight": 0.759968,
        "cluster_density": 0.62,
        "season_popularity": 0.82,
        "walk_distance": 1200,  # 景点内部游览步行距离，单位：米
        "geometry": Point(113.25, 23.12)
    },
    {
        "name": "景区B",
        "type": "人文古迹",
        "traffic_weight": 0.000000,
        "cluster_density": 0.21,
        "season_popularity": 0.95,
        "walk_distance": 3800,  # 超大步行里程，老人/儿童无法承受
        "geometry": Point(113.27, 23.14)
    },
    {
        "name": "休闲乐园",
        "type": "休闲乐园",
        "traffic_weight": 1.000000,
        "cluster_density": 0.88,
        "season_popularity": 0.68,
        "walk_distance": 1600,
        "geometry": Point(113.23, 23.10)
    }
]
# 构建空间数据表，统一坐标系
poi_gdf = gpd.GeoDataFrame(poi_raw_data, crs="EPSG:4326")
poi_gdf = poi_gdf.to_crs("EPSG:4547")

# ----------------------2. 人群步行阈值配置字典（业务分层）----------------------
# 单位：单日可承受最大步行米数
walk_threshold_map = {
    "adult": 4000,      # 成人单日上限4000米
    "elder": 2000,      # 老人单日上限2000米
    "child": 1800       # 儿童单日上限1800米
}

# ----------------------3. 核心步行约束筛选函数----------------------
def filter_over_walk_poi(poi_dataset, crowd_type="elder"):
    """
    根据人群类型过滤超步行负荷景点
    :param poi_dataset: 标准POI数据集，含walk_distance字段
    :param crowd_type: 人群类型：adult/elder/child
    :return: 过滤后符合体力耐受的干净POI数据集
    """
    max_walk = walk_threshold_map[crowd_type]
    # 保留游览步行距离 ≤ 人群耐受上限的景点
    fit_poi = poi_dataset[poi_dataset["walk_distance"] <= max_walk].copy()
    return fit_poi

# ----------------------4. 模拟业务入参：多代家庭出行（含老人，选用elder阈值）----------------------
user_crowd = "elder"
filtered_walk_poi = filter_over_walk_poi(poi_gdf, crowd_type=user_crowd)

# ----------------------5. 控制台输出校验结果----------------------
print("===== 全部景点原始步行距离数据 =====")
print(poi_gdf[["name", "type", "walk_distance"]].to_string(index=False))

print(f"\n===== 当前人群：{user_crowd}，步行耐受上限{walk_threshold_map[user_crowd]}米，筛选后适配景点 =====")
print(filtered_walk_poi[["name", "type", "walk_distance"]].to_string(index=False))

print("\n✅ 人群步行体力约束筛选完成，输出字段完全匹配设计规范")