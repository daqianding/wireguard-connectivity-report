# WireGuard 连接排障报告（2026-11-25）

这份记录用于让实验室网管核对：macOS 客户端 `10.200.0.5` 通过公网 UDP `114.94.188.196:50015` 访问实验室服务器时，一直无法完成 WireGuard 握手。

**最新结果：已找到可用的代理 UDP 路径。** 官方 WireGuard 命令行客户端经 Clash 的 SOCKS5 UDP 两次成功握手，最终完整读取四台服务器的 SSH banner 和 Ed25519 主机公钥；直连实验仍失败。密钥和实验室入口在成功窗口可用，当前更应排查直连路径及来源策略。未进行用户账号登录认证。

共整理 T0–T6 和 E1–E9 共 16 个阶段（包含未建隧道基线），另附 DNS UDP、时间、路由追踪和网络过滤检查。对原始文件被覆盖、日志遗漏及一次执行错误均作明确说明。

- [可复现的代理连接方法](WORKAROUND.zh-CN.md)：使用官方 WireGuard 与一个只转发加密 UDP 的本地中转。
- [完整中文报告](REPORT.zh-CN.md)：环境、全部尝试、逐轮结果、证据边界、原因分析及网管检查步骤。
- [证据来源说明](evidence/README.md)：区分留存文件、对话中保存的输出、事后环境快照。
- [早期及最终测试输出摘录](evidence/transcript-excerpts.md)：其中部分原始文件被重复运行覆盖，不能视为原始日志文件。
- [留存的详细握手日志](evidence/T5-system-mtu1380-proxy-on/result.log)、[公网 UDP 抓包文本](evidence/T5-system-mtu1380-proxy-on/public-udp.log)、[隧道内 SSH 抓包文本](evidence/T5-system-mtu1380-proxy-on/tunnel-ssh.log)。
- [脱敏客户端配置](config/HKU-SH-Lab.redacted.conf)：私钥已移除，不能直接用于连接。

公开材料不包含 WireGuard 私钥、sudo 密码、代理订阅或账号凭据；保留与此次排障直接相关的网络地址、端口及公钥，供网管关联检查。没有上传原始聊天截图或实验室配置文档的分享链接。
