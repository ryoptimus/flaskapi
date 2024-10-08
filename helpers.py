# helpers.py

from flask import current_app
from pydantic import BaseModel
from typing import List
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

# PROMPT_AI helper: data model for project idea generation
class ProjectIdea(BaseModel):
    project_title: str
    description: str
    languages: List[str]
    steps: List[str]
    scale_up_ideas: List[str]

# PROMPT_AI helper: parse inputs lists to engineer prompt
# Prompt example:
#   I am a role[0] and role[1] using technology[0] and technology[1] 
#   and technology[2] in the industries[0] industry. Generate a project idea.
def engineer_brainstorm_prompt(roles, technologies, industries) -> str:
  prompt = (
    "I am a " + conjunct_me([role.lower() for role in roles]) +
    " using " + conjunct_me(technologies) +
    f" in the {industries[0].lower()} industry. Generate a project idea. " 
    "Include which languages/technologies are used, clear steps for achieving "
    "project completion, and ideas for scaling it up."
  )
  return prompt

# PROMPT_AI helper: conjoin list of things using commas and/or 'and'
def conjunct_me(list):
  if len(list) > 2:
    joined_string = ", ".join(list[:-1]) + ", and " + list[-1]
    return joined_string
  elif len(list) == 2:
    joined_string = " and ".join(list)
    return joined_string
  else:
    return list[0]
  
# PROMPT_AI_TO_GENERATE_TASKS helper: data model for task generation
# class Tasks(BaseModel):
  # tasks: List[List[str]]
  
# Task generation helper
def engineer_taskgen_prompt(title, summary, languages, steps):
  prompt = f"""
  I will provide you with a project title, a brief summary, my languages/technologies preferences, and a list of steps necessary for project completion. You must provide a list of tasks needed for each step. 

  Project Title: {title}
  Summary: {summary}
  Languages/Technologies: {conjunct_me(languages)}
  Steps: """
  for step in steps:
    prompt += f"\n\t{step}"
  return prompt + "\n"

# LOGIN and REGISTER helpers: hash and verify passwords using bcrypt
def hash_password(password: str, bcrypt):
    # Utilize bcrypt with an automatically generated salt
    return bcrypt.generate_password_hash(password)
  
def verify_password(plain_password, hashed_password, bcrypt) -> bool:
    # Verify the hashed password
    return bcrypt.check_password_hash(hashed_password, plain_password)
  
def generate_confirmation_token(email):
  serializer = URLSafeTimedSerializer(current_app.config['ITSDANGEROUS_SECRET_KEY'])
  return serializer.dumps(email, salt=current_app.config['ITSDANGEROUS_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
  serializer = URLSafeTimedSerializer(current_app.config['ITSDANGEROUS_SECRET_KEY'])
  try:
    email = serializer.loads(
      token,
      salt=current_app.config['ITSDANGEROUS_PASSWORD_SALT'],
      max_age=expiration
    )
  except:
    return False
  return email

def send_email(to, subject, template):
  mail = current_app.extensions['mail']
  message = Message(
    subject,
    recipients=[to],
    html=template,
    sender=current_app.config['MAIL_DEFAULT_SENDER']
  )
  mail.send(message)