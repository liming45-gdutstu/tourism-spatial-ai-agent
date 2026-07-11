# poi_api_crawl.py 高德地图Web服务API合规POI数据采集脚本
# 严格遵循memory-bank/data&api-design.md POI数据表结构规范
# 仅调用高德官方Web服务接口，无任何爬虫逻辑
# 输出格式：CSV数据表 + EPSG:4326标准GIS shp矢量文件

import requests
import time
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# ====================== 1. 全局配置参数（用户需修改此处） ======================
AMAP_API_KEY = ""
TARGET_CITY = "广州"
SEARCH_KEYWORDS = ["景区", "公园", "文旅景点", "休闲乐园", "人文古迹"]
OUTPUT_DIR = "poi_data"
# 广州地理坐标过滤范围（EPSG:4326 WGS84）
LNG_MIN, LNG_MAX = 112.0, 114.0
LAT_MIN, LAT_MAX = 22.0, 24.0

# ====================== 2. 季节热度分值映射表 ======================
SEASON_POP_MAP = {
    "春季": 4,
    "夏季": 7,
    "秋季": 6,
    "冬季": 3,
    "法定节假日": 10
}

# ====================== 3. 景点类型与用户偏好标签映射 ======================
SCENIC_TYPE_MAP = {
    "风景名胜": "自然风光",
    "公园广场": "自然风光",
    "旅游景点": "自然风光",
    "文化古迹": "人文古迹",
    "休闲娱乐": "休闲乐园",
    "游乐园": "休闲乐园",
    "博物馆": "人文古迹",
    "展览馆": "人文古迹",
    "寺庙道观": "人文古迹",
    "度假村": "休闲乐园",
    "动物园": "休闲乐园",
    "植物园": "自然风光",
    "海滨浴场": "自然风光",
    "森林公园": "自然风光"
}

