import socket
from app.logging_config import logger

# En yaygın ve anlamlı portlar (istersen sonra genişletiriz)
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Alt",
}


def scan_port(ip_address: str, port: int, timeout: float = 0.5) -> bool:
    """
    Belirtilen IP ve portta bağlantı kurulabiliyor mu diye kontrol eder.
    True = port açık, False = port kapalı/erişilemez.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip_address, port))
        return result == 0
    except socket.error:
        return False
    finally:
        sock.close()


def scan_common_ports(ip_address: str) -> list[dict]:
    logger.info(f"Port taramasi baslatildi: {ip_address}")
    open_ports = []
    for port, service_name in COMMON_PORTS.items():
        is_open = scan_port(ip_address, port)
        if is_open:
            open_ports.append({"port": port, "service": service_name})
    logger.info(f"Port taramasi tamamlandi: {ip_address} - {len(open_ports)} acik port bulundu")
    return open_ports