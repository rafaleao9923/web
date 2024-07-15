import jwt
import os
import requests

from celery import shared_task
from django.core.mail import send_mail
from dotenv import load_dotenv
from rapidfuzz import fuzz
from subscription.models import Address

load_dotenv()

jwt_key = os.getenv("JWT_KEY")
jwt_algorithms = os.getenv("JWT_ALGORITHMS")
expected_client_producer = os.getenv("CLIENT_PRODUCER")
expected_service_producer = os.getenv("SERVICE_PRODUCER")
service_token = os.getenv("SERVICE_TOKEN")


def decode_token(token: str, caller_type: str) -> dict:
    try:
        decoded_token = jwt.decode(jwt=token,
                                   key=jwt_key,
                                   algorithms=jwt_algorithms)
    except jwt.exceptions.InvalidSignatureError:
        match caller_type:
            case 'client':
                return {"client_producer": "The producer sent an invalid token"}
            case 'service':
                return {"service_producer": "The producer sent an invalid token"}
    return decoded_token


@shared_task
def match_address_task(address):
    calling_producer = decode_token(address['client_token'], 'client')['client_producer']
    if calling_producer == expected_client_producer:
        response = requests.get('http://address-api:7000/api/v1/addresses/')
        addresses = [a_address['address'] for a_address in response.json()]

        top_score = 0
        min_score = 70
        match_address = address["address"]
        for base_address in addresses:
            score = round(fuzz.ratio(address["address"].lower(), str(base_address).lower()))
            if score >= top_score and score >= min_score:
                top_score = score
                match_address = base_address
            if top_score == 100:
                continue

        print(f'Match address: {match_address} > Score: {top_score}')

        address = {"name": address["name"],
                   "address": match_address,
                   "postalcode": address["postalcode"],
                   "city": address["city"],
                   "country": address["country"],
                   "email": address["email"]
                   }
        print(address)
        response = requests.post('http://address-api:7000/api/v1/addresses/', data=address)

        print(f"New address inserted for {address['name']}")

        send_email_task.delay(address["name"], address["address"], address["email"], service_token)
    else:
        print(f"Authentication failed (match_address_task): {calling_producer}")


@shared_task
def send_email_task(name, street, email, token):
    calling_producer = decode_token(token, 'service')['service_producer']
    if calling_producer == expected_service_producer:
        send_mail(
            "Your subscription",
            f"Dear {name},\n\nThanks for subscribing to our magazine!\n\nWe registered the subscription at this address:\n{street}.\n\nAnd you'll receive the latest edition of our magazine within three days.\n\nCM Publishers",
            "magazine@cm-publishers.com",
            [email],
            fail_silently=False,
        )
    else:
        print(f"Authentication failed (send_email_task): {calling_producer}")
