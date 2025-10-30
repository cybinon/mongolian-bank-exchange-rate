"""
Цуглуулагчийн тохиргооны модуль.
Бүх тохиргооны утгуудыг орчны хувьсагчдаас уншина.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class CrawlerConfig:
    """Цуглуулагчийн тохиргооны анги."""
    
    # Өгөгдлийн сангийн тохиргоо
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./exchange_rates.db")
    
    # Хуваарийн тохиргоо
    CRON_SCHEDULE: str = os.getenv("CRON_SCHEDULE", "0 1 * * *")
    
    # SSL тохиргоо
    SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "False").lower() in ('true', '1', 't', 'yes')
    
    # Хугацааны хязгаар (секундээр)
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    PLAYWRIGHT_TIMEOUT: int = int(os.getenv("PLAYWRIGHT_TIMEOUT", "60000"))  # миллисекунд
    
    # Банкуудын URI хаягууд
    KHANBANK_URI: str = os.getenv("KHANBANK_URI", "https://www.khanbank.com/api/back/rates")
    TDBM_URI: str = os.getenv("TDBM_URI", "https://www.tdbm.mn/en/exchange-rates")
    GOLOMT_URI: str = os.getenv("GOLOMT_URI", "https://www.golomtbank.com/api/exchange")
    XACBANK_URI: str = os.getenv("XACBANK_URI", "https://xacbank.mn/api/currencies")
    ARIGBANK_URI: str = os.getenv("ARIGBANK_URI", "https://www.arigbank.mn/en/rate")
    BOGDBANK_URI: str = os.getenv("BOGDBANK_URI", "https://www.bogdbank.com/exchange")
    STATEBANK_URI: str = os.getenv("STATEBANK_URI", "https://www.statebank.mn/back/api/fetchrate")
    MONGOLBANK_URI: str = os.getenv("MONGOLBANK_URI", "https://www.mongolbank.mn/en/currency-rate-movement/data")
    CAPITRONBANK_URI: str = os.getenv(
        "CAPITRONBANK_URI",
        "https://www.capitronbank.mn/admin/en/wp-json/bank/rates/capitronbank"
    )
    CKBANK_URI: str = os.getenv("CKBANK_URI", "https://www.ckbank.mn/currency-rates")
    TRANSBANK_URI: str = os.getenv("TRANSBANK_URI", "https://transbank.mn/en/exchange")
    NIBANK_URI: str = os.getenv("NIBANK_URI", "https://www.nibank.mn/en/rate")
    MBANK_URI: str = os.getenv("MBANK_URI", "https://m-bank.mn/")
    
    # Ариг банкны тусгай тохиргоо
    ARIGBANK_BEARER_TOKEN: Optional[str] = os.getenv("ARIGBANK_BEARER_TOKEN")
    ARIGBANK_API_URL: str = os.getenv(
        "ARIGBANK_API_URL",
        "https://www.arigbank.mn/exchange/getRate"
    )
    
    @classmethod
    def get_bank_uri(cls, bank_name: str) -> Optional[str]:
        """Банкны нэрээр URI хаяг авах."""
        uri_map = {
            "khanbank": cls.KHANBANK_URI,
            "tdbm": cls.TDBM_URI,
            "golomt": cls.GOLOMT_URI,
            "xacbank": cls.XACBANK_URI,
            "arigbank": cls.ARIGBANK_URI,
            "bogdbank": cls.BOGDBANK_URI,
            "statebank": cls.STATEBANK_URI,
            "mongolbank": cls.MONGOLBANK_URI,
            "capitronbank": cls.CAPITRONBANK_URI,
            "ckbank": cls.CKBANK_URI,
            "transbank": cls.TRANSBANK_URI,
            "nibank": cls.NIBANK_URI,
            "mbank": cls.MBANK_URI,
        }
        return uri_map.get(bank_name.lower())


# Create a singleton instance
config = CrawlerConfig()
