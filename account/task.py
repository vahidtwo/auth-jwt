import logging

from settings.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="send_otp_verification", autoregister=True)
def send_otp_verification(otp):
    logger.info("-"*10)
    logger.info(f"|otp is {otp:-^30}|")
    logger.info("-"*10)


@celery_app.task(name="send_url_verification", autoregister=True)
def send_url_verification(url):
    logger.info("-"*10)
    logger.info(f"|url verification is {url:-^30}|")
    logger.info("-"*10)
