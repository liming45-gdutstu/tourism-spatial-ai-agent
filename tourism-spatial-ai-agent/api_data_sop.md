# 高德API POI数据采集处理SOP

## 1. 前置准备

### 1.1 高德开发者账号注册

1. 访问高德开放平台：https://lbs.amap.com/
2. 注册/登录个人开发者账号
3. 创建应用，申请Web服务API Key
4. 确保Key权限包含「Web服务」接口调用权限

### 1.2 本地环境依赖安装

```bash
pip install requests pandas geopandas shapely fiona
```

| 依赖包    | 版本要求 | 用途说明                     |
| --------- | -------- | ---------------------------- |
| requests  | >=2.20   | 发送HTTP请求调用高德API      |
| pandas    | >=1.0    | 数据清洗、结构化处理         |
| geopandas | >=0.10   | GIS矢量数据处理、SHP文件导出 |
| shapely   | >=1.8    | 几何对象创建（Point）        |
| fiona     | >=1.8    | SHP文件读写支持              |

### 1.3 验证环境

运行 `python test_env.py` 确认所有依赖安装正常。

## 2. 参数配置说明

### 2.1 配置文件位置

编辑 `poi_api_crawl.py` 顶部配置区域：

```python
# ====================== 1. 全局配置参数（用户需修改此处） ======================
AMAP_API_KEY = ""          # 必填：填写你的高德Web服务API Key
TARGET_CITY = "广州"        # 必填：目标城市名称
SEARCH_KEYWORDS = ["景区", "公园", "文旅景点", "休闲乐园", "人文古迹"]  # 可增删
OUTPUT_DIR = "poi_data"    # 输出目录名
LNG_MIN, LNG_MAX = 112.0, 114.0  # 经度过滤范围
LAT_MIN, LAT_MAX = 22.0, 24.0    # 纬度过滤范围
```

### 2.2 参数说明

| 参数            | 类型   | 必填 | 默认值                                               | 说明                     |
| --------------- | ------ | ---- | ---------------------------------------------------- | ------------------------ |
| AMAP_API_KEY    | string | 是   | 空字符串                                             | 高德Web服务API密钥       |
| TARGET_CITY     | string | 是   | "广州"                                               | 目标城市中文名           |
| SEARCH_KEYWORDS | list   | 是   | ["景区", "公园", "文旅景点", "休闲乐园", "人文古迹"] | POI搜索关键词列表        |
| OUTPUT_DIR      | string | 否   | "poi_data"                                           | 输出文件存储目录         |
| LNG_MIN/MAX     | float  | 否   | 112.0/114.0                                          | 经度过滤区间（广州范围） |
| LAT_MIN/MAX     | float  | 否   | 22.0/24.0                                            | 纬度过滤区间（广州范围） |

## 3. 数据清洗规则

### 3.1 坐标过滤规则

- 仅保留经度在 [112.0, 114.0] 范围内的POI
- 仅保留纬度在 [22.0, 24.0] 范围内的POI
- 空坐标、格式异常的POI自动丢弃

### 3.2 去重规则

- 以高德POI唯一ID（`poi_id`）作为去重依据
- 保留第一次出现的记录，后续重复ID自动跳过
- 输出去重前后数量统计

### 3.3 类型映射规则

| 高德原始类型                       | 映射后用户偏好标签 |
| ---------------------------------- | ------------------ |
| 风景名胜、公园广场、旅游景点       | 自然风光           |
| 文化古迹、博物馆、展览馆、寺庙道观 | 人文古迹           |
| 休闲娱乐、游乐园、度假村、动物园   | 休闲乐园           |
| 海滨浴场、植物园、森林公园         | 自然风光           |
| 其他未匹配类型                     | 其他               |

### 3.4 季节热度绑定

为每条POI记录绑定 `season_popularity` 字段，值为字典类型：

```python
{
    "春季": 4,
    "夏季": 7,
    "秋季": 6,
    "冬季": 3,
    "法定节假日": 10
}
```

- 热度分值范围：0~10（数值越高表示该季节客流越大）
- 夏季/秋季为广州旅游旺季，热度较高
- 法定节假日为峰值，热度最高

## 4. 输出文件规范

### 4.1 CSV文件

**文件名**：`poi_data/clean_poi_api.csv`

