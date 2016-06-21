#!/usr/bin/python

from OpenSSL import crypto
from os.path import exists, join
from socket import gethostname
CERT_FILE = "ssl_DSePHR.crt"
KEY_FILE = "ssl_DSePHR.key"


def create_self_signed_cert(cert_dir):
    """
    If datacard.crt and datacard.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    """

    if not exists(join(cert_dir, CERT_FILE)) \
            or not exists(join(cert_dir, KEY_FILE)):

        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "TH"
        cert.get_subject().ST = "Songkhla"
        cert.get_subject().L = "Hatyai"
        cert.get_subject().O = "PSU"
        cert.get_subject().OU = "LAB"
        cert.get_subject().CN = gethostname()
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')

        open(join(cert_dir, CERT_FILE), "wt").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(join(cert_dir, KEY_FILE), "wt").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    return (join(cert_dir, CERT_FILE),join(cert_dir, KEY_FILE))