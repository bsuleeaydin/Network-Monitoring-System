from unittest.mock import patch
from app.services.ping_service import check_device_status


def test_check_device_status_online():
    # ping3.ping fonksiyonunu sahte bir cevapla değiştiriyoruz (0.05 saniye = başarılı ping)
    with patch("app.services.ping_service.ping", return_value=0.05):
        result = check_device_status("192.168.1.1")
        assert result["status"] == "online"
        assert result["response_time_ms"] == 50.0


def test_check_device_status_offline():
    # ping fonksiyonu None dönerse (cevap yok) offline olmalı
    with patch("app.services.ping_service.ping", return_value=None):
        result = check_device_status("10.255.255.1")
        assert result["status"] == "offline"
        assert result["response_time_ms"] is None