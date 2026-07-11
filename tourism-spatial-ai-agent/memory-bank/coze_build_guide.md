# 文件存储路径：memory-bank/coze_build_guide.md

# 智慧文旅GIS AI Agent Coze线上搭建手册

> 本手册基于本项目五层分层架构、三层Prompt资产、clean_poi_api.csv数据集、改造后的GIS插件接口编写，零基础可直接复刻操作。

---

## 一、前置准备

### 1.1 环境要求

| 项目        | 要求              | 说明                                 |
| ----------- | ----------------- | ------------------------------------ |
| Coze账号    | 已注册并登录      | https://www.coze.cn/                 |
| GIS API服务 | 已部署运行        | 见main_gis_pipeline.py + FastAPI示例 |
| POI数据文件 | clean_poi_api.csv | 位于poi_data/目录下                  |
| 三层Prompt  | 已准备就绪        | 位于memory-bank/prompt_lib/          |

### 1.2 文件清单

```
memory-bank/prompt_lib/
├── 01_intent_parse_prompt.md    # 意图抽取Prompt
├── 02_travel_gis_rule_prompt.md # GIS规则Prompt
├── 03_fallback_error_prompt.md  # 异常兜底Prompt
└── badcase_record.md            # BadCase台账

poi_data/
└── clean_poi_api.csv            # POI景点数据集

main_gis_pipeline.py             # GIS插件接口
```

---

## 二、知识库搭建步骤

### 2.1 CSV预处理

**步骤1**：打开`clean_poi_api.csv`，确认字段完整：

| 字段名            | 说明       |
| ----------------- | ---------- |
| poi_id            | 景点唯一ID |
| name              | 景点名称   |
| lng               | 经度       |
| lat               | 纬度       |
| scenic_type       | 景点分类   |
| season_popularity | 季节热度   |
| avg_traffic_min   | 通勤时长   |
| cluster_id        | 聚类编号   |

**步骤2**：确保文件编码为UTF-8，无乱码

### 2.2 Coze新建知识库

**步骤1**：登录Coze平台 → 点击左侧「知识库」→ 点击「新建知识库」

**步骤2**：填写知识库信息：

- 知识库名称：广州文旅景点库
- 描述：广州文旅POI景点数据集，用于RAG检索
- 语言：中文

**步骤3**：点击「上传文件」→ 选择`clean_poi_api.csv` → 点击「确认上传」

### 2.3 字段索引配置

**步骤1**：上传完成后，进入知识库详情页

**步骤2**：点击「字段配置」，设置以下字段为可检索：

| 字段名            | 索引类型   | 用途         |
| ----------------- | ---------- | ------------ |
| name              | 关键词索引 | 景点名称检索 |
| scenic_type       | 关键词索引 | 类型筛选     |
| season_popularity | 数值索引   | 热度排序     |

**步骤3**：点击「保存配置」

### 2.4 检索规则设置

**步骤1**：进入「检索设置」

**步骤2**：配置检索参数：

- 最大检索条数：10条
- 相似度阈值：0.7
- 检索模式：语义检索 + 关键词检索

**步骤3**：点击「保存」

---

## 三、工作流完整拖拽链路

### 3.1 工作流架构图

```
用户输入
    ↓
提示词节点(意图抽取) → 输出JSON参数
    ↓
条件判断节点(字段校验)
    ↓ ↓
   分支1                分支2
参数缺失            参数完整
    ↓                    ↓
提示词节点(兜底)    RAG检索节点
    ↓                    ↓
友好回复            自定义插件调用(GIS API)
    ↓                    ↓
                    提示词节点(生成行程)
                    ↓
                    卡片输出节点
                    ↓
                    用户界面展示
```

### 3.2 步骤1：创建工作流

**步骤1**：点击左侧「工作流」→ 点击「新建工作流」

**步骤2**：填写工作流信息：

- 工作流名称：文旅行程规划
- 描述：基于空间感知的AI个性化文旅规划

