from fastapi import APIRouter
from .. import schemas, crud, models

from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated

from sqlalchemy.orm import Session
from dotenv import load_dotenv
# from . import crud, models, schemas
from ..database import SessionLocal, engine
from .authentication import get_current_user

router = APIRouter(tags=["payments"])

load_dotenv()
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import stripe
import os


# This is your test secret API key.
stripe.api_key = os.getenv('STRIPE_API_KEY')

YOUR_DOMAIN = os.getenv('FRONTEND_URL')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get('/create-checkout-session')
async def create_checkout_session( current_user: Annotated[schemas.UserResponse, Depends(get_current_user)]):
    
    print('checkout link hit')
    try:
        checkout_session = stripe.checkout.Session.create(


            line_items=[
                {
                    'price': os.getenv('STRIPE_PROD'),
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url= os.getenv('FRONTEND_URL') + '/editor',
            cancel_url= os.getenv('FRONTEND_URL'),
            customer_email= current_user.email
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={'checkout_session_url': checkout_session.url})






endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

@router.post('/webhook')
async def webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

# Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
            session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'], expand=['line_items'])

            print('This is session', session)
            if session['payment_status'] == 'paid' and session['amount_total'] == 1000:
                print('update the users credit')
                crud.add_subscription_credits(session['customer_email'], 1500, db)
            elif session['payment_status'] == 'paid' and session['amount_total'] == 52:
                print('update the users credit')
                crud.add_subscription_credits(session['customer_email'], 900, db)
                
  # Handle the checkout.session.completed event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'Invalid payload: {e}')
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f'Signature verification failed: {e}')
    # Handle the event here
    # handle_event(event)
    return {"status": "success"}


