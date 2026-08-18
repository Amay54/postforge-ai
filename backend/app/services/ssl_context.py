import os
import ssl
import subprocess
import certifi
import cryptography.x509
from cryptography.hazmat.primitives import serialization

_cached_bundle_path = None
_cached_ssl_context = None

def get_consolidated_ca_bundle() -> str:
    """
    Creates a secure, consolidated CA bundle combining certifi's public root CAs
    with Windows System Root Store certificates (including local enterprise/scanner roots).
    """
    global _cached_bundle_path
    if _cached_bundle_path and os.path.exists(_cached_bundle_path):
        return _cached_bundle_path

    bundle_dir = os.path.dirname(certifi.where())
    bundle_file = os.path.join(bundle_dir, "postforge_cacert.pem")
    
    certifi_content = open(certifi.where(), "r", encoding="utf-8").read()
    
    # Read Windows root certificates if on Windows
    valid_pems = []
    if os.name == "nt":
        try:
            ps_script = '$certs = Get-ChildItem -Path Cert:\\LocalMachine\\Root, Cert:\\CurrentUser\\Root | Where-Object { $_.RawData -ne $null }; foreach ($c in $certs) { [System.Convert]::ToBase64String($c.RawData) }'
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                for line in res.stdout.strip().split("\n"):
                    line_str = line.strip()
                    if line_str:
                        try:
                            import base64
                            der_bytes = base64.b64decode(line_str)
                            x509_obj = cryptography.x509.load_der_x509_certificate(der_bytes)
                            pem_bytes = x509_obj.public_bytes(serialization.Encoding.PEM)
                            valid_pems.append(pem_bytes.decode("utf-8"))
                        except Exception:
                            pass
        except Exception:
            pass

    try:
        with open(bundle_file, "w", encoding="utf-8") as f:
            f.write(certifi_content)
            if valid_pems:
                f.write("\n\n# === Windows System & Security Root Certificates ===\n")
                for pem in valid_pems:
                    f.write(pem.strip() + "\n\n")
        _cached_bundle_path = bundle_file
        return bundle_file
    except Exception:
        return certifi.where()

def get_secure_ssl_context() -> ssl.SSLContext:
    """
    Returns a strict, verified SSLContext with CERT_REQUIRED and hostname checking enabled.
    """
    global _cached_ssl_context
    if _cached_ssl_context:
        return _cached_ssl_context

    ca_path = get_consolidated_ca_bundle()
    ctx = ssl.create_default_context(cafile=ca_path)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = True
    
    if hasattr(ssl, "VERIFY_X509_STRICT"):
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        
    _cached_ssl_context = ctx
    return ctx
