# 证据来源与保存限制

初始和 `expanded/` 日期为 2026-11-25，`followup-20261126/` 为次日复核；除显式标为 UTC 的行外，本文时间均按 Asia/Hong_Kong（UTC+08:00）。

| 文件 | 来源 | 可支持的结论 / 限制 |
|---|---|---|
| `T2-system-mtu1380/result.log` | 从首次系统隧道测试的留存日志复制 | 启动成功、地址/MTU/路由、四台 SSH 超时、握手与流量计数、系统代理开启；日志未打印精确起始时间 |
| `T5-system-mtu1380-proxy-on/result.log` | 从 15:50:31–15:51:16 的留存日志复制 | 官方 wireguard-go verbose 日志和完整测试输出 |
| `T5-system-mtu1380-proxy-on/public-udp.log` | 同一轮在 en0 上的 tcpdump 文本输出 | 9 个外发 UDP 包、源/目的地址和端口、长度、时间；不是 PCAP，没有完整包字节 |
| `T5-system-mtu1380-proxy-on/tunnel-ssh.log` | 同一轮在 utun7 上的 tcpdump 文本输出 | 40 个发往四台服务器的 TCP SYN / 重传；源地址为 10.200.0.5 |
| `transcript-excerpts.md` | 从本次对话中已经返回的工具输出逐项整理 | T0、T1、T3、T4、T6 的可用证据；明确为摘录，不冒充完整原始文件 |
| `report-time-environment.txt` | 编写报告时重新读取本机环境 | 仅证明快照时的 OS、版本、地址、路由、系统代理状态，不能倒推到早期每一轮 |

## 为什么部分轮次只有输出摘录

详细复测脚本多次使用相同输出路径，并用 `>` 覆盖写入。T3（15:22）和 T4（15:25）的原始文件后来被覆盖，当前该目录保存的是 T5（15:50）。这些早期轮次的结果和抓包内容曾完整或部分显示在工具返回中，因此可以引用相应输出，但没有独立的原始文件或 PCAP 可供复核。

T6 按用户要求直接执行官方命令，没有运行自定义复测脚本，也没有抓包；状态输出和端口探测结果保存在对话工具记录中。不能把 T5 的 `9 packets captured` 标成 T6 的结果。

## 脱敏方式

留存日志内容中的本机用户目录替换为 `$HOME`，临时复测路径统一为 `/tmp/wg-recheck`。其余诊断文本（包括无害的退出提示）保留。命令输出本来已将私钥显示为 `(hidden)`。没有生成文件哈希、完整聊天导出或任何凭据附件。

`diagnostics/system-recheck.sh` 是历史复测脚本的可读参考版本：把配置路径改成必填参数，把日志目录改为 `/tmp/wg-recheck` 并添加目录创建。它不是新的测试结果，也没有在公开版本上再运行一轮。日常复测优先使用报告里的官方命令。

## 扩展实验 E1–E9

`expanded/` 保存逐轮独立日志、实际配置状态、公网或回环抓包文本、UDP 中转计数、SSH 探测结果，以及只读防火墙检查。`observed-results.json` 仅汇总日志中实际观察字段，不是完整性清单。

E6/E9 是成功代理实验；E7 是相同中转程序直接发 UDP 的失败对照；E8 是修复本机执行错误后较新源码的失败直连复核。详情及执行问题见报告 7.7 节。

`E6-hostkeys.txt` 是第一次未完整结束的 keyscan 输出（四台 banner、两台公钥），`E9-hostkeys.txt` 才是完成后采集的四台完整结果。它们只有服务器公钥，不含用户认证私钥。

`egress-*.json` 为稍后 HTTP trace 的观测，不能当作服务端看见的实际 UDP NAT 源地址。`path-and-clock-notes.md` 为对话中的输出整理。公开材料保留 HTTP 出口地址用于排障，但未包含代理服务器连接配置或订阅。

## 次日 E10–E12

`followup-20261126/` 保留本轮独立输出，本机用户目录替换为 `$HOME`。本轮没有覆盖旧日志或将 daemon 与状态输出写入同一文件。

