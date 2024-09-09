## background
协和的校园网限制比较严格，只允许登录三个设备，且网络不稳定，这些都容易导致关键设备掉线。
该脚本是为了实现让服务器等长期开启的设备能够一直保持一个设备占用，需要自取。
有任何问题欢迎issue。

## dependence
代码在python 3.8上测试过，理论上更高版本也能用。
推荐使用anaconda做版本的隔离。
```bash
pip install selenium
```
## run
```bash
# 如果需要监听掉线并及时联网的话，需要结合tmux开后台来使用，否则关掉窗口以后python进程就断了
python login.py --username XXX --password XXX --need_keep <True or False>
```