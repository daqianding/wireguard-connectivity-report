"""One bounded TTL probe using a fresh, encrypted WireGuard initiation.
No keys are read. This diagnoses packet reach, not a working WG session.
Each probe gets a new source port so quoted ICMP can identify that probe.
"""
import socket, struct, select, time, json
TARGET = '114.94.188.196'
PORT = 50015
TTLS = [1, 3, 7, 12, 16, 17, 18, 19, 20, 21, 22, 24, 32, 64]
front = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
front.bind(('127.0.0.1', 52999))
front.settimeout(20)
icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
print('Waiting for one fresh WireGuard initiation on 127.0.0.1:52999', flush=True)
payload, client = front.recvfrom(65535)
assert len(payload) == 148 and payload[:4] == b'\x01\x00\x00\x00', 'Unexpected first datagram'
print(json.dumps({'payload_bytes': len(payload), 'type': 1, 'sender_index': struct.unpack('<I', payload[4:8])[0], 'probes': len(TTLS)}), flush=True)
for ttl in TTLS:
    up = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    up.bind(('0.0.0.0', 0))
    local_port = up.getsockname()[1]
    up.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    started = time.monotonic()
    up.sendto(payload, (TARGET, PORT))
    result = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'ttl': ttl, 'source_port': local_port, 'result': 'timeout'}
    deadline = started + 1.5
    while time.monotonic() < deadline:
        ready, _, _ = select.select([icmp, up], [], [], max(0, deadline-time.monotonic()))
        if not ready:
            break
        if up in ready:
            try:
                reply, source = up.recvfrom(65535)
                if source != (TARGET, PORT):
                    continue
                result.update(result='udp_reply', bytes=len(reply), message_type=struct.unpack('<I', reply[:4])[0] if len(reply)>=4 else None, ms=round((time.monotonic()-started)*1000,3))
                break
            except OSError as e:
                result.update(result='socket_error', error=str(e))
                break
        if icmp in ready:
            packet, router = icmp.recvfrom(65535)
            ihl = (packet[0] & 15)*4
            if len(packet) < ihl+8+20 or packet[ihl] not in (3,11):
                continue
            inner = packet[ihl+8:]
            inner_hl = (inner[0]&15)*4
            if len(inner) < inner_hl+8 or inner[9] != 17 or socket.inet_ntoa(inner[16:20]) != TARGET:
                continue
            sport, dport = struct.unpack('!HH', inner[inner_hl:inner_hl+4])
            if sport != local_port or dport != PORT:
                continue
            result.update(result='icmp_reply', router=router[0], icmp_type=packet[ihl], icmp_code=packet[ihl+1], ms=round((time.monotonic()-started)*1000,3))
            break
    print(json.dumps(result), flush=True)
    up.close()
icmp.close()
front.close()
print('Finished; no WireGuard session authentication was attempted by this probe.', flush=True)
