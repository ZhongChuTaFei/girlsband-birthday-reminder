# 🌸 少女乐队生日提醒

一个运行在 **GitHub Actions** 上的 Python 脚本，通过企业微信机器人 Webhook 自动发送少女乐队角色及其声优的生日祝福。

---

## ✨ 功能速览

* ~~**GitHub Actions 自动运行**：每日日本时间0点自动运行，无需额外服务器。~~ Github Actions因推送延迟原因默认不启用 如需启用请查看[部署步骤](https://github.com/ZhongChuTaFei/girlsband-birthday?tab=readme-ov-file#%E9%83%A8%E7%BD%B2%E6%AD%A5%E9%AA%A4)中第3步
* **企业微信机器人兼容**：默认支持企业微信机器人消息格式。
* **Webhook 安全管理**：Webhook URL 通过 GitHub Secrets 配置，确保安全。
* **内置生日数据**：
    * 包含 **BanG Dream! 中十二个乐队的角色**生日：Poppin'Party、Afterglow、Pastel*Palettes、Roselia、Hello, Happy World!、Morfonica、RAISE A SUILEN、MyGO!!!!!、Ave Mujica、梦限大MewType、Millsage、一家Dumb Rock!。
    * 包含 **BanG Dream! 中十一个乐队的角色声优**生日：Poppin'Party、Afterglow、Pastel*Palettes、Roselia、Hello, Happy World!、Morfonica、RAISE A SUILEN、MyGO!!!!!、Ave Mujica、Millsage、一家Dumb Rock!。
    * 包含 **Girls Band Cry 中一个乐队的角色**生日：TOGENASHI TOGEARI。
    * 包含 **Girls Band Cry 中两个乐队的角色声优**生日：TOGENASHI TOGEARI、Diamond Dust。

---

## 🚀 快速开始

### 部署步骤

1.  **Fork 此仓库**：将本仓库 Fork 到您的 GitHub 账户。
2.  **配置 Webhook URL**：
    * 在您的 Fork 仓库中，进入 `Settings` -> `Secrets and variables` -> `Actions` 。
    * 点击 `New repository secret`。
    * **名称 (Name)**：`WEBHOOK_URL`
    * **值 (Value)**：填入您的**企业微信机器人 Webhook URL**。
3.  **启用 GitHub Actions自动推送**：
    * 前往 `.github/workflows/birthday.yml` 取消第4-6行注释（删除行前的`#`）
    * 进入您的 Fork 仓库的 `Actions` 选项卡。
    * 启用工作流。

---
## ▶️ 运行示例

### $\color{#ea9f00}{🎂邦多利生日提醒}$
>现在是日本时间7月14日0点整，7月14日是Poppin'Party的主唱、吉他手，**户山香澄**的生日，祝她生日快乐🎉！

### $\color{#ea9f00}{🎂邦多利生日提醒}$
>现在是日本时间12月25日0点整，12月25日是Poppin'Party的主唱、吉他手，户山香澄的声优**爱美**的生日，祝她生日快乐🎉！

---
## ⚙️ 自定义与维护

### 1. 数据结构说明
每条数据都是一个 JSON 对象，各字段含义如下：

| 字段名 | 说明 | 是否必填 |
| :--- | :--- | :--- |
| `name` | 姓名（角色或声优） | 是 |
| `band` | 乐队/团体名称 | 是 |
| `role` | 职位/角色描述 | 是 |
| `birthday` | 生日（格式 MM-DD） | 是 |
| `project` | 企划代号（如 GBC）。若不填，默认为邦多利 | 否 |
| `character` | 若该条目为声优，需填写对应的角色名 | 否 |

### 2. 编辑示例
```json
// 示例 1：角色生日
{
    "name": "户山香澄",
    "band": "Poppin'Party",
    "role": "主唱、吉他手",
    "birthday": "07-14"
}

// 示例 2：声优生日
{
    "name": "爱美",
    "character": "户山香澄",
    "band": "Poppin'Party",
    "role": "主唱、吉他手",
    "birthday": "12-25"
}

// 示例 3：GBC 企划角色生日
{
    "name": "井芹仁菜",
    "band": "TOGENASHI TOGEARI",
    "role": "主唱",
    "birthday": "10-24",
    "project": "GBC"
}
```

### 3. 进阶配置
企划名称映射：如果你添加了新的企划代号，请同步修改 main.py 中的 PROJECT_MAP 字典，以便在消息推送中显示正确的中文名称：

```Python
PROJECT_MAP = {
    "GBC": "嘎嘣脆",
    "MY_NEW_PROJECT": "新企划名称"
}
```
* 特殊说明：若 character 字段包含 ex 后缀（如 "今井莉莎ex"），程序将自动去除该后缀，并在推送文案中将“声优”描述调整为“前声优”。