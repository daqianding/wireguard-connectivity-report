# 对话工具输出摘录

以下内容从本次对话中已返回的工具结果整理。没有对应原始文件的轮次，其输出不能视作完整原始日志。未独立保存的时间和字段标为未知，不从相邻轮次推定。

## T0：未启动 WireGuard 时的基线

本机没有找到 `wg`、`wg-quick`、`wireguard-go`，未找到 App Store WireGuard 应用。到内网服务器和公网入口的路由均指向 `en0`、网关 `10.68.0.1`。

```text
10.128.13.130:22 TimeoutError: timed out
10.128.13.131:22 TimeoutError: timed out
10.128.13.132:22 TimeoutError: timed out
10.128.13.133:22 TimeoutError: timed out
```

探测使用本机 Python socket，每个连接超时 5 秒；此时没有 WireGuard 隧道，因此该基线失败不构成协议故障证据。

## T1：临时用户态 netstack 测试

以下开头的说明文字由测试程序打印，不是官方 WireGuard GUI 的日志。程序使用官方 `wireguard-go` 的 `device`、`conn.NewDefaultBind()`、`tun/netstack`，进程内地址是 `10.200.0.5`、MTU 1380；未安装系统路由。

```text
Temporary userspace WireGuard started; native UDP transport; no HTTP/SOCKS proxy; system routes unchanged.
10.128.13.131:22 FAILED after 35.001s: context deadline exceeded
10.128.13.133:22 FAILED after 35.001s: context deadline exceeded
10.128.13.132:22 FAILED after 35.001s: context deadline exceeded
10.128.13.130:22 FAILED after 35.001s: context deadline exceeded
endpoint=114.94.188.196:50015
last_handshake_time_sec=0
last_handshake_time_nsec=0
tx_bytes=1036
rx_bytes=0
```

另一次观察到该进程绑定本地 UDP `58043`。没有为这轮保存抓包，因此不能把 1036 字节直接写成“抓到 7 个包”。程序及临时私钥文件随后删除。

首次依赖解析曾出现 `ambiguous import`：独立旧 `tun/netstack` 模块与主模块同时提供同名包。固定主模块 `golang.zx2c4.com/wireguard v0.0.0-20261024220952-b3bc704ef0ee` 后，依赖整理和编译成功，才开始以上网络测试。该构建错误发生在发包前。

## T3：15:22:30–15:23:15，系统代理开启，MTU 1380

运行版本：wireguard-tools `1.0.20260223`、wireguard-go `0.0.20250522`。本地接口 `utun7`，本地 UDP 端口 `54670`。

关键日志摘录：

```text
DEBUG: (utun7) 2026/11/25 15:22:30 peer(6C6I…eilE) - Sending handshake initiation
DEBUG: (utun7) 2026/11/25 15:22:35 peer(6C6I…eilE) - Handshake did not complete after 5 seconds, retrying (try 2)
DEBUG: (utun7) 2026/11/25 15:22:35 peer(6C6I…eilE) - Sending handshake initiation
10.128.13.130:22 FAILED after 45.004s; timeout: timed out
10.128.13.131:22 FAILED after 45.004s; timeout: timed out
10.128.13.132:22 FAILED after 45.004s; timeout: timed out
10.128.13.133:22 FAILED after 45.004s; timeout: timed out
transfer: 0 B received, 1.30 KiB sent
HTTPEnable : 1
HTTPSEnable : 1
SOCKSEnable : 1
```

公网抓包摘录中的 9 个数据包均为同方向：

```text
10.68.209.149.54670 > 114.94.188.196.50015: [udp sum ok] UDP, length 148
```

包时间（UTC+08:00）：

```text
2026-11-25 15:22:30.113438
2026-11-25 15:22:35.149960
2026-11-25 15:22:40.370386
2026-11-25 15:22:45.488035
2026-11-25 15:22:50.609765
2026-11-25 15:22:55.659756
2026-11-25 15:23:00.679272
2026-11-25 15:23:05.995640
2026-11-25 15:23:11.029464
```

```text
9 packets captured
6550 packets received by filter
0 packets dropped by kernel
```

对应 IPv4 总长度均为 176，TTL 64，fragment offset 0，flags `[none]`。没有匹配的入站记录。隧道内抓包显示源地址 `10.200.0.5` 向四台服务器的 22 端口发 SYN 并重传，共捕获 40 个包。

## T4：15:25:20–15:26:05，系统代理关闭，MTU 1380

