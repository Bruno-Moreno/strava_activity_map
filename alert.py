from dotenv import load_dotenv

from src.training_log.alert_check import check_and_alert


if __name__ == "__main__":
    load_dotenv()
    check_and_alert()