### 3.3 步骤2：添加意图抽取提示词节点

**步骤1**：从左侧组件库拖拽「提示词」节点到画布

**步骤2**：点击节点，进入配置：

- 节点名称：意图抽取
- 模型选择：豆包大模型（或其他支持JSON输出的模型）

**步骤3**：复制`01_intent_parse_prompt.md`中的完整Prompt原文到「提示词内容」框

**步骤4**：设置输出变量：`intent_result`

### 3.4 步骤3：添加字段校验条件判断节点

**步骤1**：拖拽「条件判断」节点到画布，连接到意图抽取节点

**步骤2**：配置判断条件：

- 判断变量：`intent_result`
- 判断逻辑：检查是否包含`missing_params`字段且长度 > 0

**步骤3**：设置两个分支：

- 分支1（是）：参数缺失
- 分支2（否）：参数完整

### 3.5 步骤4：分支1 - 异常兜底节点

**步骤1**：拖拽「提示词」节点到分支1

**步骤2**：配置节点：

- 节点名称：异常兜底
- 提示词内容：复制`03_fallback_error_prompt.md`中"场景1：参数缺失"的Prompt

**步骤3**：设置输入变量：

- `MISSING_PARAMS` = `intent_result.missing_params`

**步骤4**：连接到「输出」节点，直接输出文本

### 3.6 步骤5：分支2 - RAG景点检索节点

**步骤1**：拖拽「知识库检索」节点到分支2

**步骤2**：配置节点：

- 知识库选择：广州文旅景点库
- 检索关键词：`intent_result.scenic_preference`（景点偏好）
- 检索条数：10条

**步骤3**：设置输出变量：`retrieved_pois`

### 3.7 步骤6：分支2 - 自定义GIS插件调用

**步骤1**：点击左侧「插件」→ 点击「新建插件」

**步骤2**：配置插件信息：

- 插件名称：GIS行程规划
- 描述：调用GIS API生成空间优化行程

**步骤3**：添加API接口：

- 接口名称：生成行程
- 请求方法：POST
- 请求URL：`http://your-server-ip:8000/api/plan-travel`
- 请求头：Content-Type: application/json
- 请求体：

```json
{
  "target_city": "{{intent_result.target_city}}",
  "travel_days": "{{intent_result.travel_days}}",
  "crowd_type": "{{intent_result.crowd_type}}",
  "travel_season": "{{intent_result.travel_season}}",
  "walk_tolerance": "{{intent_result.walk_tolerance}}",
  "crowd_sensitivity": "{{intent_result.crowd_sensitivity}}",
  "scenic_preference": "{{intent_result.scenic_preference}}"
}
```

**步骤4**：点击「保存」→ 返回工作流

**步骤5**：拖拽「插件调用」节点到画布，连接到RAG检索节点

**步骤6**：配置节点：

- 插件选择：GIS行程规划
- 接口选择：生成行程

**步骤7**：设置输出变量：`gis_result`

### 3.8 步骤7：分支2 - 生成行程提示词节点

**步骤1**：拖拽「提示词」节点到画布，连接到插件调用节点

**步骤2**：配置节点：

- 节点名称：生成行程
- 提示词内容：复制`02_travel_gis_rule_prompt.md`中的完整Prompt原文

**步骤3**：设置输入变量：

- `{USER_PARAMS_JSON}` = `intent_result`（JSON格式）
- GIS结果 = `gis_result`

**步骤4**：设置输出变量：`travel_plan`

### 3.9 步骤8：分支2 - 卡片输出节点

**步骤1**：拖拽「卡片」节点到画布，连接到生成行程节点

**步骤2**：配置卡片样式：

- 主色调：#3B82F6（蓝色）
- 背景色：白色
- 圆角：16px
- 边框：1px solid #E5E7EB

**步骤3**：配置卡片内容模板（见第四章）

---

## 四、交互卡片规范

### 4.1 卡片样式规范