同一服务器入口、密钥、允许网段、接口及 MTU。本地 UDP 端口随机变为 `59354`。脚本末尾明确记录：

```text
HTTPEnable : 0
HTTPSEnable : 0
SOCKSEnable : 0
ProxyAutoConfigEnable : 0
```

这能证明记录时系统代理关闭；没有单独保存这一轮 Clash 进程列表，不能仅据此证明所有 Clash 组件完全退出。

关键输出：

```text
DEBUG: (utun7) 2026/11/25 15:25:20 peer(6C6I…eilE) - Sending handshake initiation
DEBUG: (utun7) 2026/11/25 15:25:30 peer(6C6I…eilE) - Handshake did not complete after 5 seconds, retrying (try 2)
10.128.13.130:22 FAILED after 45.003s; timeout: timed out
10.128.13.131:22 FAILED after 45.003s; timeout: timed out
10.128.13.132:22 FAILED after 45.003s; timeout: timed out
10.128.13.133:22 FAILED after 45.003s; timeout: timed out
transfer: 0 B received, 1.30 KiB sent
```

公网抓包中的 9 个包均为：

```text
10.68.209.149.59354 > 114.94.188.196.50015: [udp sum ok] UDP, length 148
```

包时间（UTC+08:00）：

```text
2026-11-25 15:25:20.221624
2026-11-25 15:25:25.292255
2026-11-25 15:25:30.500066
2026-11-25 15:25:35.809989
2026-11-25 15:25:41.085458
2026-11-25 15:25:46.268475
2026-11-25 15:25:51.463433
2026-11-25 15:25:56.626553
2026-11-25 15:26:01.956501
```

```text
9 packets captured
3998 packets received by filter
0 packets dropped by kernel
```

对应 IPv4 总长度 176、TTL 64、fragment offset 0、flags `[none]`。没有匹配的返回包。对比 T3，结果没有改善。

## T6：直接运行官方命令，MTU 1280

发生于 T5 之后；没有独立保存起止时间。本轮未运行自定义复测脚本，也没有抓包。以下来自实际命令返回；终端颜色控制符已移除。

启动：

```text
[#] wireguard-go utun
[+] Interface for HKU-SH-Lab is utun7
[#] wg addconf utun7 /dev/fd/63
[#] ifconfig utun7 inet 10.200.0.5/24 10.200.0.5 alias
[#] ifconfig utun7 mtu 1280
[#] ifconfig utun7 up
[#] route -q -n add -inet 10.200.0.0/24 -interface utun7
[#] route -q -n add -inet 10.128.13.0/24 -interface utun7
[+] Backgrounding route monitor
```

接口和路由：

```text
utun7: flags=8051<UP,POINTOPOINT,RUNNING,MULTICAST> mtu 1280
    inet 10.200.0.5 --> 10.200.0.5 netmask 0xffffff00

route to: 114.94.188.196
gateway: 10.71.128.1
interface: en0

route to: 10.128.13.133
interface: utun7
mtu: 1280
```

最初一次 `wg show`：

```text
transfer: 0 B received, 1.01 KiB sent
```

四个原生 `nc -G 10 -w 3 -vz <IP> 22` 的结果（先测试 .133，随后并行测试另外三台）：

```text
nc: connectx to 10.128.13.133 port 22 (tcp) failed: Operation timed out
nc: connectx to 10.128.13.130 port 22 (tcp) failed: Operation timed out
nc: connectx to 10.128.13.131 port 22 (tcp) failed: Operation timed out
nc: connectx to 10.128.13.132 port 22 (tcp) failed: Operation timed out
```

关闭前最终 `wg show utun7`：

```text
interface: utun7
  public key: 7qUSYM2GQ4+kFPGXhza1dAAvSGiFtWjE6/oncgG4uhY=
  private key: (hidden)
  listening port: 55455

peer: 6C6IP2TPYqsQSYeJD4aMKihY0+8crOCGjbqFQLGeilE=
  endpoint: 114.94.188.196:50015
  allowed ips: 10.200.0.0/24, 10.128.13.0/24
  transfer: 0 B received, 2.31 KiB sent
  persistent keepalive: every 25 seconds
```

没有 `latest handshake` 字段，系统代理 HTTP/HTTPS/SOCKS 均保持开启。随后执行 `wg-quick down` 成功，内网目标路由回到默认网关 `10.71.128.1`。

本轮出口网关与 T0–T5 不同，因此它不是只改变 MTU 的严格单变量实验。未记录当时的出口公网 IP、SSID、运营商或准确地理位置。
