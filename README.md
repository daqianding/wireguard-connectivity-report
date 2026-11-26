# WireGuard 连接排障报告（2026-11-25–26）

这份记录用于让实验室网管核对：macOS 客户端 `10.200.0.5` 通过公网 UDP `114.94.188.196:50015` 访问实验室服务器时，一直无法完成 WireGuard 握手。

**最新结果：代理路径可实际登录和传输数据，直连仍失败。** 11 月 26 日使用 `daqianding` 和已有 SSH 密钥成功登录 `10.128.13.133`，服务器观察到的隧道来源为 `10.200.0.5`；通过 SSH 各上传、下载 1 MiB 测试数据均成功。当天直连再次抓到 10 个 148 字节外发 UDP 包，零回包；随后代理握手响应约 445 ms。11 月 25 日还已确认四台服务器的 SSH 服务可达。

成功路径需要明确把 WireGuard UDP 送入 Clash SOCKS5；仅开启系统代理不会自动代理原生 WireGuard。当前 AnyTLS 节点把 UDP 装入 TLS/TCP，改变了传输方式、路径和出口来源。不能因此断言具体丢包点或责任方。服务器账号无 sudo 权限，live peer、服务端抓包及路由器 ACL 仍需网管核实。

共整理 T0–T6 和 E1–E12 共 19 个阶段（包含未建隧道基线），另附 DNS UDP、时间、路由追踪和网络过滤检查。对原始文件被覆盖、日志遗漏及一次执行错误均作明确说明。最新证据见[报告第 11 节](REPORT.zh-CN.md#11-2026-11-26-复核实际登录数据传输与服务器只读检查)。

- [可复现的代理连接方法](WORKAROUND.zh-CN.md)：使用官方 WireGuard 与一个只转发加密 UDP 的本地中转。
- [完整中文报告](REPORT.zh-CN.md)：环境、全部尝试、逐轮结果、证据边界、原因分析及网管检查步骤。
- [证据来源说明](evidence/README.md)：区分留存文件、对话中保存的输出、事后环境快照。
- [早期及最终测试输出摘录](evidence/transcript-excerpts.md)：其中部分原始文件被重复运行覆盖，不能视为原始日志文件。
- [留存的详细握手日志](evidence/T5-system-mtu1380-proxy-on/result.log)、[公网 UDP 抓包文本](evidence/T5-system-mtu1380-proxy-on/public-udp.log)、[隧道内 SSH 抓包文本](evidence/T5-system-mtu1380-proxy-on/tunnel-ssh.log)。
- [脱敏客户端配置](config/HKU-SH-Lab.redacted.conf)：私钥已移除，不能直接用于连接。

公开材料不包含 WireGuard 私钥、sudo 密码、代理订阅或账号凭据；保留与此次排障直接相关的网络地址、端口及公钥，供网管关联检查。没有上传原始聊天截图或实验室配置文档的分享链接。
