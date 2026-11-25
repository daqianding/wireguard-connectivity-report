import argparse, socket, struct, select, time, signal

def readn(s,n):
    data=b''
    while len(data)<n:
        block=s.recv(n-len(data))
        if not block: raise RuntimeError('SOCKS control connection closed')
        data+=block
    return data

def addr(s,atyp):
    if atyp==1: return socket.inet_ntoa(readn(s,4))
    if atyp==3: return readn(s,readn(s,1)[0]).decode()
    if atyp==4: return socket.inet_ntop(socket.AF_INET6,readn(s,16))
    raise RuntimeError('Unsupported SOCKS address type')

def associate():
    ctl=socket.create_connection(('127.0.0.1',7890),timeout=5)
    ctl.sendall(b'\x05\x01\x00')
    if readn(ctl,2)!=b'\x05\x00': raise RuntimeError('SOCKS no-auth negotiation rejected')
    ctl.sendall(b'\x05\x03\x00\x01'+b'\x00'*6)
    h=readn(ctl,4)
    if h[1]!=0: raise RuntimeError('SOCKS UDP ASSOCIATE rejected: '+str(h[1]))
    host=addr(ctl,h[3]);port=struct.unpack('!H',readn(ctl,2))[0]
    if host=='0.0.0.0':host='127.0.0.1'
    udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);udp.connect((host,port));udp.settimeout(5)
    print('SOCKS UDP ASSOCIATE OK; local relay='+host+':'+str(port),flush=True)
    return ctl,udp

def frame(payload,host,port):
    return b'\x00\x00\x00\x01'+socket.inet_aton(host)+struct.pack('!H',port)+payload

def unframe(data):
    if len(data)<4 or data[2]!=0:raise RuntimeError('Invalid or fragmented SOCKS UDP reply')
    typ=data[3]
    if typ==1: offset=8
    elif typ==4:offset=20
    elif typ==3:offset=5+data[4]
    else:raise RuntimeError('Invalid SOCKS UDP address type')
    return data[offset+2:]

def dnscheck(use_proxy):
    query=struct.pack('!HHHHHH',0x6137,0x0100,1,0,0,0)+b'\x07example\x03com\x00'+struct.pack('!HH',1,1)
    ctl=None
    if use_proxy:
        ctl,udp=associate();udp.send(frame(query,'1.1.1.1',53))
    else:
        udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);udp.settimeout(5);udp.connect(('1.1.1.1',53));udp.send(query)
    try:
        reply=udp.recv(65535)
        if use_proxy:reply=unframe(reply)
        qid,flags,qd,an,ns,ar=struct.unpack('!HHHHHH',reply[:12])
        print('UDP DNS control: proxy='+str(use_proxy)+'; transaction_matches='+str(qid==0x6137)+'; response='+str(bool(flags&0x8000))+'; rcode='+str(flags&15)+'; answers='+str(an),flush=True)
    finally:
        udp.close()
        if ctl:ctl.close()

p=argparse.ArgumentParser();p.add_argument('--check',choices=['direct','proxy']);p.add_argument('--listen',type=int,default=52999);p.add_argument('--direct',action='store_true');args=p.parse_args()
if args.check:
    dnscheck(args.check=='proxy')
else:
    ctl=None
    if args.direct:
        up=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);up.connect(('114.94.188.196',50015))
    else:
        ctl,up=associate()
    front=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);front.bind(('127.0.0.1',args.listen))
    print('Forwarding WireGuard encrypted UDP from 127.0.0.1:'+str(args.listen)+' to 114.94.188.196:50015; mode='+('direct' if args.direct else 'SOCKS'),flush=True)
    peer=None;sent=received=0
    try:
        while True:
            readable,_,_=select.select(([front,up,ctl] if ctl else [front,up]),[],[],1)
            for s in readable:
                if s is ctl:
                    if not ctl.recv(1):raise RuntimeError('SOCKS control connection closed')
                elif s is front:
                    data,peer=front.recvfrom(65535);up.send(data if args.direct else frame(data,'114.94.188.196',50015));sent+=1
                    print(time.strftime('%Y-%m-%d %H:%M:%S')+' local_to_upstream payload_bytes='+str(len(data)),flush=True)
                else:
                    raw=up.recv(65535);payload=raw if args.direct else unframe(raw);received+=1
                    print(time.strftime('%Y-%m-%d %H:%M:%S')+' upstream_to_local payload_bytes='+str(len(payload)),flush=True)
                    if peer:front.sendto(payload,peer)
    except KeyboardInterrupt:
        pass
    finally:
        print('Relay totals: sent_datagrams='+str(sent)+' received_datagrams='+str(received),flush=True)
        front.close();up.close()
        if ctl:ctl.close()
