# 多代家庭文旅GIS AI行程Agent

> 基于空间感知的AI个性化文旅规划智能体，为多代家庭提供智能化、空间合理化的旅游行程规划服务

## 📍 项目简介

本项目针对OTA行业「千人一面」的行程推荐痛点，创新引入GIS空间分析能力，构建面向多代家庭（青年、亲子、多代同堂）的分层个性化行程规划系统。通过Kmeans片区聚类、交通通达度权重、季节客流承载力、分人群步行阈值四大差异化能力，实现从「景点堆砌」到「空间最优」的行程规划升级。

**核心价值**：为不同人群（青年8km/亲子5km/多代家庭3km）提供差异化行程方案，解决传统行程推荐忽略体力差异、景点跨区通勤长、旺季拥挤体验差等行业痛点。

---

## 🔗 在线演示

- **墨刀交互原型**：[点击查看](https://modao.cc/proto/sOpuSkMUti03ha7Yy8sJJt/sharing?view_mode=read_only)
- **Coze线上智能体**：待发布

---

## ✨ 四大核心产品亮点

### 亮点1：GIS片区Kmeans聚类

- 基于景点经纬度自动划分游玩片区，减少跨区通勤
- 同片区景点优先串联，降低单日步行折返
- 聚类结果可视化展示，直观呈现片区分布

### 亮点2：多代人群分层参数表单

- **青年**：单日步行上限8km，高拥挤耐受度，推荐热门景点
- **亲子家庭**：单日步行上限5km，中拥挤耐受度，亲子友好景点优先
- **多代家庭**：单日步行上限3km，低拥挤耐受度，避开高客流景点

### 亮点3：采集-生成-确认-导出闭环流程

1. **需求采集**：自然语言解析用户出行意图
2. **行程生成**：GIS空间算法计算最优路线
3. **方案确认**：可视化卡片展示行程指标
4. **数据导出**：支持CSV/SHP格式数据输出

### 亮点4：景点+5分钟本地美食配套

- 推荐景点周边5分钟步行范围内的特色美食
- 配套餐饮信息提升行程实用性
- 减少游客额外搜索成本

---

## 🏃 完整业务链路

### 前端用户操作流程

```
用户输入自然语言需求
    ↓
意图识别解析（7项参数抽取）
    ↓
参数完整性校验
    ↓ ↓
参数缺失        参数完整
    ↓              ↓
友好引导补充    RAG景点检索
                   ↓
              GIS空间计算
                   ↓
              行程生成展示
                   ↓
              卡片输出确认
```

### 后端GIS算法计算流程

```
POI数据输入（187条广州文旅景点）
    ↓
Kmeans片区聚类 → 生成cluster_id
    ↓
交通通达度权重计算 → 通勤最优排序
    ↓
季节客流承载力筛选 → 过滤高拥挤景点
    ↓
分人群步行体力约束 → 确保不超标
    ↓
AI综合打分推荐 → TOP景点排序
    ↓
行程结果输出（标准化JSON）
```

---

## 🎨 原型页面功能拆解

### 页面1：首页 - 需求输入

- 欢迎语与品牌展示
- 自然语言输入框
- 快速选择标签（城市、天数、人群类型）
- 热门推荐快捷入口

### 页面2：意图解析 - 参数确认

- 用户需求结构化展示
- 7项参数可视化呈现
- 参数修改入口
- 一键生成行程按钮

### 页面3：行程推荐 - 卡片展示

- 淡蓝商务风格卡片
- 分天行程详细展示
- 核心指标面板（综合评分、交通权重、配套密度、季节拥挤度）
- 步行约束提示

### 页面4：行程详情 - 可视化地图

- 景点片区聚类分布图
- 游玩路线轨迹展示
- 步行距离热力图
- 导出功能按钮

### 弹窗功能

- 参数缺失引导弹窗
- 加载状态弹窗
- 异常报错兜底弹窗
- 分享/导出弹窗

---

## 📦 项目完整交付物清单

### 产品设计文档

- [tech-stack.md](memory-bank/tech-stack.md) - 技术栈选型文档
- [architecture.md](memory-bank/architecture.md) - 五层分层架构设计
- [data&api-design.md](memory-bank/data&api-design.md) - 数据与接口规范
- [implementation-plan.md](memory-bank/implementation-plan.md) - 开发执行计划

### Prompt资产库

- [01_intent_parse_prompt.md](memory-bank/prompt_lib/01_intent_parse_prompt.md) - 用户意图抽取模板
- [02_travel_gis_rule_prompt.md](memory-bank/prompt_lib/02_travel_gis_rule_prompt.md) - GIS空间约束行程模板
- [03_fallback_error_prompt.md](memory-bank/prompt_lib/03_fallback_error_prompt.md) - 异常兜底降级模板
- [badcase_record.md](memory-bank/prompt_lib/badcase_record.md) - BadCase迭代优化台账

### GIS核心算法

- [poi_api_crawl.py](poi_api_crawl.py) - 高德合规POI数据采集
- [poi_data_process.py](poi_data_process.py) - POI数据预处理
- [gis_cluster.py](gis_cluster.py) - Kmeans空间聚类
- [gis_traffic_weight.py](gis_traffic_weight.py) - 交通通达度权重
- [gis_carry_capacity.py](gis_carry_capacity.py) - 季节客流承载力
- [gis_walk_limit.py](gis_walk_limit.py) - 分人群步行约束
- [poi_score_agent.py](poi_score_agent.py) - AI综合打分
- [main_gis_pipeline.py](main_gis_pipeline.py) - 全链路GIS流水线

### 数据资产

- [clean_poi_api.csv](poi_data/clean_poi_api.csv) - 清洗完成的187条POI数据
- [poi_tourism_raw.shp](poi_data/poi_tourism_raw.shp) - GIS矢量文件

### 规范文档

- [api_data_sop.md](api_data_sop.md) - POI数据采集SOP
- [coze_build_guide.md](memory-bank/coze_build_guide.md) - Coze搭建手册
- [progress.md](memory-bank/progress.md) - 项目开发里程碑

### Demo归档

- [demo_info.txt](memory-bank/coze_demo/demo_info.txt) - 演示信息与测试用例

---

## 📁 项目目录结构

```
tourism-spatial-ai-agent/
├── gis_cluster.py              # GIS模块：Kmeans空间聚类
├── gis_traffic_weight.py       # GIS模块：交通通达度权重
├── gis_carry_capacity.py       # GIS模块：季节客流承载力
├── gis_walk_limit.py           # GIS模块：分人群步行约束
├── poi_api_crawl.py            # POI数据采集脚本
├── poi_data_process.py         # POI数据预处理
├── poi_score_agent.py          # AI综合打分模块
├── main_gis_pipeline.py        # GIS全链路流水线入口
├── api_data_sop.md             # POI数据采集规范
├── CLAUDE.md                   # 全局AI开发约束
├── .gitignore                  # Git忽略配置
├── poi_data/                   # POI数据存储
│   ├── clean_poi_api.csv       # 清洗完成的POI数据
│   └── poi_tourism_raw.shp     # GIS矢量文件
└── memory-bank/                # 项目文档归档
    ├── tech-stack.md           # 技术栈选型
    ├── architecture.md         # 架构设计
    ├── data&api-design.md      # 数据接口规范
    ├── implementation-plan.md  # 开发计划
    ├── progress.md             # 开发里程碑
    ├── coze_build_guide.md     # Coze搭建手册
    ├── prompt_lib/             # Prompt资产库
    │   ├── 01_intent_parse_prompt.md
    │   ├── 02_travel_gis_rule_prompt.md
    │   ├── 03_fallback_error_prompt.md
    │   └── badcase_record.md
    ├── coze_demo/              # Demo归档
    │   └── demo_info.txt
    ├── docs/                   # PRD文档与HTML源码（待补充）
    └── proto_screenshot/       # 墨刀原型截图（待补充）
```

---

## 🎯 面试现场演示操作步骤

### 步骤1：打开墨刀原型（约2分钟）

1. 访问墨刀分享链接
2. 展示首页设计，讲解产品定位
3. 演示自然语言输入交互

### 步骤2：讲解用户分层设计（约3分钟）

1. 展示三大人群类型（青年/亲子/多代家庭）
2. 讲解差异化参数设计（步行阈值、拥挤耐受度）
3. 说明设计背后的用户洞察

### 步骤3：演示行程生成流程（约5分钟）

1. 输入测试用例："带爸妈和孩子去广州玩3天"
2. 展示意图解析结果（7项参数）
3. 展示GIS计算过程（聚类、权重、筛选）
4. 展示最终行程卡片输出

### 步骤4：验证GIS约束效果（约3分钟）

1. 检查每日步行距离是否≤3km
2. 验证景点是否集中在同一片区
3. 确认季节拥挤度符合低耐受度要求

### 步骤5：展示异常场景处理（约2分钟）

1. 输入不完整需求："我想去广州玩"
2. 展示友好引导弹窗
3. 说明异常兜底策略

### 步骤6：讲解测试用例覆盖（约3分钟）

1. 展示5组测试用例设计
2. 说明覆盖的用户场景
3. 讲解测试验证标准

---

## 🧪 测试用例设计

### 测试用例1：多代家庭（核心场景）

- **用户输入**：带爸妈和孩子去广州玩3天，不想走太多路，喜欢看风景和历史古迹
- **预期结果**：每日步行≤2.5km，推荐低拥挤景点（越秀公园、中山纪念堂），配套休息点多

### 测试用例2：亲子家庭

- **用户输入**：一家三口暑假去广州玩2天，喜欢游乐园和自然风光
- **预期结果**：每日步行≤4km，推荐亲子友好景点（广州塔、海心沙），均衡拥挤度

### 测试用例3：青年

- **用户输入**：两个年轻人国庆去广州玩5天，不怕人多，喜欢美食和拍照打卡
- **预期结果**：每日步行可达7km，推荐热门景点（北京路、长隆）

### 测试用例4：参数缺失（异常场景）

- **用户输入**：我想去广州玩
- **预期结果**：友好引导补充信息（游玩天数、人群类型），推荐热门景点

### 测试用例5：无匹配景点（边界场景）

- **用户输入**：带老人去广州玩1天，步行不超过1km，只要博物馆
- **预期结果**：返回少量匹配景点，提示放宽约束

---

## 📅 项目开发进度

| 阶段                           | 完成时间   | 状态    |
| ------------------------------ | ---------- | ------- |
| 第一阶段：GIS空间分析模块      | 2026-07-08 | ✅ 完成 |
| 第二阶段：高德POI数据采集      | 2026-07-08 | ✅ 完成 |
| 第三阶段：Prompt资产库搭建     | 2026-07-08 | ✅ 完成 |
| 第四阶段：Coze线上Agent改造    | 2026-07-08 | ✅ 完成 |
| 第五阶段：全链路联调与演示优化 | 进行中     | 🔄      |

---

## 📧 联系方式

欢迎交流讨论，如有问题或建议请随时联系！

---

**⭐ 如果这个项目对你有帮助，欢迎Star！**
