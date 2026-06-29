import logging
import os

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, company_name: str, verification_link: str) -> None:
    logger.info("=" * 60)
    logger.info(f"TO: {to_email}")
    logger.info(f"SUBJECT: Verify your company '{company_name}' on KnowMate")
    logger.info(f"BODY:")
    logger.info(f"  Hello,")
    logger.info(f"  Please verify your email to complete registration for {company_name}.")
    logger.info(f"  Click the link below:")
    logger.info(f"  {verification_link}")
    logger.info(f"  This link expires in 30 minutes.")
    logger.info("=" * 60)

    link_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "latest_verification_link.txt")
    try:
        with open(link_file, "w") as f:
            f.write(verification_link)
    except OSError:
        pass
