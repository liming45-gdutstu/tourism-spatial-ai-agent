implementation-plan.md
项目分步开发执行计划
总述
本文档严格遵循 CLAUDE.md 全局开发约束、B 站 Vibe Coding 全套实操技巧，将「基于空间感知的 AI 个性化文旅规划 Agent」项目拆分为两大阶段，明确每一步操作、产出物、校验标准、Plan 模式启用规则，所有开发流程按本文顺序执行，禁止跳步。
第一阶段：前置规范文档搭建（已完成本阶段全部步骤）
阶段目标
搭建 memory-bank 项目底层规范仓库，锁定技术、架构、数据三层开发标准，解决 AI 上下文失忆问题，为代码开发提供强制参考依据。
分步执行清单
表格
步骤 操作内容 产出文件 是否启用 Plan 模式 完成校验标准
1 按 5 段式需求模板生成 tech-stack.md 技术栈文档 D:/work/tourism-spatial-ai-agent/tech-stack.md 是（大型文档规划） VS 项目根目录存在完整文档，分层罗列五层架构配套工具
2 按 5 段式需求模板生成 architecture.md 五层架构文档 architecture.md 是（大型架构规划） 明确五层数据流、模块职责、四大 GIS 核心模块不可删减
3 按 5 段式需求模板生成 data&api-design.md 数据接口文档 data&api-design.md 是（数据结构规划） 全量输入输出字段表格定义，严格匹配架构分层
4 新建 memory-bank 归档文件夹，移入三份设计文档 memory-bank/tech-stack.md、architecture.md、data&api-design.md 否（纯文件移动操作） 三份文档统一收纳，项目根目录无散落设计文档
5 memory-bank 内新建两个空白日志文件 memory-bank/progress.md、memory-bank/implementation-plan.md 否（新建空白文件） 文件夹内两个空白文件存在，用于后续记录迭代、开发计划
6 项目根目录新建全局约束 CLAUDE.md CLAUDE.md 是（全局规则规划） 根目录顶层存放，包含完整 Vibe Coding 开发流程锁死规则
本阶段完成状态
所有前置规范文档全部编写、归档、保存完毕，项目底层标准固定，可进入代码开发阶段。
第二阶段：代码开发迭代阶段（后续实操执行）
通用开发规则（融合 B 站 Vibe Coding 技巧）
所有模块遵循「先空白可运行框架 → 本地验证无报错 → 填充 GIS 业务算法」顺序；
大型完整模块开发开启 Plan 模式做前期规划，调试 bug、微调页面样式直接下发指令；
每完成单个模块，更新 memory-bank/progress.md 记录里程碑、参数改动；
代码报错必须附带截图 + 文字说明故障模块、预期效果，提交修复。
分步开发清单（按执行顺序）
子阶段 1：RAG 景点数据源预处理模块
操作：生成 Python 空白文件框架，导入 pandas、geopandas 依赖
产出：poi_data_process.py
Plan 模式：是（数据源完整规划）
测试标准：成功读取高德 POI 数据，输出格式完全匹配 data&api-design.md 表格字段
子阶段 2：四大 GIS 空间算法核心模块（项目差异化核心）
固定开发顺序，不可调换：
Kmeans 片区聚类模块
产出：gis_cluster.py，先建空白框架，验证经纬度读取正常后填充聚类算法
交通通达度权重计算模块
产出：gis_traffic_weight.py，输入输出严格绑定 POI 数据表结构
客流承载力过滤模块
产出：gis_crowd_filter.py，匹配季节拥挤参数自动删减景点
人群步行约束适配模块
产出：gis_walk_limit.py，按人群类型自动控制单日步行上限
Plan 模式：全部开启（核心业务模块规划）
统一测试标准：四层模块串联执行，输出行程指标无字段缺失、无数值超限错误
子阶段 3：离线可视化 HTML 页面开发
操作：新建空白 HTML 文件，用 Live Server 预览基础页面框架
产出：travel_view.html、配套 css/js 样式文件
Plan 模式：否（页面样式微调无需规划，仅底层数据渲染需匹配 data 文档）
测试标准：本地打开可渲染片区地图、行程指标面板，淡蓝绿水彩设计规范
子阶段 4：Coze 智能体插件对接开发
操作：基于 GIS 输出数据编写插件调用入参模板
产出：Coze 工作流配置文档、插件入参 JSON 模板
Plan 模式：是（跨系统交互规划）
测试标准：输入用户需求参数，插件可完整调用 GIS 算法并返回友好行程文案
子阶段 5：全链路联调与上下文归档
操作：完整跑通「用户输入→Coze→大模型→RAG→GIS→可视化」全数据流
产出：更新 progress.md 完整开发里程碑日志，同步修正架构文档迭代内容
Plan 模式：是（全项目收尾规划）
测试标准：无数据字段不匹配、无 GIS 逻辑遗漏、页面渲染正常
子阶段 6：Git 仓库归档（最终交付）
操作：将项目完整目录推送至 GitHub，完善 README.md
产出：完整开源项目仓库，memory-bank 全套文档作为项目说明资料
Plan 模式：否（纯 Git 操作）
测试标准：仓库包含全部文档、代码、开发日志，可完整复现开发流程
三、开发迭代与日志规范
每完成一个子阶段，在memory-bank/progress.md记录：完成时间、新增文件、架构 / 参数改动点；
若新增 GIS 计算规则、人群类型、景点标签，同步更新 architecture.md、data&api-design.md、CLAUDE.md 三份文档；
连续完成 3 个及以上代码模块后，执行上下文压缩指令，清空冗余对话历史，仅保留 memory-bank 文档作为永久参考。
