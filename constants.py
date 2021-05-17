"""
store all constants for lambda
"""
import os

ENV = os.getenv('ENVIRONMENT', 'production')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

WEBHOOK = os.getenv('WEBHOOK', None)
NOT_FOUND_URL = os.getenv('NOT_FOUND_URL', "https://bitespeed.co")

MAX_RETRY = 5
MAX_URL_LENGTH = 10
