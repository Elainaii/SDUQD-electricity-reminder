# 山东大学青岛校区宿舍电量查询与提醒

> Fork 自[原项目](https://github.com/Dregen-Yor/SDU-QD-Electricity-Query-Script)，修改为使用 Server酱 进行微信推送提醒

## 项目简介

基于山大V卡通2.0版本的宿舍电量查询脚本，无需登录即可查询宿舍当前电费余量。

本项目使用 **Server酱** 进行微信推送，配合 **GitHub Actions** 实现自动定时检测并提醒，当宿舍电量低于设定阈值时会自动推送消息到微信。

## 功能特点

- ✅ 自动查询宿舍电量
- ✅ 低电量自动微信推送提醒（通过 Server酱）
- ✅ GitHub Actions 定时任务，无需本地运行
- ✅ 支持自定义电量阈值
- ✅ Markdown 格式消息，美观易读

## 支持楼栋

目前可查 `S1 S2 S5 S6 S7 S8 S9 S10 S11 B1 B2 B5 B9 B10 T1 T2 T3`

## 前置准备

### 1. 获取 Synjones-Auth 字段

`Synjones-Auth` 字段经测试不会过期，可以长期使用。获取方法有两种：

- [网页端抓包教程](guide/网页端抓包教程.md)（推荐，较为简单）
- [手机端抓包教程](guide/burpsuite手机抓包教程.md)

**注意：** 网页端重新登录后字段会失效，推荐使用网页端抓包后不再登录网页版V卡通。

### 2. 获取 Server酱 SendKey

1. 访问 [Server酱官网](https://sct.ftqq.com/)
2绑定微信（用于接收推送消息）
3在控制台获取你的 `SendKey`

## 使用方法

### 方式一：使用 GitHub Actions（推荐）

1. **Fork 本仓库**

2. **配置 GitHub Secrets**
   
   在仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下密钥：
   
   - `SENDKEY`: 你的 Server酱 SendKey
   - `SYNJONES_AUTH`: 抓包获取的 Synjones-Auth 字段

3. **修改配置**（可选）
   
   编辑 `auto-script.py` 中的以下参数：
   - 第 40 行：修改楼栋和房间号
   - 第 50 行：修改电量阈值

4. **启用 Actions**
   
   在仓库的 `Actions` 页面启用工作流，脚本会在每天 **北京时间 8:00** 自动运行

### 方式二：本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
2. **运行脚本**
   ```bash
   python auto-script.py --sendkey "你的SendKey" --Synjones_Auth "你的认证信息"
   ```

## 配置说明

### 修改检测时间

编辑 `.github/workflows/SduElectricityReminder.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 0:00，对应北京时间 8:00
```

### 修改电量阈值

编辑 `auto-script.py` 第 50 行：

```python
if last_value < 10:  # 修改此处的数值，当电量低于该值时发送提醒
```

### 修改楼栋房间号

编辑 `auto-script.py` 第 40 行：

```python
last = query("S1", "a114", Synjones_Auth=Synjones_Auth)  # 修改楼栋和房间号
```

## 依赖环境

- Python 3.12.7
- requests
- pyyaml

## 隐私声明

- 所有认证信息存储在 GitHub Secrets 中，安全加密
- 推送服务使用 Server酱，仅推送到你绑定的微信
- 不会保存或上传任何其他用户数据

## 致谢

本项目 Fork 并修改自原项目，感谢原作者的贡献。

## 许可证

本项目仅供学习交流使用，请勿用于商业用途。
