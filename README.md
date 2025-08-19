# MiscarryCalc

一款基于 uni-app 的超声报告智能解析与孕周/停育辅助计算工具。用户拍摄或上传早孕期超声报告单，系统自动识别关键字段（如孕囊大小 GS、胚芽长 CRL、超声检查日期、是否停育等），给出多种孕周估算结果，并在存在“停育”时，推算末次月经（LMP）、停育日期以及“预自然流产日”（含 25%/50%/75% 时间点参考）。

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
- 内置测试数据，一键演示完整流程

## 技术栈
- 前端：uni-app（Vue 3 + `<script setup>`）
- 组件：`uni-popup`、`uni-transition`、`uni-scss`
- 后端：Python RESTful 服务（示例脚本见 `backend/Hun_RESTful/1_MiscarryCalc.py`）

## 必装插件：
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
│  └─ Hun_RESTful/1_MiscarryCalc.py   # 后端示例脚本
├─ static/logo.png
├─ LICENSE (MIT)
└─ README.md
```

## 后端接口（示例）
前端默认使用已部署的演示服务：
- 上传图片：`POST https://apps.hundao.xyz/rendered/{fileName}`
- 获取分析结果：`GET https://apps.hundao.xyz/1_MiscarryCalc/analysis/{fileName}`
- 测试数据：
  - 当前报告（非停）：`GET .../analysis/test`
  - 当前报告（停育）：`GET .../analysis/test2`
  - 停育前报告：`GET .../analysis/test4`

如需自建后端或替换域名，请修改：
- `pages/index/index.vue` 中的 `uploadFileUnified()`、`getAnalysisResultUnified()` 与 `executeTest()` 的接口地址

## 本地运行
本仓库更适合使用 HBuilderX 打开与运行。

方式 A：HBuilderX
1. 安装 HBuilderX（3.x 及以上）
2. 通过“文件 -> 打开目录”，选择本项目根目录
3. 运行到浏览器（H5）或各平台模拟器/真机调试

方式 B：VS Code + 插件（不推荐本仓库直接 CLI 运行）
- 本仓库未包含 UniApp CLI 的 `package.json`。若需 CLI 方式，请先用官方脚手架创建一个 uni-app 项目，然后把本仓库的以下文件/目录拷贝到新项目中：
  - `App.vue`、`main.js`、`pages.json`、`manifest.json`
  - `pages/`、`uni_modules/`、`static/`、`uni.scss`、`uni.promisify.adaptor.js`

## 使用说明
1. 进入首页，点击“拍摄超声报告单”上传当前报告
2. 若结果提示“停育”，可继续上传“胎停育前报告单”以获得 LMP、停育日期与“预自然流产日”等推算
3. 可在“超声检查日期（停育前）”处手动校正日期
4. 点击“预自然流产日”行可查看 25%/50%/75% 时间点参考
5. 可用“测试”按钮快速演示

## 数据与隐私
- 上传的图片会发送至配置的服务器地址进行识别与分析。请在生产环境中替换为自有后端，并确保合法合规以及充分的隐私与安全保护。

## 免责声明
- 本项目仅作技术演示与教学用途，不提供医疗诊断或治疗建议。
- 任何基于本项目产生的结论请务必由专业医生判读与确认。

## 许可证
本项目使用 MIT License，详见 `LICENSE`。
