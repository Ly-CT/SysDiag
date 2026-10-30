# ===== tests/test_port_check.py =====
import socket

from sysdiag.models import Config, Status
from sysdiag.modules import port_check


def test_open_port():
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        cfg = Config(port_targets=[("127.0.0.1", port)], timeout_s=1)
        assert port_check.run(cfg)[0].status is Status.OK


def test_closed_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    cfg = Config(port_targets=[("127.0.0.1", port)], timeout_s=1)
    assert port_check.run(cfg)[0].status is Status.FAIL