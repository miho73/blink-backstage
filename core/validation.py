import re


def length_check(value, min, max):
  if len(value) < min or len(value) > max:
    return False
  return True

def length_check_min(value, min):
  if len(value) < min:
    return False
  return True

def length_check_max(value, max):
  if len(value) > max:
    return False
  return True

def regex_check(value, expression):
  if re.match(expression, value) is None:
    return False
  return True

def assert_value(value, expected):
  if value != expected:
    return False
  return True

def validate_all(
  *conditions
):
  for condition in conditions:
    if not condition:
      return True
  return False
