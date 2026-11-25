# 已验证的临时连接方法：官方 WireGuard 经 Clash SOCKS5 UDP

2026-11-25 的 E6/E9 两轮已成功完成 WireGuard 握手；E9 完整读取四台服务器的 SSH banner 和主机公钥。未进行账号登录认证、长时间稳定性或吞吐测试。

本方法保留官方 WireGuard 客户端处理所有密钥和加密。本地 Python 工具只把已经加密的 WireGuard UDP 数据报交给现有 SOCKS5 UDP 代理，代码中没有 WireGuard 私钥。不要用 HTTP CONNECT 或普通 TCP 端口转发代替 UDP 中转。

## 前提

- 本机已安装 `wireguard-tools`、`wireguard-go`、Homebrew Bash 4+ 和 Python 3。
- Clash 在 `127.0.0.1:7890` 提供无需额外认证的 SOCKS5 UDP 服务，选定的代理链支持并实际能传输 UDP；本次运行时链类型为 AnyTLS。
- 保持 Clash 系统代理，关闭其 TUN；不要同时启动本机原来的直连 WireGuard 配置与此配置。
- 配置使用这台设备已经获分配的私钥；公开仓库没有私钥，不能从示例自动建立认证。

## 1. 准备本地配置

原设备已经保存了私钥齐全的本地文件 `~/.config/wireguard/HKU-SH-proxy.conf`（权限 0600）。其它设备请由管理员分配独立配置，不要共用同一设备身份。

相对本次直连配置，只有传输入口改变为：

```ini
[Interface]
PrivateKey = <existing local private key>
Address = 10.200.0.5/24
MTU = 1280

[Peer]
PublicKey = 6C6IP2TPYqsQSYeJD4aMKihY0+8crOCGjbqFQLGeilE=
Endpoint = 127.0.0.1:52999
AllowedIPs = 10.200.0.0/24, 10.128.13.0/24
PersistentKeepalive = 25
```

`127.0.0.1:52999` 是本机中转。中转的真实远端固定为 `114.94.188.196:50015`。详见 [公开样例](config/HKU-SH-Lab-proxy.redacted.conf)。

## 2. 终端 A：启动中转

在此仓库目录中运行：

```bash
python3 -u diagnostics/socks-udp-relay.py
```

应看到 `SOCKS UDP ASSOCIATE OK`。让这个终端保持运行。此工具只支持本次受控的单个客户端 / 单个实验室入口，没有自动重连、后台服务或常驻安装。

如需独立确认代理 UDP 能工作，可先执行：

```bash
python3 diagnostics/socks-udp-relay.py --check proxy
```

它查询 `1.1.1.1:53` 的 `example.com` A 记录，不使用本地私有域名。DNS 成功只是前置能力检查，不保证实验室握手成功。

## 3. 终端 B：启动官方系统隧道

```bash
sudo /opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick up ~/.config/wireguard/HKU-SH-proxy.conf
sudo /opt/homebrew/bin/wg show
nc -G 10 -w 3 -vz 10.128.13.133 22
```

预期 `wg show` 出现近期的 `latest handshake` 及双向流量，端口探测显示 succeeded。之后才使用你自己的实验室 SSH 用户名和 SSH 身份进行登录。本仓库不设置或保存 SSH 密码，不修改 known_hosts。

## 4. 结束

先停止隧道，再在终端 A 按 Ctrl-C 退出中转：

```bash
sudo /opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick down ~/.config/wireguard/HKU-SH-proxy.conf
```

如果代理节点或本机网络发生变化，中转可能需要重启。本方法是一次已验证的排障 / 临时连接方式，不代替网管修复直连链路。没有在本机安装自动启动服务。
