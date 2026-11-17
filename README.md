## PUMC 校园网自动登录

使用 Selenium + 系统 Chromium/ChromeDriver 登录 SRun 校园网，支持后台保活。

### 依赖

Python 3、`selenium`、`curl`，以及版本匹配的 Chromium 和 `/usr/bin/chromedriver`。

### 运行

```bash
python login.py --username YOUR_ACCOUNT --password YOUR_PASSWORD --need_keep True --tolerance -1
```

建议在 `tmux` 的 `network` 会话内运行。保留原有参数兼容性；`--need_keep False` 只检查/登录一次，成功退出码 0，失败退出码 1。`--tolerance -1` 无限重试，正整数为允许的连续失败次数。

### 行为

- 先通过 `/cgi-bin/rad_user_info` 区分在线、离线及查询失败。
- 仅明确离线时启动浏览器；在线但外网异常时不重复提交账号密码。
- 等待输入框可见和按钮可点击；提交后等待认证接口确认在线，再检测外网 HTTPS。两项均通过才报告 `Login successful`。
- 外网检测使用百度 HTTPS，失败后回退到 NCBI HTTPS；绕过代理，DNS/连接/请求均有超时。
- 正常每 60 秒检测，失败时逐步退避至最多 300 秒；浏览器仅在重新登录时创建，完成后关闭。
- 在自动化浏览器中关闭 `HttpsFirstBalancedModeAutoEnable`，兼容 Chromium 157 对原有 HTTP 校园网入口的拦截；不修改全局浏览器或系统配置，不忽略 TLS 证书校验。

**安全边界：** 默认入口仍为校园网原有 HTTP 地址，账号密码提交不受 TLS 保护。命令行密码可能被同机用户通过进程列表看到，请勿分享进程参数、终端历史或含启动命令的截图。

### 测试

```bash
python -m unittest -v test_login
```