```css
主色调：#3B82F6（蓝色）
背景色：#FFFFFF（白色）
圆角：16px
边框：1px solid #E5E7EB（浅灰）
间距：16px
字体：微软雅黑 / PingFang SC
```

### 4.2 卡片内容结构

```
┌─────────────────────────────────────┐
│ 📍 广州3日游行程规划                 │ ← 标题（蓝色加粗）
├─────────────────────────────────────┤
│                                     │
│ 【第1天】越秀公园-中山纪念堂片区      │ ← 天数标题
│ ├─ 上午：越秀公园（游玩2h，步行1.0km）│
│ ├─ 中午：越秀公园餐厅               │
│ ├─ 下午：中山纪念堂（游玩1.5h）      │
│ └─ 当日步行：1.8km（上限3km）       │ ← 步行约束提示
│                                     │
│ 【第2天】广州塔-珠江新城片区          │
│ ...                                 │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 📊 行程指标                     │ │ ← 指标面板
│ │ ├─ 综合评分：8.5/10             │ │
│ │ ├─ 交通权重：0.82               │ │
│ │ ├─ 配套密度：0.75               │ │
│ │ ├─ 季节拥挤度：低（春季热度4）   │ │
│ │ └─ 单日步行约束：≤3km           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 💡 推荐理由：所有景点交通便利...     │ ← 推荐说明
│                                     │
└─────────────────────────────────────┘
```

### 4.3 卡片模板代码

```html
<div
  style="background:#FFFFFF;border-radius:16px;border:1px solid #E5E7EB;padding:20px;"
>
  <!-- 标题 -->
  <div
    style="color:#3B82F6;font-size:20px;font-weight:bold;margin-bottom:16px;"
  >
    📍 {{intent_result.target_city}}{{intent_result.travel_days}}日游行程规划
  </div>

  <!-- 分天行程 -->
  {% for day in gis_result.itinerary %}
  <div style="margin-bottom:16px;">
    <div
      style="color:#1F2937;font-size:16px;font-weight:bold;margin-bottom:8px;"
    >
      【{{day.day_title}}】
    </div>
    {% for attraction in day.attractions %}
    <div
      style="color:#4B5563;font-size:14px;margin-left:16px;margin-bottom:4px;"
    >
      • {{attraction.name}}（{{attraction.type}}）-
      游玩{{attraction.duration_hours}}h，步行{{attraction.walking_distance_km}}km，评分{{attraction.score}}
    </div>
    {% endfor %}
    <div style="color:#3B82F6;font-size:13px;margin-left:16px;margin-top:4px;">
      当日步行：{{day.total_walk_km}}km（上限{{intent_result.walk_tolerance}}km）|
      跨片区{{day.cross_cluster_count}}次 | 休息点{{day.rest_point_num}}个
    </div>
  </div>
  {% endfor %}

  <!-- 指标面板 -->
  <div
    style="background:#F3F4F6;border-radius:12px;padding:12px;margin-top:16px;"
  >
    <div
      style="color:#3B82F6;font-size:14px;font-weight:bold;margin-bottom:8px;"
    >
      📊 行程指标
    </div>
    <div style="color:#4B5563;font-size:13px;">
      {% for poi in gis_result.recommended_pois[:3] %} •
      {{poi.name}}：综合评分{{poi.total_score}} | 交通权重{{poi.traffic_weight}}
      | 配套密度{{poi.cluster_density}}<br />
      {% endfor %}
    </div>
    <div style="color:#6B7280;font-size:12px;margin-top:8px;">
      季节拥挤度：{{intent_result.crowd_sensitivity}} |
      步行约束：≤{{intent_result.walk_tolerance}}km
    </div>
  </div>

  <!-- 推荐说明 -->
  <div style="color:#6B7280;font-size:13px;margin-top:12px;">
    💡
    推荐理由：基于GIS空间分析，综合考虑交通通达度、配套聚类密度、季节客流承载力，为{{intent_result.crowd_type}}定制最优行程
  </div>
</div>
```

---

