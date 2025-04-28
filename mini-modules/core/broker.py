import socket

def resolve_broker(mdns_name):
    try:
        return socket.gethostbyname(mdns_name)
    except Exception:
        fallback_ip = "192.168.1.100"
        print("Using fallback IP:", fallback_ip)
        return fallback_ip
