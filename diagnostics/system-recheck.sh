#!/bin/bash
set -e
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
export LOG_LEVEL=verbose
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
base=/tmp/wg-recheck
conf="${1:?Pass the absolute path to the existing local WireGuard configuration}"
mkdir -p "$base"
exec > "$base/result.log" 2>&1
printf '=== Official WireGuard system-tunnel recheck ===\n'
date -u
wg --version
wireguard-go --version
capture_pid=''
inner_pid=''
started=0
cleanup() {
 set +e
 if [ "$started" = 1 ]; then /opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick down "$conf"; fi
 if [ -n "$inner_pid" ]; then kill -INT "$inner_pid"; wait "$inner_pid"; fi
 if [ -n "$capture_pid" ]; then kill -INT "$capture_pid"; wait "$capture_pid"; fi
 printf '\n=== Cleanup completed ===\n'
 route -n get 10.128.13.133
 touch "$base/finished"
}
trap cleanup EXIT
/sbin/route -n get 114.94.188.196
/usr/sbin/tcpdump -ni en0 -l -tttt -vv 'host 114.94.188.196 and (udp port 50015 or icmp)' > "$base/public-udp.log" 2>&1 &
capture_pid=$!
/opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick up "$conf"
started=1
iface=$(cat /var/run/wireguard/HKU-SH-Lab.name)
printf '\n=== Interface address and applied configuration ===\n'
ifconfig "$iface"
wg show "$iface"
/sbin/route -n get 10.128.13.133
/sbin/route -n get 114.94.188.196
/usr/sbin/tcpdump -ni "$iface" -l -tttt 'tcp port 22 and net 10.128.13.0/24' > "$base/tunnel-ssh.log" 2>&1 &
inner_pid=$!
printf '\n=== SSH connection test ===\n'
/usr/bin/python3 - <<'PY'
import socket,time,concurrent.futures
hosts=['10.128.13.130','10.128.13.131','10.128.13.132','10.128.13.133']
def probe(host):
 start=time.monotonic()
 try:
  with socket.create_connection((host,22),timeout=45) as s:
   local=s.getsockname()
   s.settimeout(5)
   banner=s.recv(256).decode(errors='replace').strip()
   return f'{host}:22 CONNECTED after {time.monotonic()-start:.3f}s; local={local}; banner={banner!r}'
 except Exception as e:
  return f'{host}:22 FAILED after {time.monotonic()-start:.3f}s; {type(e).__name__}: {e}'
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(probe,hosts): print(result,flush=True)
PY
printf '\n=== Final handshake and transfer status ===\n'
wg show "$iface"
printf '\n=== System proxy status ===\n'
scutil --proxy