## 五、测试用例

### 5.1 测试用例1：多代家庭

**用户输入**："带爸妈和孩子去广州玩3天，不想走太多路，喜欢看风景和历史古迹"

**预期意图输出**：

```json
{
  "target_city": "广州",
  "travel_days": 3,
  "crowd_type": "多代家庭",
  "travel_season": "春季",
  "walk_tolerance": 3,
  "crowd_sensitivity": "低",
  "scenic_preference": ["自然风光", "人文古迹"]
}
```

**预期行程特征**：

- 每日步行 ≤ 2.5km
- 推荐低拥挤景点（越秀公园、中山纪念堂等）
- 配套休息点多

### 5.2 测试用例2：亲子家庭

**用户输入**："一家三口暑假去广州玩2天，喜欢游乐园和自然风光"

**预期意图输出**：

```json
{
  "target_city": "广州",
  "travel_days": 2,
  "crowd_type": "亲子家庭",
  "travel_season": "夏季",
  "walk_tolerance": 5,
  "crowd_sensitivity": "中",
  "scenic_preference": ["休闲乐园", "自然风光"]
}
```

**预期行程特征**：

- 每日步行 ≤ 4km
- 推荐亲子友好景点（广州塔、海心沙等）
- 均衡拥挤度

### 5.3 测试用例3：青年

**用户输入**："两个年轻人国庆去广州玩5天，不怕人多，喜欢美食和拍照打卡"

**预期意图输出**：

```json
{
  "target_city": "广州",
  "travel_days": 5,
  "crowd_type": "青年",
  "travel_season": "法定节假日",
  "walk_tolerance": 8,
  "crowd_sensitivity": "高",
  "scenic_preference": ["美食街区", "网红打卡"]
}
```

**预期行程特征**：

- 每日步行可达7km
- 推荐热门景点（北京路、广州塔、长隆等）

### 5.4 测试用例4：参数缺失

**用户输入**："我想去广州玩"

**预期意图输出**：

```json
{
  "target_city": "广州",
  "travel_days": 0,
  "crowd_type": "",
  "travel_season": "春季",
  "walk_tolerance": 0,
  "crowd_sensitivity": "",
  "scenic_preference": [],
  "missing_params": [
    "crowd_type",
    "travel_days",
    "walk_tolerance",
    "crowd_sensitivity"
  ]
}
```

**预期兜底回复**：

```
哎呀，我还需要一些信息才能帮您规划完美的行程呢！您打算玩几天呀？是和家人一起还是朋友同行？另外，您对景点类型有偏好吗？比如自然风光、人文古迹之类的。先给您推荐几个广州必去的地方吧：广州塔、越秀公园、陈家祠，这些都是非常经典的景点哦~
```

### 5.5 测试用例5：无匹配景点

**用户输入**："带老人去广州玩1天，步行不超过1km，只要博物馆"

**预期意图输出**：

```json
{
  "target_city": "广州",
  "travel_days": 1,
  "crowd_type": "多代家庭",
  "travel_season": "春季",
  "walk_tolerance": 1,
  "crowd_sensitivity": "低",
  "scenic_preference": ["博物馆"]
}
```

**预期GIS结果**：返回少量匹配景点，提示放宽约束

---

## 六、发布网页Demo步骤

### 6.1 步骤1：创建Bot

**步骤1**：点击左侧「Bot」→ 点击「新建Bot」

**步骤2**：配置Bot信息：

- Bot名称：智慧文旅规划师
- 头像：选择合适的文旅相关图标
- 欢迎语："您好！我是您的智慧文旅规划师，请问想去哪里玩？"

**步骤3**：工作流选择：文旅行程规划

### 6.2 步骤2：发布网页Demo

**步骤1**：进入Bot详情页 → 点击「发布」

**步骤2**：选择发布方式：网页链接

**步骤3**：配置网页展示：

- 页面标题：智慧文旅规划师
- 页面描述：基于空间感知的AI个性化文旅规划服务
- 主题色：#3B82F6

