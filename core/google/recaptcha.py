import logging

from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment, Event, CreateAssessmentRequest

from core.config import config

parent = "projects/blink-hs"
location = "us-central1"

log = logging.getLogger(__name__)


def verify_recaptcha(token: str, client_ip: str, action: str):
  client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

  log.debug("Assessing reCAPTCHA. token=\"{}\", client_ip=\"{}\", action=\"{}\"".format(token, client_ip, action))
  assessment = Assessment(
    event=Event(
      token=token,
      site_key=config['security']['recaptcha']['site_key'],
      user_ip_address=client_ip,
      expected_action=action
    )
  )

  request = CreateAssessmentRequest(
    assessment=assessment,
    parent=parent,
  )

  response = client.create_assessment(request)
  log.debug("reCAPTCHA assessment completed. token=\"{token}\"".format(token=token))

  if response.token_properties.valid and response.risk_analysis.score >= 0.6:
    log.debug("reCAPTCHA passed. token=\"{}\"".format(token))
    return True
  else:
    log.debug("reCAPTCHA was not passed(score). token=\"{token}\", score=\"{score}\"".format(token=token,
                                                                                             score=response.risk_analysis.score))
    return False
