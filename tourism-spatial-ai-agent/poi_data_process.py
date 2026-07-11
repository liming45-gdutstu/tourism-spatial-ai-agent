# poi_data_process.py
# 景点POI数据预处理模块
# 匹配memory-bank/data&api-design.md POI数据表结构规范
# 依赖库：pandas、geopandas
import pandas as pd
import geopandas as gpd

def load_amap_raw_data(file_path: str) -> pd.DataFrame:
    """
    读取高德POI原始接口返回csv数据
    :param file_path: 高德POI原始数据文件路径
    :return: 原始未清洗POI数据集
    """
    raw_df = pd.read_csv(file_path, encoding="utf-8")
    return raw_df

def clean_poi_data(raw_df: pd.DataFrame, target_city: str) -> pd.DataFrame:
    """
    原始POI数据清洗、字段映射，转换为标准POI数据表结构
    :param raw_df: 高德原始数据集
    :param target_city: 目标过滤城市名称
    :return: 清洗完成、字段对齐data&api-design.md的标准POI表
    """
    # 1. 筛选目标城市数据，复制副本避免修改原数据
    city_filter_df = raw_df[raw_df["city"] == target_city].copy()

    # 2. 字段重命名，严格对齐data&api-design.md底层POI数据表字段
    city_filter_df.rename(columns={
        "poi_id": "poi_id",
        "name": "name",
        "longitude": "lng",
        "latitude": "lat",
        "scenic_type": "scenic_type",
        "neighbor_traffic_min": "avg_traffic_min"
    }, inplace=True)

    # 3. 相邻通勤时长统一转为int类型（单位：分钟）
    city_filter_df["avg_traffic_min"] = city_filter_df["avg_traffic_min"].astype(int)

    # 4. 分季节拥挤度字典绑定，匹配season_popularity字段定义
    season_pop_map = {
        "春季": 3,
        "夏季": 8,
        "秋季": 5,
        "冬季": 2,
        "法定节假日": 10
    }
    city_filter_df["season_popularity"] = [season_pop_map for _ in range(len(city_filter_df))]

    # 5. 初始化Kmeans聚类编号，默认-1，后续gis_cluster.py更新赋值
    city_filter_df["cluster_id"] = -1

    # 6. 按景点名称去重，保留第一条有效数据
    city_filter_df.drop_duplicates(subset=["name"], keep="first", inplace=True)

    return city_filter_df

def export_standard_poi(clean_df: pd.DataFrame, save_path: str):
    """
    输出标准化POI数据集，用于后续四大GIS模块输入
    :param clean_df: 清洗完成的标准POI数据
    :param save_path: 数据集csv保存路径
    """
    # 导出标准csv，不写入索引列，兼容中文显示
    clean_df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"标准POI数据表已导出，存储路径：{save_path}")

# 本地测试入口（单独运行验证完整清洗流程）
if __name__ == "__main__":
    # 测试参数示例
    test_file = "amap_raw_scenic.csv"
    city = "广州"
    save_output = "standard_poi_dataset.csv"

    # 执行完整数据预处理流程
    raw_data = load_amap_raw_data(test_file)
    standard_poi = clean_poi_data(raw_data, city)
    export_standard_poi(standard_poi, save_output)
    print("POI数据预处理完整业务逻辑运行完成，字段完全匹配data&api-design.md规范，可接入Kmeans聚类模块")