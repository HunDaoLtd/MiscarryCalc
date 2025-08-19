# MiscarryCalc

一款基于 uni-app + Flask 的超声报告智能解析与孕周/停育辅助计算工具。用户拍摄或上传早孕期超声报告单，系统自动识别关键字段（如孕囊大小 GS、胚芽长 CRL、超声检查日期、是否停育等），给出多种孕周估算结果，并在存在“停育”时推算末次月经（LMP）、停育日期以及“预自然流产日”（含 25%/50%/75% 时间点参考）。

> 重要提示：本项目仅用于学习与科研探索，不能替代临床诊断或医疗建议。

## 主要功能
- 拍摄/上传报告图，自动识别并解析核心字段
- 同屏对比“停育前报告”与“当前报告”，辅助判断与时间线推断
- 孕周估算支持：
  - 孕囊估算（早期）
  - Robinson 公式（推荐）
  - 回归方程
  - 经验法则
  - Hadlock 公式（CRL 多项式）
- 自动计算：
  - 末次月经（LMP）= 检查日期 - 孕周（天）
  - 停育日期 = LMP + 当前孕周（天）
  - 预自然流产日 = 停育日期 + 23 天，并提供 15/23/32 天三个概率时间点参考
- 日期一致性校验：提示“当前报告日期早于停育前报告日期”的异常

## 技术栈
- 前端：uni-app（Vue 3 + `<script setup>`）
- 组件：`uni-popup`、`uni-transition`、`uni-scss`
- 后端：Flask + OpenAI SDK + MySQL（示例脚本见 `backend/miscarry_calc.py`）
- 数据库：MySQL（图片分析结果结构化存储 + 去重缓存）

## 必装插件
uni-popup 弹出层：https://ext.dcloud.net.cn/plugin?name=uni-popup  
uni-file-picker 文件选择上传：https://ext.dcloud.net.cn/plugin?id=4079

## 目录结构
```
.
├─ App.vue
├─ main.js
├─ pages.json
├─ manifest.json
├─ uni.scss
├─ uni.promisify.adaptor.js
├─ pages/
│  └─ index/index.vue    # 主要页面与逻辑
├─ uni_modules/
│  ├─ uni-popup/
│  ├─ uni-transition/
│  └─ uni-scss/
├─ backend/
│  ├─ miscarry_calc.py        # Flask 主服务（上传 & 分析）
│  ├─ mysql_op.py             # MySQL 封装
│  └─ requirements.txt        # 后端依赖（可选新增）
├─ static/logo.png
├─ LICENSE (MIT)
└─ README.md
```

## 后端接口
`backend/miscarry_calc.py` 暴露的核心 REST 接口（默认端口 5003）：

| 功能 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 上传/覆盖图片 | POST / PUT | `/images/{filename}` | form-data: file=<二进制>，成功返回 `{success: true}` |
| 获取已上传图片 | GET | `/images/{filename}` | 静态访问（含长期缓存头） |
| 分析图片（含缓存命中） | GET | `/analysis/{filename}` | 返回识别 JSON，若首次或强制则调用大模型 |
| 强制重新分析 | GET | `/analysis/{filename}?force=1` | 或加请求头 `X-Force-Analyze: true` |

返回 JSON（示例）：
```json
{
  "孕囊大小": 18,
  "胚芽长": 6,
  "是否停育": false,
  "日期": "2025-08-01"
}
```

前端示例中历史演示域名与路径可能与当前代码不同；若自建后端，请在 `pages/index/index.vue` 中搜索并修改：
`uploadFileUnified` / `getAnalysisResultUnified` / `executeTest` 中的 baseURL。

### 强制刷新分析
出现以下情况可以考虑使用 `force=1`：
1. 原始图像质量提升（重新上传更清晰版本）
2. 模型策略 / Prompt 调整
3. 数据库中缓存结果异常

### 依赖的环境变量
| 变量名 | 作用 | 必需 |
|--------|------|------|
| `ENV_METACHAT_API_KEY` | OpenAI 兼容接口 API Key | 是 |

### 可选修改
`UPLOAD_DIR`（默认 `/var/hundao/apps/1_miscarry_calc/images`）可改为本地可写目录，例如开发时改为 `./uploads`。

