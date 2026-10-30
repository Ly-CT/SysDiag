# ===== src/sysdiag/modules/__init__.py =====
from . import disk_check, dns_check, port_check, system_info
# Clave de CLI -> módulo. Network, Services y Printer se agregarán aquí.
MODULES = {
    "system": system_info,
    "disk": disk_check,
    "dns": dns_check,
    "ports": port_check,
}