def init_output_directory():
    """初始化输出目录，确保poi_data文件夹存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ 创建数据输出目录: {OUTPUT_DIR}")
    else:
        print(f"✅ 输出目录已存在: {OUTPUT_DIR}")

def call_amap_api(keyword, city, page=1, page_size=50, max_retries=3):
    """
    调用高德地图Web服务place/text接口查询POI数据
    :param keyword: 搜索关键词
    :param city: 目标城市
    :param page: 当前页码
    :param page_size: 每页数量（最大50）
    :param max_retries: 最大重试次数
    :return: API返回的JSON数据或空字典
    """
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "keywords": keyword,
        "city": city,
        "output": "json",
        "key": AMAP_API_KEY,
        "page": page,
        "offset": page_size,
        "extensions": "all"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "1":
                return result
            elif result.get("status") == "0":
                print(f"⚠️  API调用失败，错误信息: {result.get('info', '未知错误')}")
                if attempt < max_retries - 1:
                    print(f"🔄 等待5秒后重试，第{attempt+2}/{max_retries}次")
                    time.sleep(5)
                    continue
            break
        except requests.exceptions.RequestException as e:
            print(f"⚠️  网络请求异常: {str(e)}")
            if attempt < max_retries - 1:
                print(f"🔄 等待5秒后重试，第{attempt+2}/{max_retries}次")
                time.sleep(5)
                continue
    
    return {}

def extract_poi_data(result, keyword):
    """
    从API返回结果中提取POI数据，转换为标准字段格式
    :param result: API返回的JSON数据
    :param keyword: 搜索关键词（用于标记来源）
    :return: 提取后的POI字典列表
    """
    pois = []
    if not result or "pois" not in result:
        return pois
    
    for item in result["pois"]:
        try:
            # 提取经纬度并转换为浮点数
            location = item.get("location", "")
            if not location:
                continue
            lng_str, lat_str = location.split(",")
            lng = float(lng_str)
            lat = float(lat_str)
            
            # 经纬度异常过滤：只保留广州范围内的有效坐标
            if not (LNG_MIN <= lng <= LNG_MAX and LAT_MIN <= lat <= LAT_MAX):
                print(f"📋 过滤异常坐标: {item.get('name')} ({lng}, {lat}) - 超出广州范围")
                continue
            
            # 提取景点类型，映射到用户偏好标签
            raw_type = item.get("type", "")
            scenic_type = "其他"
            for key, value in SCENIC_TYPE_MAP.items():
                if key in raw_type:
                    scenic_type = value
                    break
            
            # 构建标准POI字典，字段严格对齐data&api-design.md
            poi = {
                "poi_id": item.get("id", ""),
                "name": item.get("name", ""),
                "lng": lng,
                "lat": lat,
                "scenic_type": scenic_type,
                "address": item.get("address", ""),
                "adname": item.get("adname", ""),
                "pname": item.get("pname", ""),
                "raw_type": raw_type,
                "tel": item.get("tel", ""),
                "keyword_source": keyword
            }
            pois.append(poi)
        except Exception as e:
            print(f"⚠️  解析POI数据异常: {str(e)}")
            continue
    
    return pois

def deduplicate_by_poi_id(poi_list):
    """
    根据poi_id去重，保留第一个出现的记录
    :param poi_list: 原始POI列表
    :return: 去重后的POI列表
    """
    seen_ids = set()
    unique_pois = []
    
    for poi in poi_list:
        poi_id = poi["poi_id"]
        if poi_id and poi_id not in seen_ids:
            seen_ids.add(poi_id)
            unique_pois.append(poi)
    
    print(f"🔍 去重完成: 原始{len(poi_list)}条 → 去重后{len(unique_pois)}条")
    return unique_pois

def add_season_popularity(poi_df):
    """
    为每个POI绑定季节热度字段season_popularity
    :param poi_df: POI数据DataFrame
    :return: 添加季节热度字段后的DataFrame
    """
    poi_df["season_popularity"] = poi_df.apply(lambda _: SEASON_POP_MAP.copy(), axis=1)
    poi_df["avg_traffic_min"] = 15
    poi_df["cluster_id"] = -1
    
    print("✅ 已为所有POI绑定季节热度分值、通勤时长、聚类编号字段")
    return poi_df

def export_to_csv(poi_df, filename="clean_poi_api.csv"):
    """
    导出POI数据为CSV文件
    :param poi_df: POI数据DataFrame
    :param filename: 输出文件名
    """
    output_path = os.path.join(OUTPUT_DIR, filename)
    poi_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"📊 CSV文件已导出: {output_path}")

def export_to_shp(poi_df, filename="poi_tourism_raw.shp"):
    """
    导出POI数据为EPSG:4326标准GIS shp矢量文件
    :param poi_df: POI数据DataFrame
    :param filename: 输出文件名
    """
    # 创建geometry列，转换为Point对象
    geometry = [Point(xy) for xy in zip(poi_df["lng"], poi_df["lat"])]
    gdf = gpd.GeoDataFrame(poi_df, geometry=geometry, crs="EPSG:4326")
    
    # 导出为shp文件
    output_path = os.path.join(OUTPUT_DIR, filename)
    gdf.to_file(output_path, encoding="utf-8")
    print(f"🗺️  SHP矢量文件已导出: {output_path}")

def main():
    """主函数：执行完整POI数据采集流程"""
    # 1. 检查API Key是否已配置
    if not AMAP_API_KEY:
        print("❌ 错误：请先在脚本顶部配置AMAP_API_KEY")
        print("🔗 获取地址：https://lbs.amap.com/dev/key/app")
        return
    
    # 2. 初始化输出目录
    init_output_directory()
    
    # 3. 遍历所有关键词进行搜索
    all_pois = []
    for keyword in SEARCH_KEYWORDS:
        print(f"\n============= 开始搜索关键词: {keyword} =============")
        
        page = 1
        total_count = 0
        while True:
            # 接口限流延时：每请求间隔0.5秒，遵守高德API调用频率限制
            time.sleep(0.5)
            
            # 调用高德API
            result = call_amap_api(keyword, TARGET_CITY, page=page)
            
            if not result:
                break
            
            # 提取POI数据
            pois = extract_poi_data(result, keyword)
            all_pois.extend(pois)
            
            # 获取总数和当前页数量
            count = int(result.get("count", 0))
            total = int(result.get("total", 0))
            total_count += count
            
            print(f"📄 第{page}页：获取{count}条POI，累计{total_count}条")
            
            # 判断是否还有下一页
            if total_count >= total or count == 0:
                break
            
            page += 1
    
    # 4. POI去重
    unique_pois = deduplicate_by_poi_id(all_pois)
    
    # 5. 转换为DataFrame并添加标准字段
    poi_df = pd.DataFrame(unique_pois)
    poi_df = add_season_popularity(poi_df)
    
    # 6. 输出CSV和SHP文件
    export_to_csv(poi_df)
    export_to_shp(poi_df)
    
    # 7. 输出统计信息
    print(f"\n🎉 POI数据采集完成！")
    print(f"📍 目标城市: {TARGET_CITY}")
    print(f"🔖 搜索关键词: {', '.join(SEARCH_KEYWORDS)}")
    print(f"📈 采集总数: {len(all_pois)}条")
    print(f"🔍 去重后: {len(unique_pois)}条")
    print(f"📁 输出目录: {os.path.abspath(OUTPUT_DIR)}")
    print(f"\n✅ 数据格式完全对齐data&api-design.md，可直接输入第一阶段main_gis_pipeline.py全链路GIS流水线")

if __name__ == "__main__":
    main()