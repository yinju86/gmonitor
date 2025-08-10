# GMonitor 使用说明

## 简介

GMonitor 是一个自动化监听群聊并自动查询股票信息的工具。你可以直接下载可执行文件使用，无需安装 Python，也可以选择从源码运行。

---

## 一、直接下载使用（推荐）

1. **前往 [GitHub Releases 页面](https://github.com/你的仓库地址/releases) 下载最新版 `g.exe` 和 `config.json` 文件。**
2. **将 `g.exe` 和 `config.json` 放在同一个文件夹内。**
3. **双击运行 `g.exe`，程序会自动打开浏览器并开始工作。**

> ⚠️ 请先用文本编辑器打开 `config.json`，填写你的账号、密码、群名称和机器人 Webhook 地址。

---

## 二、从源码运行（开发者/高级用户）

1. **安装 [Python 3.10](https://www.python.org/downloads/release/python-3100/)。**
2. **在项目目录下打开命令行，执行：**
   ```shell
   pip install -r requirements.txt
   ```
3. **配置 `config.json` 文件，填写你的账号、密码、群名称和机器人 Webhook 地址。**
4. **运行程序：**
   ```shell
   python g.py
   ```

---

## 常见问题

- **浏览器驱动问题**  
  默认使用 Chrome 浏览器。请确保已安装最新版 Chrome，并将 [ChromeDriver](https://chromedriver.chromium.org/downloads) 放入系统 PATH 或与 `g.exe` 同目录。

- **配置问题**  
  `config.json` 必须与 `g.exe` 在同一目录，内容需正确填写。

---

如有疑问，请在 GitHub Issues 提交