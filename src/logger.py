import logging
from config import config

log_config = config['logging']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt=f"[{log_config['tag_style']}] [{log_config['date_style']}]")