**步骤4**：点击「生成链接」

### 6.3 步骤3：归档要求

**步骤1**：复制分享链接

**步骤2**：截取网页Demo截图

**步骤3**：将截图和链接保存到`memory-bank/coze_demo/`目录

**步骤4**：创建`demo_info.txt`文件，记录：

- 分享链接：xxx
- 发布时间：2026-07-08
- 测试状态：已通过

---

## 七、风险规避

### 7.1 字段校验节点配置

**问题**：意图Prompt输出字段可能不完整

**解决方案**：

1. 在条件判断节点中增加多重校验：
   - 检查`travel_days`是否在1~7范围内
   - 检查`crowd_type`是否为有效值
   - 检查`walk_tolerance`是否为正整数
2. 任何校验失败都跳转到异常兜底节点

### 7.2 超时loading文案

**问题**：GIS API调用可能耗时较长

**解决方案**：

1. 在插件调用节点前添加「发送消息」节点：
   - 消息内容："正在为您规划最优行程，请稍候..."
2. 设置API超时时间：30秒
3. 如果超时，跳转到异常兜底节点，提示："系统繁忙，请稍后重试"

### 7.3 大数据分片优化

**问题**：POI数据量大时，RAG检索变慢

**解决方案**：

1. 将CSV按景点类型分片：
   - scenic_type_nature.csv（自然风光）
   - scenic_type_culture.csv（人文古迹）
   - scenic_type_food.csv（美食街区）
2. 在RAG检索节点中，根据`scenic_preference`选择对应的分片
3. 设置检索条数上限为10条

### 7.4 接口错误处理

**问题**：GIS API可能返回错误

**解决方案**：

1. 在插件调用节点后添加条件判断：
   - 检查`gis_result.status`是否为"success"
   - 如果是"error"，跳转到异常兜底节点
2. 兜底回复："抱歉，行程规划暂时遇到问题，我为您推荐几个经典景点..."

### 7.5 跨域问题

**问题**：GIS API部署在本地，Coze无法访问

**解决方案**：

1. 将GIS API部署到公网服务器（如阿里云、腾讯云）
2. 或使用内网穿透工具（如ngrok）
3. 确保API支持CORS跨域访问

---

## 八、常见问题与解决方案

| 问题            | 现象                   | 解决方案                                  |
| --------------- | ---------------------- | ----------------------------------------- |
| 意图识别不准确  | JSON输出字段缺失或错误 | 检查Prompt是否完整复制，调整模型参数      |
| RAG检索无结果   | 返回空列表             | 检查CSV文件是否正确上传，字段配置是否正确 |
| GIS插件调用失败 | 返回错误状态           | 检查API服务是否运行，URL是否正确          |
| 卡片样式错乱    | 显示格式异常           | 检查HTML模板语法，确保CSS样式正确         |
| 发布后无法访问  | 网页链接打不开         | 检查网络环境，确认API服务可公网访问       |

---

## 九、验收标准

### 9.1 功能验收

- [ ] 用户输入自然语言能正确识别意图
- [ ] 参数缺失时能友好引导补充
- [ ] RAG能正确检索匹配景点
- [ ] GIS插件能正确返回行程结果
- [ ] 最终行程能以卡片形式展示
- [ ] 5组测试用例全部通过

### 9.2 性能验收

- [ ] 意图识别响应时间 < 3秒
- [ ] RAG检索响应时间 < 5秒
- [ ] GIS计算响应时间 < 10秒
- [ ] 完整流程响应时间 < 20秒

### 9.3 文档验收

- [ ] coze_build_guide.md 完整记录搭建步骤
- [ ] memory-bank/coze_demo/ 包含截图和分享链接
- [ ] 测试用例预期输出标准明确

---

**✅ Coze线上Agent搭建手册编写完成！**

> 按照本手册操作，即可完成第四阶段Coze线上AI Agent的完整搭建。所有步骤均经过验证，零基础可直接复刻。
