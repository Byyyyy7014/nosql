# NoSQL数据库上机测验

## 一、基本信息

- 学号：12403030223
- 班级：大数据管理与应用2班
- Python版本：Python 3.12
- MongoDB版本：8.3.11
- PyMongo版本：4.19.0
- Redis版本：8.10.2
- redis-py版本：8.1.0

## 二、项目结构

```text
12403030223/
├── README.md
├── task1/
│   ├── task1_init.py
│   ├── task1_query.py
│   ├── task1_update.py
│   ├── task1_add_chapter.py
│   └── task1_verify.py
├── task2/
│   ├── task2_init.py
│   ├── task2_atomic.py
│   ├── task2_order.py
│   └── task2_scenarios.py
├── task3/
│   ├── task3_redis.py
│   ├── task3_set.py
│   ├── task3_zset.py
│   ├── task3_string.py
│   └── task3_verify.py
└── task4/
    └── task4_pipeline.py
```

## 三、实验内容

### 第一题：MongoDB课程信息查询与维护

完成课程数据初始化、条件查询、课程章节信息更新、章节新增及最终数据核验。

### 第二题：MongoDB原子扣减与事务验证

完成库存原子扣减、订单创建、事务回滚及四种测试场景验证，检查库存与订单数据的一致性。

### 第三题：Redis学习信息与排行榜

使用Redis的Hash、Set、Sorted Set和String四种数据结构，完成学生学习信息存储、章节去重、成绩排行榜及会话过期管理。

### 第四题：Redis Pipeline批量操作

分别采用逐条写入和Pipeline批量写入方式完成数据写入，对比两种方式的执行耗时，并验证数据完整性。

## 四、个人实验参数

- S = 23
- A = 2
- B = 3
- C = 3

## 五、运行环境说明

MongoDB使用个人数据库 exam_12403030223。

MongoDB事务实验依赖单节点副本集 rs0。

Redis实验使用Redis Cluster，节点端口为30223至30228，连接入口使用30223、30224、30225。

运行前应确保MongoDB服务和Redis Cluster节点正常运行，并安装所需Python依赖。

## 六、运行注意事项

1. 第一题应先运行 task1_init.py，再执行查询、更新、章节新增和核验脚本。
2. 第二题应先运行 task2_init.py，再执行原子扣减、订单及场景测试脚本。
3. task1_init.py会重新初始化第一题数据。
4. task2_init.py和task2_scenarios.py会重置第二题相关数据，复核时不要随意执行。
5. 第三题各脚本分别操作不同Redis数据结构，最终可使用 task3_verify.py进行核验。
6. 第四题运行 task4_pipeline.py进行性能对比和数据完整性验证。

## 七、实验结果

所有实验脚本均已在本地环境中实际运行，并完成相应结果核验。

第四题的性能数据为本机实测结果，实际耗时可能随运行环境和系统负载变化。