| 文件 | 内容 / 限制 |
|---|---|
| `local-environment.log`、`proxy-runtime.json` | 本机地址、路由、系统代理；只保留 Clash 链类型，移除节点名称及凭据 |
| `target-proxy-connections.json` | Clash 实际观察到的目标 UDP/Socks5 流；不含无关连接 |
| `server-readonly.log`、`server-network.log` | `.133` 真实 SSH 登录后的只读命令输出、sudo 拒绝；不含私钥或服务器配置文件内容 |
| `direct-up.log`、`direct-check.log`、`direct-status.log`、`direct-public.log`、`direct-down.log` | E11 官方客户端生命周期、路由、TCP 超时、抓包与 WG 状态；状态快照早于最终抓包截止 |
| `proxy-up.log`、`proxy-initial-status.log`、`proxy-first-down.log` | E10 生命周期及已握手状态 |
| `proxy-second-up.log`、`proxy-handshake.log`、`proxy-final-status.log`、`proxy-final-down.log` | E12 生命周期、前 6 个回环包和数据传输后状态；抓包达到 `-c 6` 自动结束 |
| `ssh-transfer.json` | 三个实际 SSH 子进程的返回码、输出或字节计数及单调时钟耗时；测试数据不落远端文件 |
| `proxy-relay.log` | E10/E12 共用中转进程记录的逐包长度及方向；含握手、SSH、保活，合计发 1563、收 1282 个数据报，不是单轮抓包计数 |
| `udp-dns-direct.log` | UDP DNS 正向对照；不证明目标 UDP 50015 可达 |
| `http-egress-*.json` | HTTP trace 的出口 IP/loc/colo；不能视为实验室所见 UDP 来源 |
| `cleanup.log`、`cleanup-interfaces.log` | 收尾后的代理与路由；后者为空文件是 `wg show interfaces` 无接口的实际输出；前者未发现相关测试进程 |

这批文件是文本输出及观测汇总，不是原始 PCAP。代理日志仅记录已加密数据报的长度和方向，没有记录 UDP 内容或 SSH 会话数据。账号名、UID、服务器接口和地址保留用于网管核对；没有上传本机 SSH 私钥、WireGuard 私钥、sudo 密码、代理订阅或节点连接配置。

## 进一步隔离 E13–E16

`isolation-20261126/` 保存后续 39 个证据文件。本机用户目录替换为 `$HOME`，无关本地网络隐私配置 UUID 替换为 `<local-id>`；没有上传整个 Network Extension 配置或系统设置截图。

- `mihomo-direct*` 和 `direct-via-mihomo-relay.log`：独立 Mihomo DIRECT 的配置、日志、API 连接记录、DNS 控制、9 包无回复及 WG 状态。原主实例未更改。
- `filter-configuration.json`：停用前筛选的 NE 配置字段；`cisco-off-*` 为总扩展停用的起止状态、保留的配置字段、进程检查、11 包无回复和 WG 状态；`cisco-restored-state.log` 确认恢复。配置记录的 Enabled 与扩展运行状态是不同层次，未混用。
- `apple-firewall.log`：系统防火墙只读状态和 WireGuard 入站许可，没有关闭防火墙。
- `restored-proxy-*`：Cisco 恢复后的代理握手、真实 SSH 登录、有限 systemd 状态和无权读取完整 journal 的提示。
- `trace-udp50015.log`：固定目的 UDP 50015 的普通 traceroute；40 B 普通探测内容，不是 WireGuard 请求。
- `wg-ttl-*-v1.*`：第一版实际握手 TTL 探测及代码；connected UDP 抢先返回 socket 错误，漏读相应 ICMP，不能用于判断“无路由”。未删除或覆盖这一轮记录。
- `wg-ttl-*`（无 v1）：修正后真实握手内容的 14 包探测、匹配的 6 个 ICMP 和官方客户端启动/关闭输出；可运行代码在 `diagnostics/wg-ttl-probe.py`。本工具仅检查包到达响应设备，不验证完整 WG 会话，重放及多路径限制见报告。
- `rdap-networks.json`：从 APNIC RDAP 取得的地址段名称/范围等公开字段，不含注册联系人。网页读取工具无法打开该 API，随后通过 HTTPS curl 成功读取 JSON；这属于地址注册资料，不是物理定位。
- `cleanup*`：没有残留测试进程/接口，Clash 系统代理保留。

Cisco 的临时停用已获用户单独明确同意。实际通过系统设置的扩展总开关完成，停用后进程退出、系统标记 disabled；恢复后界面为 on、进程重新出现、系统标记 enabled。网络页逐项状态下拉在自动化中未产生可验证变化，因此没有把那些点击计作有效停用。

## 逐台账号权限核对

`account-check-20261126/` 保存晚间重新连接后的逐台 SSH 输出、交互式 `.133` sudo 输出转录及临时隧道状态。`.130` 组成员包含 sudo，用户确认这是平时成功使用 sudo 的机器；`.133` 默认 sudo 仍拒绝。`.131/.132` 本次密钥认证失败，不能从中推断其 sudo 权限。传统 `sudo.ws` 未完成密码认证，权限未核实。以上不改变此前网络抓包结果，解决的是同名账号对应不同机器的权限歧义。
