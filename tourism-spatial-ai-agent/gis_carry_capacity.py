# gis_carry_capacity.py 客流承载力&季节拥挤度筛选模块
# 适配多代家庭文旅场景：根据季节热度、用户拥挤耐受阈值过滤高拥挤景点
import pandas
import numpy
import geopandas as gpd
from shapely.geometry import Point

# ----------------------1. 复用标准模拟数据集（字段严格对齐data&api-design.md）----------------------
# 完整复用前面GIS脚本统一POI字段：name/type/traffic_weight/cluster_density/season_popularity/geometry
poi_raw_data = [
    {
        "name": "景区A",
        "type": "自然风景",
        "traffic_weight": 0.759968,
        "cluster_density": 0.62,
        "season_popularity": 0.82,  # 季节热度：0~1，数值越高客流越拥挤
        "geometry": Point(113.25, 23.12)
    },
    {
        "name": "景区B",
        "type": "人文古迹",
        "traffic_weight": 0.000000,
        "cluster_density": 0.21,
        "season_popularity": 0.95,  # 旺季极高客流，拥挤度超标
        "geometry": Point(113.27, 23.14)
    },
    {
        "name": "休闲乐园",
        "type": "休闲乐园",
        "traffic_weight": 1.000000,
        "cluster_density": 0.88,
        "season_popularity": 0.68,
        "geometry": Point(113.23, 23.10)
    }
]
# 构建基础GeoDataFrame，统一WGS84坐标系
poi_gdf = gpd.GeoDataFrame(poi_raw_data, crs="EPSG:4326")
# 统一转换CGCS2000平面投影，和其他GIS脚本坐标系保持一致
poi_gdf = poi_gdf.to_crs("EPSG:4547")

# ----------------------2. 核心承载力筛选函数（入参适配AI Agent调用）----------------------
def filter_overcrowd_poi(poi_dataset, crowd_tolerance=0.9):
    """
    客流拥挤过滤函数
    :param poi_dataset: 完整POI空间数据集（含season_popularity字段）
    :param crowd_tolerance: 用户拥挤耐受阈值 0~1，数值越大能接受越拥挤场景
    :return: 过滤后低拥挤度干净POI数据集（字段无增减，完全匹配规范）
    """
    # 筛选：保留季节热度 ≤ 用户耐受阈值的景点，剔除超高拥挤点位
    clean_poi = poi_dataset[poi_dataset["season_popularity"] <= crowd_tolerance].copy()
    return clean_poi

# ----------------------3. 模拟用户输入参数（可由上层poi_score_agent.py传入）----------------------
# 场景：多代家庭出游，老人小孩不耐拥挤，耐受阈值设为0.9
user_tolerance = 0.9
# 执行拥挤过滤
filtered_poi_result = filter_overcrowd_poi(poi_gdf, crowd_tolerance=user_tolerance)

# ----------------------4. 控制台输出结果，用于演示校验----------------------
print("===== 客流承载力筛选前全部景点 =====")
print(poi_gdf[["name", "type", "season_popularity"]].to_string(index=False))

print(f"\n===== 拥挤耐受阈值：{user_tolerance}，筛选后低拥挤景点 =====")
print(filtered_poi_result[["name", "type", "season_popularity"]].to_string(index=False))

print("\n✅ 客流承载力筛选完成，已剔除超拥挤景点，输出字段完全匹配设计规范")