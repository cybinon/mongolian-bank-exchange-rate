"""
Системийн бүртгэл (logging) тохиргооны модуль.
"""
import logging

def get_logger(name):
    """
    Нэртэй бүртгэгч (logger) үүсгэж буцаах.
    
    Args:
        name: Бүртгэгчийн нэр (ихэвчлэн модулийн нэр)
        
    Returns:
        Тохируулагдсан logger объект
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