**字段结构**（严格对齐data&api-design.md）：

| 字段名            | 数据类型 | 说明                                    |
| ----------------- | -------- | --------------------------------------- |
| poi_id            | string   | 高德POI唯一编号                         |
| name              | string   | 景点名称                                |
| lng               | float    | 经度（EPSG:4326）                       |
| lat               | float    | 纬度（EPSG:4326）                       |
| scenic_type       | string   | 景点分类（用户偏好标签）                |
| address           | string   | 详细地址                                |
| adname            | string   | 区县名称                                |
| pname             | string   | 省份名称                                |
| raw_type          | string   | 高德原始类型                            |
| tel               | string   | 联系电话                                |
| keyword_source    | string   | 搜索关键词来源                          |
| season_popularity | dict     | 分季节客流热度                          |
| avg_traffic_min   | int      | 相邻点位平均通勤时长（默认15分钟）      |
| cluster_id        | int      | 片区聚类编号（默认-1，后续GIS模块赋值） |

### 4.2 SHP矢量文件

**文件名**：`poi_data/poi_tourism_raw.shp`

**属性信息**：

- 坐标系：EPSG:4326（WGS84）
- 几何类型：Point（点要素）
- 属性字段：与CSV文件一致

**文件组成**：

- `.shp` - 几何数据
- `.shx` - 空间索引
- `.dbf` - 属性表
- `.prj` - 投影信息

### 4.3 数据流向

```
高德API → poi_api_crawl.py → [clean_poi_api.csv + poi_tourism_raw.shp] → main_gis_pipeline.py
```

## 5. 常见异常与排错方案

### 5.1 API Key错误

**现象**：运行时提示"API调用失败"，错误信息包含"INVALID_USER_KEY"

**解决方案**：

1. 检查 `AMAP_API_KEY` 是否正确填写
2. 确认Key已开通「Web服务」权限
3. 检查Key是否已过期或被封禁

### 5.2 网络连接失败

**现象**：提示"网络请求异常"或超时错误

**解决方案**：

1. 检查网络连接是否正常
2. 确认防火墙未阻止出站HTTP请求
3. 可尝试添加代理配置

### 5.3 数据量为0

**现象**：所有关键词搜索结果均为0条

**解决方案**：

1. 检查城市名称是否正确（如"广州"而非"广州市"）
2. 确认API Key权限正常
3. 尝试缩小搜索范围或更换关键词

### 5.4 SHP文件导出失败

**现象**：提示fiona相关错误

**解决方案**：

1. 确保已安装fiona：`pip install fiona`
2. Windows用户可能需要安装GDAL依赖
3. 尝试简化文件名，避免特殊字符

### 5.5 坐标异常

**现象**：输出数据中经纬度超出预期范围

**解决方案**：

1. 脚本已内置坐标过滤，异常坐标会自动过滤并打印日志
2. 如需调整范围，修改 `LNG_MIN/MAX` 和 `LAT_MIN/MAX` 参数

## 6. 运行步骤

### 步骤1：申请高德API Key

1. 访问 https://lbs.amap.com/dev/key/app
2. 创建应用，选择「Web服务」类型
3. 获取API Key

### 步骤2：安装依赖

```bash
pip install requests pandas geopandas shapely fiona
```

### 步骤3：运行采集脚本

```bash
python poi_api_crawl.py
```

### 步骤4：验证输出

检查 `poi_data/` 目录下是否生成：

- `clean_poi_api.csv` - 结构化数据表
- `poi_tourism_raw.shp` - GIS矢量文件

## 7. 模块验收标准

### 自动生成内容（已完成）

- [x] `poi_api_crawl.py` 采集脚本
- [x] `api_data_sop.md` 规范文档

### 用户本地操作内容（需手动完成）

- [ ] 申请高德Web服务API Key
- [ ] 安装依赖库（requests, pandas, geopandas等）
- [ ] 运行脚本采集POI数据
- [ ] 验证输出文件完整性

### 验收标准

1. CSV文件字段完整匹配data&api-design.md规范
2. SHP文件坐标系为EPSG:4326，可被QGIS/ArcGIS正常读取
3. 数据量 > 0，无明显坐标异常
4. 可直接输入第一阶段GIS流水线（main_gis_pipeline.py）无报错
