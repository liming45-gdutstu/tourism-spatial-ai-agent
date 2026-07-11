# gis_cluster.py
# GIS模块2：景点Kmeans空间片区聚类
# 输入：poi_data_process.py导出的 standard_poi_dataset.csv
# 输出：带cluster_id片区编号的更新后标准POI数据表
# 依赖：pandas, geopandas, scikit-learn
import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans

def load_standard_poi(file_path: str) -> pd.DataFrame:
    """
    读取预处理完成的标准POI数据集
    :param file_path: 标准POI csv文件路径
    :return: 含lng/lat坐标的景点数据表
    """
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    return df

def kmeans_scenic_cluster(poi_df: pd.DataFrame, cluster_num: int = 8) -> pd.DataFrame:
    """
    Kmeans空间聚类，按经纬度划分景点片区，生成cluster_id
    :param poi_df: 标准POI数据表
    :param cluster_num: 自动划分片区数量，默认8个片区
    :return: 新增/更新cluster_id字段的POI表
    """
    # 提取经纬度坐标作为聚类特征
    coord_data = poi_df[["lng", "lat"]].values
    # 初始化Kmeans聚类模型
    kmeans_model = KMeans(n_clusters=cluster_num, random_state=42)
    # 执行聚类，生成片区编号
    poi_df["cluster_id"] = kmeans_model.fit_predict(coord_data)
    return poi_df

def export_cluster_poi(clean_df: pd.DataFrame, save_path: str):
    """
    导出带聚类片区编号的POI数据表，供给交通权重/客流承载力模块
    :param clean_df: 完成聚类标记的POI数据
    :param save_path: 导出csv保存路径
    """
    clean_df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"聚类片区分配完成，更新数据表已导出至 {save_path}")

# 本地独立测试入口
if __name__ == "__main__":
    input_poi_file = "standard_poi_dataset.csv"
    output_cluster_file = "poi_with_cluster.csv"
    split_cluster_count = 8

    # 完整聚类流程
    poi_data = load_standard_poi(input_poi_file)
    clustered_poi = kmeans_scenic_cluster(poi_data, cluster_num=split_cluster_count)
    export_cluster_poi(clustered_poi, output_cluster_file)
    print("Kmeans景点片区聚类模块运行完成，已为所有景点分配片区cluster_id")