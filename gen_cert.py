import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import ipaddress


def generate_self_signed_cert():
    print("正在生成 10 年期自签证书...")

    # 生成私钥
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 证书信息
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Guangdong"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Shenzhen"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Internal"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])

    # 证书主体（包含 localhost 和局域网 IP 支持）
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow() - datetime.timedelta(days=1)  # 提前一天生效防时区问题
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=3650)  # 10 年有效期
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"localhost"),
            x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
            # 如果你需要局域网 IP 访问，可以把下面的 IP 换成你电脑的局域网 IP
            # x509.IPAddress(ipaddress.IPv4Address(u"192.168.1.100")),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # 保存私钥 key.pem
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 保存证书 cert.pem
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("✅ 证书生成成功！当前目录下已生成 cert.pem 和 key.pem")


if __name__ == "__main__":
    generate_self_signed_cert()