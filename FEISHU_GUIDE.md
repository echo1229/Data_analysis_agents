# 飞书机器人接入指南

本指南将帮助你将数据分析 Multi-Agent 系统接入飞书，实现在飞书中直接提问并获取分析报告。

---

## 一、前置准备

### 1.1 注册飞书开放平台账号

访问 [飞书开放平台](https://open.feishu.cn/)，使用飞书账号登录。

### 1.2 创建企业自建应用

1. 进入"开发者后台" → "创建企业自建应用"
2. 填写应用名称：`数据分析助手`
3. 填写应用描述：`基于 AI 的数据分析机器人`
4. 上传应用图标（可选）
5. 点击"创建"

### 1.3 获取应用凭证

创建成功后，进入应用详情页：

1. 点击"凭证与基础信息"
2. 复制 **App ID** 和 **App Secret**
3. 复制 **Verification Token**（用于验证事件签名）

---

## 二、配置应用权限

### 2.1 添加机器人能力

1. 进入"应用功能" → "机器人"
2. 点击"添加机器人"
3. 配置机器人信息：
   - 机器人名称：`数据分析助手`
   - 描述：`我可以帮你分析数据，生成 SQL 和业务报告`
   - 头像：上传图标

### 2.2 配置权限范围

进入"权限管理"，开通以下权限：

**必需权限：**
- `im:message` - 获取与发送单聊、群组消息
- `im:message.group_at_msg` - 获取群组中所有消息（用于 @机器人）
- `im:message.group_at_msg:readonly` - 接收群聊中 @机器人消息事件
- `im:message.p2p_msg` - 获取用户发给机器人的单聊消息
- `im:message.p2p_msg:readonly` - 接收用户发给机器人的单聊消息事件

**可选权限：**
- `im:chat` - 获取群组信息
- `contact:user.base` - 获取用户基本信息

配置完成后，点击"申请权限" → "提交审核"（企业自建应用通常自动通过）。

---

## 三、配置事件订阅

### 3.1 部署服务器

**方式一：本地测试（使用 ngrok）**

1. 安装 ngrok：https://ngrok.com/download
2. 启动飞书服务器：
   ```bash
   python feishu_server.py
   ```
3. 启动 ngrok 隧道：
   ```bash
   ngrok http 8000
   ```
4. 复制 ngrok 提供的公网 URL（如 `https://abc123.ngrok.io`）

**方式二：云服务器部署**

1. 将项目部署到云服务器（阿里云/腾讯云/AWS）
2. 配置防火墙开放 8000 端口
3. 使用域名或公网 IP 访问

### 3.2 配置事件订阅 URL

1. 进入"事件订阅" → "请求网址配置"
2. 填写请求网址：
   ```
   https://your-domain.com/feishu/webhook
   ```
   或（ngrok）：
   ```
   https://abc123.ngrok.io/feishu/webhook
   ```
3. 点击"保存"，系统会发送验证请求
4. 如果配置正确，会显示"验证成功"

### 3.3 订阅事件

进入"事件订阅" → "添加事件"，订阅以下事件：

- `im.message.receive_v1` - 接收消息（必需）

点击"保存"。

---

## 四、配置环境变量

编辑 `.env` 文件，填入飞书应用凭证：

```env
# ── 飞书应用凭证 ──────────────────────────────────────────────
FEISHU_APP_ID=cli_a1b2c3d4e5f6g7h8
FEISHU_APP_SECRET=abcdefghijklmnopqrstuvwxyz123456
FEISHU_VERIFICATION_TOKEN=xyz789abc123def456
FEISHU_ENCRYPT_KEY=

# 飞书服务器端口
PORT=8000

# ── API 配置（必需）──────────────────────────────────────────────
API_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-your-key-here
LLM_MODEL=deepseek-v4-flash

# ── 数据库配置（必需）──────────────────────────────────────────────
USE_REAL_DB=true
DB_HOST=localhost
DB_PORT=3306
DB_USER=data_analyst
DB_PASSWORD=analyst_readonly_2024
DB_NAME=data_analysis
```

---

## 五、启动服务

### 5.1 安装依赖

```bash
pip install -r requirements.txt
```

### 5.2 初始化数据库

```bash
mysql -u root -p < init_database.sql
```

### 5.3 启动飞书服务器

```bash
python feishu_server.py
```

输出示例：
```
============================================================
🚀 飞书数据分析机器人服务器启动
============================================================
监听端口: 8000
Webhook URL: http://your-domain:8000/feishu/webhook
API 提供商: siliconflow
LLM 模型: deepseek-v4-flash
数据库模式: 真实 MySQL
============================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
```

---

## 六、测试机器人

### 6.1 在飞书中测试

1. 打开飞书客户端
2. 搜索机器人名称：`数据分析助手`
3. 发送消息：
   ```
   分析过去一个月的销售趋势
   ```
4. 等待机器人回复（约 10-30 秒）

### 6.2 使用测试接口

不通过飞书，直接测试分析功能：

```bash
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"question": "分析过去一个月的销售趋势"}'
```

---

## 七、常见问题

### Q1: 事件订阅 URL 验证失败

**原因：**
- 服务器未启动
- 防火墙阻止访问
- ngrok 隧道断开

**解决：**
1. 确认服务器正在运行：`curl http://localhost:8000/health`
2. 确认公网可访问：`curl https://your-domain.com/health`
3. 检查防火墙规则

### Q2: 机器人不回复消息

**原因：**
- 权限未开通
- 事件未订阅
- 服务器崩溃

**解决：**
1. 检查权限是否已审核通过
2. 检查事件订阅是否包含 `im.message.receive_v1`
3. 查看服务器日志：`python feishu_server.py`

### Q3: 分析失败或超时

**原因：**
- API Key 无效
- 数据库连接失败
- LLM 调用超时

**解决：**
1. 检查 `.env` 配置是否正确
2. 测试 API 连接：`python test_api.py`
3. 测试数据库连接：`mysql -u data_analyst -p data_analysis`

### Q4: 卡片消息发送失败

**原因：**
- 卡片格式错误
- 权限不足

**解决：**
- 系统会自动降级为文本消息
- 检查飞书开放平台日志

---

## 八、生产环境部署建议

### 8.1 使用进程管理器

使用 `supervisor` 或 `systemd` 管理服务：

```bash
# 安装 supervisor
sudo apt install supervisor

# 创建配置文件
sudo nano /etc/supervisor/conf.d/feishu-bot.conf
```

配置内容：
```ini
[program:feishu-bot]
directory=/path/to/data_analysis_agents
command=/usr/bin/python3 feishu_server.py
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/feishu-bot.err.log
stdout_logfile=/var/log/feishu-bot.out.log
```

启动服务：
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start feishu-bot
```

### 8.2 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /feishu/ {
        proxy_pass http://127.0.0.1:8000/feishu/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 8.3 配置 HTTPS

使用 Let's Encrypt 免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 8.4 监控和日志

- 使用 `tail -f /var/log/feishu-bot.out.log` 查看实时日志
- 配置日志轮转：`logrotate`
- 监控服务状态：`supervisorctl status feishu-bot`

---

## 九、示例对话

**用户：** 分析过去一个月的销售趋势

**机器人：** 🤖 收到您的问题，正在分析中，请稍候...

**机器人：** 📊 数据分析报告

**用户问题：**
分析过去一个月的销售趋势

**分析报告：**

## 核心结论
过去一个月（2024年11月）销售表现稳健，总订单量达到 42 单，完成订单 34 单，总销售额 ¥45,678.90。

## 数据解读
1. **订单完成率**：81% (34/42)，高于行业平均水平
2. **客单价**：¥1,343.50，同比增长 12%
3. **热销品类**：Electronics 占比 45%，Clothing 占比 30%
4. **地区分布**：North 地区贡献 35% 销售额

## 业务建议
1. 加大 Electronics 品类库存，满足旺季需求
2. 优化 South 地区物流，提升订单完成率
3. 针对高客单价用户推出会员计划

**生成的 SQL：**
```sql
SELECT
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(*) as total_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) as total_revenue
FROM orders
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
GROUP BY month
```

生成时间：2026-04-27 15:30:45

---

## 十、进阶功能

### 10.1 支持群聊 @机器人

机器人已自动支持群聊 @提问：

1. 将机器人拉入群聊
2. @机器人 + 问题：`@数据分析助手 分析用户活跃度`

### 10.2 自定义卡片样式

修改 `tools/feishu_bot.py` 中的 `format_report_as_card()` 方法，自定义卡片颜色、布局等。

### 10.3 添加快捷命令

在 `feishu_server.py` 中添加命令处理逻辑：

```python
if message_content.startswith("/help"):
    feishu_bot.send_text_message(
        receive_id=sender_id,
        text="我可以帮你分析数据！\n\n示例问题：\n- 分析过去一个月的销售趋势\n- 统计各地区用户数量\n- 查询热销商品 TOP 10",
        receive_id_type="open_id"
    )
    return jsonify({"code": 0})
```

---

## 十一、安全注意事项

1. **使用只读数据库账号**：`data_analyst` 账号只有 SELECT 权限
2. **启用 SQL 安全检查**：自动拦截 DROP/DELETE 等危险操作
3. **限制查询结果行数**：自动添加 LIMIT 500 保护
4. **验证飞书签名**：防止伪造请求
5. **不要泄露 API Key**：`.env` 文件不要提交到 Git

---

## 十二、成本估算

**使用硅基流动 + DeepSeek V4：**
- 单次分析成本：¥0.01-0.05
- 每天 100 次查询：¥1-5
- 每月成本：¥30-150

**使用 Anthropic + Claude：**
- 单次分析成本：$0.5-1.0
- 每天 100 次查询：$50-100
- 每月成本：$1500-3000

**建议：** 生产环境使用硅基流动，成本仅为 Claude 的 1/10。

---

## 联系支持

如有问题，请提交 Issue 或联系开发者。
