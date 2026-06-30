import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Exporter:
    @staticmethod
    def export_csv(data, filename):
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Successfully exported to CSV: {filename}")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")

    @staticmethod
    def export_excel(data, filename):
        try:
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            logger.info(f"Successfully exported to Excel: {filename}")
        except Exception as e:
            logger.error(f"Failed to export Excel: {e}")
