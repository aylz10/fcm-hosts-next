# FCM Hosts Next

这是一个自动化维护的 Google Firebase Cloud Messaging (FCM) 优选 Hosts 项目。通过分布式边缘探测架构，实时筛选针对中国大陆运营商环境优化的优质边缘节点。

## ⚙️ 自动化架构

本项目采用三段式流水线：

1. **数据采集 (Harvest)**：在 GitHub hosted runner 上运行 `scripts/harvest.py`，利用 EDNS Client Subnet (ECS) 模拟国内运营商网段，向 Google 权威 DNS 诱捕候选 IP。
2. **国内校验 (Sommelier)**：在中国大陆的 self-hosted runner 上运行 `scripts/sommelier.py`，对候选 IP 执行 TCP 5228 真机握手测速与二次扩扫。
3. **产物发布 (Publish)**：将生成的 `fcm_ipv4.hosts`、`fcm_ipv6.hosts`、`fcm_dual.hosts` 提交回仓库，由 GitHub Pages 对外分发。

当前生产 self-hosted runner 已迁移到京东云 BGP 机器，且 `verify` 阶段只依赖 workflow artifact，不再要求国内 runner 直接 `git checkout` 仓库或在线安装 Python 依赖。

## 📦 产物列表

本项目默认每 3 小时自动更新一次，产物通过 GitHub Pages 分发。

- [fcm_dual.hosts](fcm_dual.hosts): **推荐使用**。双栈负载均衡版本，具备最佳兼容性。
- [fcm_ipv6.hosts](fcm_ipv6.hosts): 纯 IPv6 版本，适用于拥有 IPv6 环境的移动端或教育网。
- [fcm_ipv4.hosts](fcm_ipv4.hosts): 纯 IPv4 版本，作为传统环境的补丁。

## 🛠️ 使用方式

数据源通过 `https://miceworld.top/fcm-hosts-next/fcm_dual.hosts` 分发。

- **系统层**：建议通过自动化脚本每 12-24 小时拉取一次内容并原子化覆盖 `/etc/hosts`。
- **代理层**：可在 Sing-box 或 Clash 配置中通过 `hosts` 模块直接引用下载路径。

## 🧭 维护说明

- `harvest` 跑在 GitHub hosted 环境，依赖 `requirements.txt` 中的 `dnspython`。
- `verify` 跑在大陆 self-hosted 环境，只依赖系统自带 `python3` 和 workflow artifact。
- workflow 已开启同分支并发收敛，避免 schedule / push / 手动触发相互堆积。

---

_Status: Automated / Real-time Verified_
