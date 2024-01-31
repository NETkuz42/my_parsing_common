import ssl
import socks
from imaplib import IMAP4
import pandas as pd


class SocksIMAP4(IMAP4):
    """
    IMAP service trough SOCKS proxy. PySocks module required.
    """

    PROXY_TYPES = {"socks4": socks.PROXY_TYPE_SOCKS4,
                   "socks5": socks.PROXY_TYPE_SOCKS5,
                   "http": socks.PROXY_TYPE_HTTP}

    def __init__(self, host, port=144, proxy_addr=None, proxy_port=None,
                 rdns=True, username=None, password=None, proxy_type="http", timeout=None):
        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port
        self.rdns = rdns
        self.username = username
        self.password = password
        self.proxy_type = SocksIMAP4.PROXY_TYPES[proxy_type.lower()]

        IMAP4.__init__(self, host, port, timeout)

    def _create_socket(self, timeout=None):
        return socks.create_connection((self.host, self.port), proxy_type=self.proxy_type, proxy_addr=self.proxy_addr,
                                       proxy_port=self.proxy_port, proxy_rdns=self.rdns, proxy_username=self.username,
                                       proxy_password=self.password, timeout=timeout)


class SocksIMAP4SSL(SocksIMAP4):

    def __init__(self, host='', port=993, keyfile=None, certfile=None, ssl_context=None, proxy_addr=None,
                 proxy_port=None, rdns=True, username=None, password=None, proxy_type="http", timeout=None):

        if ssl_context is not None and keyfile is not None:
            raise ValueError("ssl_context and keyfile arguments are mutually "
                             "exclusive")
        if ssl_context is not None and certfile is not None:
            raise ValueError("ssl_context and certfile arguments are mutually "
                             "exclusive")

        self.keyfile = keyfile
        self.certfile = certfile
        if ssl_context is None:
            ssl_context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
        self.ssl_context = ssl_context

        SocksIMAP4.__init__(self, host, port, proxy_addr=proxy_addr, proxy_port=proxy_port,
                            rdns=rdns, username=username, password=password, proxy_type=proxy_type, timeout=timeout)

    def _create_socket(self, timeout=None):
        sock = SocksIMAP4._create_socket(self, timeout=timeout)
        server_hostname = self.host if ssl.HAS_SNI else None
        return self.ssl_context.wrap_socket(sock, server_hostname=server_hostname)

    # Looks like newer versions of Python changed open() method in IMAP4 lib.
    # Adding timeout as additional parameter should resolve issues mentioned in comments.
    # Check https://github.com/python/cpython/blob/main/Lib/imaplib.py#L202 for more details.
    def open(self, host='', port=143, timeout=None):
        SocksIMAP4.open(self, host, port, timeout)


class ProxyList:
    def __init__(self):
        self.path_to_proxy_file = r"C:\PYTHON\for_oleg\settings\proxies.csv"
        self.proxy_frame = self._get_proxy_frame()
        pass

    def _get_proxy_frame(self):
        proxy_frame = pd.read_csv(self.path_to_proxy_file, sep=";", encoding="UTF-8", dtype=object)
        return proxy_frame

    def get_my_proxy(self, email):
        old_proxy = self.proxy_frame[self.proxy_frame["last_account"] == email]
        if len(old_proxy) > 0:
            return old_proxy.iloc[0]

        free_proxy = self.proxy_frame[self.proxy_frame["last_account"].isna()]
        if len(free_proxy) > 0:
            result_proxy_series = free_proxy.iloc[0]
            index_proxy = result_proxy_series.name
            self.proxy_frame.loc[index_proxy, "last_account"] = email
            self.proxy_frame.to_csv(self.path_to_proxy_file, sep=";", index=False, encoding="UTF-8")
            return result_proxy_series

        else:
            raise "нет свободных проксей"


if __name__ == "__main__":
    pass