### 数据库存储
`mysql_op.py` 中定义表（简化摘录）：
```sql
CREATE TABLE IF NOT EXISTS `miscarry_calc_data` (
  `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `json` JSON NOT NULL,
  `gs_mm` INT UNSIGNED NULL,
  `crl_mm` INT UNSIGNED NULL,
  `miscarry` TINYINT(1) NULL,
  `exam_date` DATE NULL,
  `hash` CHAR(64) NOT NULL UNIQUE,
  `ext` VARCHAR(10) NOT NULL,
  `mime` VARCHAR(64) NOT NULL,
  `size` INT UNSIGNED NOT NULL,
  `width` INT UNSIGNED NULL,
  `height` INT UNSIGNED NULL,
  `stored_path` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_used_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_created_at` (`created_at`),
  KEY `idx_last_used_at` (`last_used_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> 注意：`decrypt_db_data("1_miscarry_calc")` 依赖的解密逻辑（`common/decrypt.py` 等）未包含在本仓库。若本地开发，可直接改写为使用明文配置或环境变量读取数据库连接信息。

### 后端本地运行（开发）
1. 进入项目根目录：`cd backend`
2. 创建虚拟环境（可选）
3. 安装依赖：参考 `requirements.txt`
4. 设置环境变量 `ENV_METACHAT_API_KEY`
5. (可选) 修改 `miscarry_calc.py` 中的 `UPLOAD_DIR` 为相对路径
6. 初始化数据库（手动执行建表 SQL，或在启动前调用 `create_miscarry_calc_data_table_if_not_exist`）
7. 运行：`python miscarry_calc.py`（默认端口 5003）

开发快速替换：可临时注释掉数据库相关逻辑，将分析结果直接返回以脱离 MySQL 依赖进行前端调试。

### 依赖概览
| 包 | 用途 |
|----|------|
| Flask / flask-cors | Web 服务与跨域 |
| openai | 调用兼容 OpenAI 接口模型（图像 + 文本） |
| pymysql | MySQL 访问 |
| pypushdeer | 上传事件推送（可选） |
| Pillow (可选) | 读取图片宽高 |

### 安全与限流建议（未默认实现）
- 上传大小限制：当前 `MAX_CONTENT_LENGTH = 1MB`，可根据业务调整
- 增加文件名白名单 / 随机化 hash
- 对外网部署需考虑：鉴权（临时 Token）、速率限制、异常报警
- 模型成本控制：可将重复图像 hash 去重（现已通过数据库唯一索引），并增加配额统计

## 前端本地运行
本仓库适合使用 HBuilderX 打开与运行。

方式 A：HBuilderX（推荐）
1. 安装 HBuilderX（3.x+）
2. 文件 -> 打开目录 -> 选择项目根
3. 运行到浏览器（H5）或 App/小程序 等目标平台

方式 B：UniApp CLI（需自建）
本仓库未包含 `package.json`。如需 CLI：
1. 使用官方脚手架创建全新 uni-app 项目
2. 拷贝本仓库以下文件/目录覆盖：`App.vue`、`main.js`、`pages.json`、`manifest.json`、`pages/`、`uni_modules/`、`static/`、`uni.scss`、`uni.promisify.adaptor.js`
3. 启动 CLI 项目 (`npm run dev:h5` 等)

## 使用说明
1. 进入首页，点击“拍摄超声报告单”上传当前报告
2. 若结果提示“停育”，可继续上传“胎停育前报告单”以获得 LMP、停育日期与“预自然流产日”等推算
3. 可在“超声检查日期（停育前）”处手动校正日期
4. 点击“预自然流产日”行可查看 25%/50%/75% 时间点参考

## 数据与隐私
- 上传的图片会发送至配置的服务器地址进行识别与分析。请在生产环境中替换为自有后端，并确保合法合规以及充分的隐私与安全保护。
 - 建议对上传内容做：最小化存储 / 定期清理 / 访问审计 / 敏感字段脱敏。

## 免责声明
- 本项目仅作技术演示与教学用途，不提供医疗诊断或治疗建议。
- 任何基于本项目产生的结论请务必由专业医生判读与确认。
 - 作者不对使用本项目造成的直接或间接后果承担责任。

## 许可证
本项目使用 MIT License，详见 `LICENSE`。

---
若发现文档与代码不一致，请提交 Issue 或 PR。欢迎共建。
