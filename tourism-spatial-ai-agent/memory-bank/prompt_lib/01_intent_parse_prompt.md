# 文件存储路径：memory-bank/prompt_lib/01_intent_parse_prompt.md

## 一、作用

本Prompt用于解析用户自然语言输入，从中固定抽取7项出行参数，输出标准JSON格式，供下游GIS空间分析模块和Coze线上Agent使用。核心目标是将非结构化的用户需求转换为结构化的计算机可识别参数，字段严格对齐data&api-design.md规范。

## 二、抽取字段

| 字段名            | 数据类型     | 取值范围                                           | 说明                 |
| ----------------- | ------------ | -------------------------------------------------- | -------------------- |
| target_city       | string       | 国内地级市/旅游城市名称，如广州、杭州              | 目标游玩城市         |
| travel_days       | int          | 1~7                                                | 游玩总天数           |
| crowd_type        | string       | 青年 / 亲子家庭 / 多代家庭                         | 出行人群类型         |
| travel_season     | string       | 春季 / 夏季 / 秋季 / 冬季 / 法定节假日             | 出行季节             |
| walk_tolerance    | int          | 数字（单位km）                                     | 单日最大步行耐受距离 |
| crowd_sensitivity | string       | 低 / 中 / 高                                       | 客流拥挤耐受度       |
| scenic_preference | list[string] | 自然风光 / 人文古迹 / 美食街区 / 网红打卡 / 博物馆 | 景点偏好标签列表     |

## 三、人群步行阈值绑定规则

系统内置人群类型与步行阈值的映射关系：

- **多代家庭**：单日最大步行上限 3km（适配老年人和儿童体力）
- **亲子家庭**：单日最大步行上限 5km（适配带孩子出行）
- **青年**：单日最大步行上限 8km（适配年轻人体力）

当用户未明确指定步行距离时，根据人群类型自动绑定上述默认值。

## 四、季节默认规则

当用户未明确指定出行季节时：

- 默认返回当前季节（春季3-5月、夏季6-8月、秋季9-11月、冬季12-2月）
- 如果无法判断当前季节，默认返回"春季"

## 五、完整Prompt原文

```
你是一个专业的文旅出行需求解析助手。请分析用户的自然语言输入，从中提取以下7项标准参数，输出纯JSON格式，不要包含任何多余文字或解释。

必须提取的参数：
1. target_city（目标游玩城市）：国内地级市或旅游城市名称，如广州、杭州
2. travel_days（游玩天数）：数字，范围1~7
3. crowd_type（出行人群类型）：取值范围为"青年"、"亲子家庭"、"多代家庭"之一
4. travel_season（出行季节）：取值范围为"春季"、"夏季"、"秋季"、"冬季"、"法定节假日"之一
5. walk_tolerance（单日最大步行距离，单位km）：数字
6. crowd_sensitivity（客流拥挤耐受度）：取值范围为"低"、"中"、"高"之一
7. scenic_preference（景点偏好）：字符串数组，可选值为"自然风光"、"人文古迹"、"美食街区"、"网红打卡"、"博物馆"

人群步行阈值默认规则（用户未指定时自动应用）：
- 多代家庭：walk_tolerance = 3
- 亲子家庭：walk_tolerance = 5
- 青年：walk_tolerance = 8

拥挤耐受度默认规则（用户未指定时自动应用）：
- 多代家庭：默认"低"（避开拥挤）
- 亲子家庭：默认"中"（均衡）
- 青年：默认"高"（无所谓拥挤）

季节默认规则（用户未指定时）：
- 默认返回"春季"

景点偏好默认规则（用户未指定时）：
- 默认返回空数组[]

输出格式要求：
- 必须是纯JSON格式，包含且仅包含上述7个字段
- 不要添加任何注释或额外说明
- 字段名必须严格匹配，大小写敏感

【输出约束】
- 如果用户输入缺少关键信息（如游玩天数、人群类型），**必须在JSON中明确标记缺失字段**，格式示例：
  {"target_city":"","travel_days":0,"crowd_type":"","travel_season":"","walk_tolerance":0,"crowd_sensitivity":"","scenic_preference":[],"missing_params":["crowd_type","travel_days"]}
- 禁止在参数不完整时强行填充默认值生成行程

示例输出格式：
{"target_city":"广州","travel_days":3,"crowd_type":"多代家庭","travel_season":"春季","walk_tolerance":3,"crowd_sensitivity":"低","scenic_preference":["自然风光","人文古迹"]}

开始解析：
```

## 六、测试案例

### 测试用例1

**用户提问**："我想带爸妈和孩子去广州玩3天，不想走太多路，喜欢看风景和历史古迹"

**标准JSON输出**：

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

### 测试用例2

**用户提问**："两个年轻人想去广州旅游5天，不怕人多，喜欢美食和拍照打卡"

**标准JSON输出**：

```json
{
  "target_city": "广州",
  "travel_days": 5,
  "crowd_type": "青年",
  "travel_season": "春季",
  "walk_tolerance": 8,
  "crowd_sensitivity": "高",
  "scenic_preference": ["美食街区", "网红打卡"]
}
```

### 测试用例3

**用户提问**："一家三口暑假去杭州玩2天，偏好自然风光"

**标准JSON输出**：

```json
{
  "target_city": "杭州",
  "travel_days": 2,
  "crowd_type": "亲子家庭",
  "travel_season": "夏季",
  "walk_tolerance": 5,
  "crowd_sensitivity": "中",
  "scenic_preference": ["自然风光"]
}
```

### 测试用例4

**用户提问**："国庆带老人去西安玩4天，偏好博物馆和人文景点，步行不能超过4公里"

**标准JSON输出**：

```json
{
  "target_city": "西安",
  "travel_days": 4,
  "crowd_type": "多代家庭",
  "travel_season": "法定节假日",
  "walk_tolerance": 4,
  "crowd_sensitivity": "低",
  "scenic_preference": ["博物馆", "人文古迹"]
}
```

### 测试用例5（新增）

**用户提问**："春节带全家去成都玩6天，喜欢美食和自然风光"

**标准JSON输出**：

```json
{
  "target_city": "成都",
  "travel_days": 6,
  "crowd_type": "多代家庭",
  "travel_season": "法定节假日",
  "walk_tolerance": 3,
  "crowd_sensitivity": "低",
  "scenic_preference": ["美食街区", "自然风光"]
}
```

### 测试用例6（新增）

**用户提问**："秋季和朋友去桂林玩3天，喜欢山水风景，不怕走路"

**标准JSON输出**：

```json
{
  "target_city": "桂林",
  "travel_days": 3,
  "crowd_type": "青年",
  "travel_season": "秋季",
  "walk_tolerance": 8,
  "crowd_sensitivity": "高",
  "scenic_preference": ["自然风光"]
}
```
