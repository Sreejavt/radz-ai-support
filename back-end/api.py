import json
import os
import uuid
import hashlib
import secrets
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv 
load_dotenv()
from pydantic import BaseModel
from typing import Optional
from search import search_question
from config import frontend_base_url
from email_service import send_email
from responses import welcome, goodbye, unknown
from datetime import datetime, date, timedelta
from fastapi import Request
from fastapi.responses import PlainTextResponse


app = FastAPI()

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "https://radz-ai-support.vercel.app"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
HELP_CENTRE_FILE = os.path.join(
    os.path.dirname(__file__),
    "help-center-documentation.json"
)

with open(HELP_CENTRE_FILE, "r", encoding="utf-8") as f:
    help_centre_docs = json.load(f)


def send_whatsapp_message(to, message_text):
    url = f"https://graph.facebook.com/v21.0/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("WHATSAPP SEND STATUS:", response.status_code)
    print("WHATSAPP SEND RESPONSE:", response.text)
    return response.json()


def create_ticket(customer_id, customer_name, issue):
    ticket_id = "TKT-" + str(uuid.uuid4())[:8].upper()

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "issue": issue,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }

    with open("tickets.json", "r") as file:
        data = json.load(file)

    data["tickets"].append(ticket)

    with open("tickets.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "ticket_created",
        f"Ticket {ticket_id} created: {issue}",
        date.today().isoformat()
    )

    return ticket


def get_ticket(ticket_id):
    with open("tickets.json", "r") as file:
        data = json.load(file)

    for ticket in data["tickets"]:
        if ticket["ticket_id"] == ticket_id:
            return ticket

    return None


def list_tickets(status=None):
    with open("tickets.json", "r") as file:
        data = json.load(file)

    tickets = data["tickets"]

    if status is not None:
        tickets = [t for t in tickets if t["status"].lower() == status.lower()]

    return sorted(tickets, key=lambda t: t["created_at"])


def update_ticket_status(customer_id, ticket_id, new_status):
    with open("tickets.json", "r") as file:
        data = json.load(file)

    for ticket in data["tickets"]:
        if ticket["ticket_id"] == ticket_id:
            ticket["status"] = new_status

            with open("tickets.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "ticket_status_changed",
                f"Ticket {ticket_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return ticket

    return None


def create_complaint(customer_id, customer_name, complaint):
    complaint_id= "CMP-" + str(uuid.uuid4())[:8].upper()

    complaint_record = {
        "customer_id": customer_id,
        "complaint_id": complaint_id,
        "customer_name": customer_name,
        "complaint": complaint,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }

    with open("complaints.json", "r") as file:
        data = json.load(file)
    data["complaints"].append(complaint_record)

    with open("complaints.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "complaint_created",
        f"Complaint {complaint_id} filed: {complaint}",
        date.today().isoformat()
    )

    return complaint_record


def get_complaint(complaint_id):
    with open("complaints.json", "r") as file:
        data = json.load(file)

    for complaint in data["complaints"]:
        if complaint["complaint_id"] == complaint_id:
            return complaint

    return None


def update_complaint_status(customer_id, complaint_id, new_status):
    with open("complaints.json", "r") as file:
        data = json.load(file)

    for complaint in data["complaints"]:
        if complaint["complaint_id"] == complaint_id:
            complaint["status"] = new_status

            with open("complaints.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "complaint_status_changed",
                f"Complaint {complaint_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return complaint

    return None


def create_escalation(customer_id, customer_name, issue, reason):
    escalation_id = "ESC-" + str(uuid.uuid4())[:8].upper()

    escalation_record = {
        "escalation_id": escalation_id,
        "customer_name": customer_name,
        "issue": issue,
        "reason": reason,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }

    with open("escalations.json", "r") as file:
        data = json.load(file)

    data["escalations"].append(escalation_record)

    with open("escalations.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "escalation_created",
        f"Escalation {escalation_id} raised: {reason}",
        date.today().isoformat()
    )

    return escalation_record


def get_escalation(escalation_id):
    with open("escalations.json", "r") as file:
        data = json.load(file)

    for escalation in data["escalations"]:
        if escalation["escalation_id"] == escalation_id:
            return escalation

    return None


def update_escalation_status(customer_id, escalation_id, new_status):
    with open("escalations.json", "r") as file:
        data = json.load(file)

    for escalation in data["escalations"]:
        if escalation["escalation_id"] == escalation_id:
            escalation["status"] = new_status

            with open("escalations.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "escalation_status_changed",
                f"Escalation {escalation_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return escalation

    return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_customer(name, email, phone, last_transaction, birthday, important_dates, details, password=None):
    with open("customers.json", "r") as file:
        data = json.load(file)

    next_number = len(data["customers"]) + 1
    customer_id = f"CUS-{next_number:06d}"

    status = determine_customer_status(last_transaction.isoformat())

    customer = {
        "customer_id": customer_id,
        "name": name,
        "email": email,
        "phone": phone,
        "status": status,
        "last_transaction": last_transaction.isoformat(),
        "birthday": birthday.isoformat(),
        "important_dates": important_dates,
        "details": details,
        "password": hash_password(password) if password else None
    }

    data["customers"].append(customer)

    with open("customers.json", "w") as file:
        json.dump(data, file, indent=2)

    today_str = datetime.now().date().isoformat()

    add_customer_history(
        customer_id,
        "customer_created",
        f"Customer account created: {name}",
        today_str
    )

    add_customer_history(
        customer_id,
        "email_added",
        f"Email recorded: {email}",
        today_str
    )

    add_customer_history(
        customer_id,
        "phone_added",
        f"Phone recorded: {phone}",
        today_str
    )

    add_customer_history(
        customer_id,
        "birthday_added",
        f"Birthday recorded: {birthday.isoformat()}",
        today_str
    )

    add_customer_history(
        customer_id,
        "status_set",
        f"Initial status set to {status}",
        today_str
    )

    add_customer_history(
        customer_id,
        "last_transaction_recorded",
        f"Last transaction date recorded: {last_transaction.isoformat()}",
        today_str
    )

    for important_date in important_dates:
        add_customer_history(
            customer_id,
            "important_date_added",
            f"{important_date.get('type', 'Important date')} added: {important_date.get('date')}",
            today_str
        )

    for detail in details:
        add_customer_history(
            customer_id,
            "detail_added",
            f"{detail.get('type', 'Detail')}: {detail.get('details')}",
            today_str
        )

    return customer

def find_customer(identifier):
    with open("customers.json", "r") as file:
        data = json.load(file)

    for customer in data["customers"]:
        if (
            customer["customer_id"].lower() == identifier.lower()
            or customer["email"].lower() == identifier.lower()
            or customer["phone"] == identifier
        ):
            return customer

    return None


def verify_customer_identity(customer_id, customer_name):
    if not customer_id or not customer_name:
        return None

    customer = find_customer(customer_id)

    if customer is None:
        return None

    if customer["name"].strip().lower() != customer_name.strip().lower():
        return None

    return customer


def generate_reset_token():
    return secrets.token_urlsafe(32)


def create_password_reset(customer_id):
    token = generate_reset_token()
    now = datetime.now()
    expires_at = now + timedelta(minutes=15)

    reset_record = {
        "token": token,
        "customer_id": customer_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "used": False
    }

    with open("password_resets.json", "r") as file:
        data = json.load(file)

    data["resets"].append(reset_record)

    with open("password_resets.json", "w") as file:
        json.dump(data, file, indent=2)

    return reset_record


def get_password_reset(token):
    with open("password_resets.json", "r") as file:
        data = json.load(file)

    for reset in data["resets"]:
        if reset["token"] == token:
            return reset

    return None


def mark_reset_used(token):
    with open("password_resets.json", "r") as file:
        data = json.load(file)

    for reset in data["resets"]:
        if reset["token"] == token:
            reset["used"] = True

            with open("password_resets.json", "w") as file:
                json.dump(data, file, indent=2)

            return reset

    return None


def reset_password(token, new_password):
    reset = get_password_reset(token)

    if reset is None:
        return {"error": "Invalid or unrecognized reset token."}

    if reset["used"]:
        return {"error": "This reset link has already been used."}

    expires_at = datetime.fromisoformat(reset["expires_at"])

    if datetime.now() > expires_at:
        return {"error": "This reset link has expired. Please request a new one."}

    with open("customers.json", "r") as file:
        data = json.load(file)

    customer_found = None

    for customer in data["customers"]:
        if customer["customer_id"] == reset["customer_id"]:
            customer["password"] = hash_password(new_password)
            customer_found = customer
            break

    if customer_found is None:
        return {"error": "Customer not found."}

    with open("customers.json", "w") as file:
        json.dump(data, file, indent=2)

    mark_reset_used(token)

    add_customer_history(
        reset["customer_id"],
        "password_reset_completed",
        "Password was reset successfully.",
        date.today().isoformat()
    )

    return {"success": True, "customer_id": reset["customer_id"]}


def update_customer_status(customer_id, new_status):
    with open("customers.json", "r") as file:
        data = json.load(file)

    for customer in data["customers"]:
        if customer["customer_id"] == customer_id:
            customer["status"] = new_status

            with open("customers.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "status_changed",
                f"Customer status changed to {new_status}",
                date.today().isoformat()
            )

            return customer

    return None
    

def create_transaction(customer_id, amount, details):
    with open("transactions.json", "r") as file:
        data = json.load(file)

    next_number = len(data["transactions"]) + 1
    order_id = f"ORD-{next_number:06d}"

    transaction = {
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "details": details,
        "transaction_date": date.today().isoformat(),
        "status": "Completed"
    }
    
    data["transactions"].append(transaction)

    with open("transactions.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "purchase",
        f"Order {order_id} for {amount}",
        transaction["transaction_date"]
    )

    return transaction


def get_transaction(order_id):
    with open("transactions.json", "r") as file:
        data = json.load(file)

    for transaction in data["transactions"]:
        if transaction["order_id"] == order_id:
            return transaction

    return None


def create_order_issue(customer_id, order_id, issue):
    order_record = {
        "order_id": order_id,
        "customer_id": customer_id,
        "issue": issue,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }

    with open("orders.json", "r") as file:
        data = json.load(file)

    data["orders"].append(order_record)

    with open("orders.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "order_issue_created",
        f"Issue reported for order {order_id}: {issue}",
        date.today().isoformat()
    )

    return order_record


def get_order(order_id):
    with open("orders.json", "r") as file:
        data = json.load(file)

    for order in data["orders"]:
        if order["order_id"] == order_id:
            return order

    return None


def update_order_status(customer_id, order_id, new_status):
    with open("orders.json", "r") as file:
        data = json.load(file)

    for order in data["orders"]:
        if order["order_id"] == order_id:
            order["status"] = new_status

            with open("orders.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "order_status_changed",
                f"Order {order_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return order

    return None


def create_refund(customer_id, order_id, reason, amount):
    transaction = get_transaction(order_id)

    # Check 1: Order ID must exist
    if transaction is None:
        return {
            "error": "Order ID not found."
        }

    # Check 2: Order must belong to this customer
    if transaction["customer_id"] != customer_id:
        return {
            "error": "This order does not belong to this customer."
        }

    # Check 3: Refund amount must exactly match the amount paid
    actual_amount = float(transaction["amount"])
    requested_amount = float(amount)

    if requested_amount != actual_amount:
        return {
            "error": "There is a mismatch in the refund amount."
        }

    # Check 4: Order must not already have a refund on file
    existing_refund = get_refund(order_id)

    if existing_refund is not None:
        return {
            "error": "This order has already been refunded."
        }
        
    # Only create the refund after ALL checks pass
    refund_record = {
        "customer_id": customer_id,
        "order_id": order_id,
        "reason": reason,
        "amount": requested_amount,
        "status": "Requested",
        "created_at": datetime.now().isoformat()
    }

    with open("refunds.json", "r") as file:
        data = json.load(file)

    data["refunds"].append(refund_record)

    with open("refunds.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "refund_requested",
        f"Refund requested for order {order_id}: {requested_amount} ({reason})",
        date.today().isoformat()
    )

    return refund_record

def get_refund(order_id):
    with open("refunds.json", "r") as file:
        data = json.load(file)

    for refund in data["refunds"]:
        if refund["order_id"] == order_id:
            return refund

    return None


def update_refund_status(customer_id, order_id, new_status):
    with open("refunds.json", "r") as file:
        data = json.load(file)

    for refund in data["refunds"]:
        if refund["order_id"] == order_id:
            refund["status"] = new_status

            with open("refunds.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "refund_status_changed",
                f"Refund for order {order_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return refund

    return None


def add_customer_history(customer_id, event_type, details, event_date):
    history_record = {
        "customer_id": customer_id,
        "event_type": event_type,
        "details": details,
        "event_date": event_date,
        "created_at": datetime.now().isoformat()
    }

    with open("customer_history.json", "r") as file:
        data = json.load(file)

    data["history"].append(history_record)

    with open("customer_history.json", "w") as file:
        json.dump(data, file, indent=2)

    return history_record


def has_history_entry(customer_id, event_type, event_date, details=None):
    with open("customer_history.json", "r") as file:
        data = json.load(file)

    for record in data["history"]:
        if (
            record["customer_id"] == customer_id
            and record["event_type"] == event_type
            and record["event_date"] == event_date
            and (details is None or record["details"] == details)
        ):
            return True

    return False


def get_customer_history(customer_id):
    with open("customer_history.json", "r") as file:
        data = json.load(file)

    history = []

    for record in data["history"]:
        if record["customer_id"] == customer_id:
            history.append(record)

    return history


def determine_customer_status(last_transaction):
    last_transaction_date = datetime.strptime(
        last_transaction,
        "%Y-%m-%d"
    ).date()

    today = date.today()
    days_since_transaction = (today - last_transaction_date).days

    if days_since_transaction <= 90:
        return "Active"
    else:
        return "Inactive"


def check_birthday_reminders():
    with open("customers.json", "r") as file:
        data = json.load(file)

    today = date.today()
    birthday_customers = []

    for customer in data["customers"]:
        birthday = datetime.strptime(
            customer["birthday"],
            "%Y-%m-%d").date()

        if birthday.month == today.month and birthday.day == today.day:
            birthday_customers.append(customer)

    return birthday_customers


def send_birthday_notification(customer):
    message = (
        f"Happy Birthday, {customer['name']}! "
        "We have a special birthday offer for you."
    )

    return message


def process_birthday_reminders():
    customers = check_birthday_reminders()

    notifications = []
    today_str = date.today().isoformat()

    for customer in customers:
        message = send_birthday_notification(customer)

        email_result = send_email(
            customer["email"],
            "Happy Birthday from ABC Company!",
            f"<p>{message}</p>"
        )

        notifications.append({
            "customer_id": customer["customer_id"],
            "message": message,
            "email_sent": email_result.get("success", False),
            "email_error": email_result.get("error")
        })


        if not has_history_entry(
            customer["customer_id"],
            "birthday_notification_sent",
            today_str
        ):
            add_customer_history(
                customer["customer_id"],
                "birthday_notification_sent",
                message,
                today_str
            )

    return notifications

def check_important_date_reminders():
    with open("customers.json", "r") as file:
        data = json.load(file)

    today = date.today()
    reminders = []

    for customer in data["customers"]:
        for important_date in customer.get("important_dates", []):
            reminder_date = datetime.strptime(
                important_date["date"],
                "%Y-%m-%d"
            ).date()

            days_until = (reminder_date - today).days

        if 0 <= days_until <= 3:
                reminders.append({
                    "customer_id": customer["customer_id"],
                    "name": customer["name"],
                    "email": customer["email"],
                    "type": important_date["type"],
                    "date": important_date["date"]
                })

    return reminders


def send_important_date_notification(reminder, days_until):
    if days_until == 0:
        timing = "is due today"
    elif days_until == 1:
        timing = "is due tomorrow"
    else:
        timing = f"is due in {days_until} days"

    return (
        f"Hello {reminder['name']}, this is a reminder that your "
        f"{reminder['type']} {timing}, on {reminder['date']}."
    )


def process_important_date_reminders():
    reminders = check_important_date_reminders()

    notifications = []

    today = date.today()

    for reminder in reminders:
        reminder_date = datetime.strptime(
            reminder["date"],
            "%Y-%m-%d"
        ).date()

        days_until = (reminder_date - today).days

        message = send_important_date_notification(
            reminder,
            days_until
        )
        email_result = send_email(
            reminder["email"],
            f"Reminder: your {reminder['type']} is coming up",
            f"<p>{message}</p>"
        )

        notifications.append({
            "customer_id": reminder["customer_id"],
            "message": message,
            "email_sent": email_result.get("success", False),
            "email_error": email_result.get("error")
        })

        today_str = date.today().isoformat()

        if not has_history_entry(
            reminder["customer_id"],
            "important_date_notification_sent",
            today_str,
            details=message
        ):
            add_customer_history(
                reminder["customer_id"],
                "important_date_notification_sent",
                message,
                today_str
            )

    return notifications


def send_offer_notification(customer, offer):
    return {
        "customer_id": customer["customer_id"],
        "message": f"Hi {customer['name']}, you are eligible for our {offer} offer!"
    }


def process_offer_notifications(offer):
    with open("customers.json", "r") as file:
        data = json.load(file)

    notifications = []

    for customer in data["customers"]:
        notification = send_offer_notification(customer, offer)

        email_result = send_email(
            customer["email"],
            f"Special offer for you: {offer}",
            f"<p>{notification['message']}</p>"
        )

        notification["email_sent"] = email_result.get("success", False)
        notification["email_error"] = email_result.get("error")
        notifications.append(notification)

    return notifications

def send_discount_notification(customer, discount):
    return {
        "customer_id": customer["customer_id"],
        "message": f"Hi {customer['name']}, you have a {discount}% discount available."
    }


def process_discount_notifications(discount):
    with open("customers.json", "r") as file:
        data = json.load(file)

    notifications = []

    for customer in data["customers"]:
        notification = send_discount_notification(customer, discount)

        email_result = send_email(
            customer["email"],
            f"You have a {discount}% discount waiting",
            f"<p>{notification['message']}</p>"
        )

        notification["email_sent"] = email_result.get("success", False)
        notification["email_error"] = email_result.get("error")
        notifications.append(notification)

    return notifications


def process_follow_up_reminders():
    with open("customers.json", "r") as file:
        data = json.load(file)

    notifications = []

    for customer in data["customers"]:
        for detail in customer.get("details", []):
            if detail["type"] == "follow_up":
                internal_message = f"Follow-up required: {detail['details']}"

                email_result = send_email(
                    customer["email"],
                    "Following up on your request",
                    f"<p>Hi {customer['name']}, we're following up on your "
                    "recent request. Our team will be in touch shortly.</p>"
                )

                notifications.append({
                    "customer_id": customer["customer_id"],
                    "message": internal_message,
                    "email_sent": email_result.get("success", False),
                    "email_error": email_result.get("error")
                })

    return notifications


def process_reengagement():
    with open("customers.json", "r") as file:
        data = json.load(file)

    today = date.today()
    notifications = []

    for customer in data["customers"]:
        last_transaction = datetime.strptime(
            customer["last_transaction"],
            "%Y-%m-%d"
        ).date()

        days_inactive = (today - last_transaction).days

        if days_inactive > 90:
            message = (
                f"Hi {customer['name']}, we haven't seen you in a while. "
                "We'd love to have you back."
            )

            email_result = send_email(
                customer["email"],
                "We miss you at ABC Company",
                f"<p>{message}</p>"
            )

            notifications.append({
                "customer_id": customer["customer_id"],
                "message": message,
                "email_sent": email_result.get("success", False),
                "email_error": email_result.get("error")
            })

    return notifications


def create_payment(customer_id, order_id, amount, status):
    transaction = get_transaction(order_id)

    # Check 1: Order must exist
    if transaction is None:
        return {
            "error": "I couldn't verify that order."
        }

    # Check 2: Order must belong to this customer
    if transaction["customer_id"] != customer_id:
        return {
            "error": "I couldn't verify that order."
        }

    # Check 3: Amount must match the transaction
    if float(amount) != float(transaction["amount"]):
        return {
            "error": "I couldn't verify that payment amount."
        }

    # Check 4: Customer's reported payment status
    # must be different from the actual transaction status
    if status.lower() == transaction["status"].lower():
        return {
            "error": "The payment status matches the transaction record. No payment issue was found."
        }

    # Only now record the payment issue
    payment = {
        "customer_id": customer_id,
        "order_id": order_id,
        "amount": amount,
        "status": status,
        "actual_status": transaction["status"],
        "created_at": datetime.now().isoformat()
    }

    with open("payments.json", "r") as file:
        data = json.load(file)

    data["payments"].append(payment)

    with open("payments.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "payment_issue_created",
        f"Payment issue reported for order {order_id}: customer reported {status}, transaction shows {transaction['status']}",
        date.today().isoformat()
    )

    return payment


def get_payment(order_id):
    with open("payments.json", "r") as file:
        data = json.load(file)

    for payment in data["payments"]:
        if payment["order_id"] == order_id:
            return payment

    return None


def update_payment_status(order_id, new_status):
    with open("payments.json", "r") as file:
        data = json.load(file)

    for payment in data["payments"]:
        if payment["order_id"] == order_id:
            payment["status"] = new_status

            with open("payments.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                payment["customer_id"],
                "payment_status_changed",
                f"Payment for order {order_id} status changed to {new_status}",
                date.today().isoformat()
            )

            return payment

    return None


def create_account_issue(customer_id, issue):
    account_issue = {
        "customer_id": customer_id,
        "issue": issue,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }

    with open("account_issues.json", "r") as file:
        data = json.load(file)

    data["account_issues"].append(account_issue)

    with open("account_issues.json", "w") as file:
        json.dump(data, file, indent=2)

    add_customer_history(
        customer_id,
        "account_issue_created",
        f"Account issue reported: {issue}",
        date.today().isoformat()
    )

    return account_issue


def get_account_issue(customer_id):
    with open("account_issues.json", "r") as file:
        data = json.load(file)

    for issue in data["account_issues"]:
        if issue["customer_id"] == customer_id:
            return issue

    return None


def update_account_issue_status(customer_id, new_status):
    with open("account_issues.json", "r") as file:
        data = json.load(file)

    for issue in data["account_issues"]:
        if issue["customer_id"] == customer_id:
            issue["status"] = new_status

            with open("account_issues.json", "w") as file:
                json.dump(data, file, indent=2)

            add_customer_history(
                customer_id,
                "account_issue_status_changed",
                f"Account issue status changed to {new_status}",
                date.today().isoformat()
            )

            return issue

    return None

# ---------- WhatsApp conversational session state ----------
whatsapp_sessions = {}

def get_whatsapp_session(phone):
    if phone not in whatsapp_sessions:
        whatsapp_sessions[phone] = {
            "customer_id": None,
            "customer_name": None,
            "flow": None,
            "stage": None,
            "data": {}
        }
    return whatsapp_sessions[phone]


def reset_flow(session):
    session["flow"] = None
    session["stage"] = None
    session["data"] = {}


IDENTITY_REQUIRED_TRIGGERS = {
    "raise a ticket": "ticket", "create a ticket": "ticket", "open a ticket": "ticket",
    "make a complaint": "complaint", "file a complaint": "complaint",
    "escalate": "escalation",
    "want a refund": "refund", "request a refund": "refund", "need a refund": "refund",
    "payment issue": "payment_issue", "payment problem": "payment_issue",
    "account issue": "account_issue", "account problem": "account_issue", "locked account": "account_issue",
    "my account details": "account_details",
    "account status": "account_status",
}

STATUS_CHECK_TRIGGERS = {
    "ticket status": "ticket_status",
    "order status": "order_status",
    "refund status": "refund_status",
    "complaint status": "complaint_status",
    "escalation status": "escalation_status",
}


def handle_whatsapp_text(from_number, text):
    session = get_whatsapp_session(from_number)
    lower = text.lower().strip()

    if session["flow"]:
        return continue_whatsapp_flow(session, text)

    for trigger, kind in STATUS_CHECK_TRIGGERS.items():
        if trigger in lower:
            session["flow"] = "status_check"
            session["stage"] = kind
            return f"Sure — please share the {kind.replace('_status', '').replace('_', ' ')} ID."

    for trigger, flow in IDENTITY_REQUIRED_TRIGGERS.items():
        if trigger in lower:
            session["flow"] = flow
            if session["customer_id"] and session["customer_name"]:
                return start_flow_after_identity(session)
            session["stage"] = "awaiting_id"
            return "Sure — first, what's your Customer ID (or email/phone)?"

    result = search_question(text)
    if result["action"] == "password_reset":
        if not (session["customer_id"] and session["customer_name"]):
            session["flow"] = "password_reset"
            session["stage"] = "awaiting_id"
            return "To reset your password, first tell me your Customer ID (or email/phone)."
        return do_password_reset(session)

    return result["answer"] or unknown()


def continue_whatsapp_flow(session, text):
    flow = session["flow"]
    stage = session["stage"]
    text = text.strip()

    if stage == "awaiting_id":
        session["data"]["pending_id"] = text
        session["stage"] = "awaiting_name"
        return "Thanks. And your full name as on your account?"

    if stage == "awaiting_name":
        customer = verify_customer_identity(session["data"]["pending_id"], text)
        if customer is None:
            session["stage"] = "awaiting_id"
            return "I couldn't verify those details. Please share your Customer ID again."
        session["customer_id"] = customer["customer_id"]
        session["customer_name"] = customer["name"]
        if flow == "password_reset":
            return do_password_reset(session)
        return start_flow_after_identity(session)

    if flow == "status_check":
        return do_status_check(session, stage, text)

    if flow == "ticket" and stage == "awaiting_issue":
        ticket = create_ticket(session["customer_id"], session["customer_name"], text)
        reset_flow(session)
        return f"Your ticket {ticket['ticket_id']} has been created successfully."

    if flow == "complaint" and stage == "awaiting_complaint":
        complaint = create_complaint(session["customer_id"], session["customer_name"], text)
        reset_flow(session)
        return f"Your complaint {complaint['complaint_id']} has been filed successfully."

    if flow == "escalation" and stage == "awaiting_reason":
        escalation = create_escalation(session["customer_id"], session["customer_name"], "Customer support issue", text)
        reset_flow(session)
        return f"Your escalation {escalation['escalation_id']} has been raised successfully."

    if flow == "refund" and stage == "awaiting_order":
        transaction = get_transaction(text)
        if transaction is None or transaction["customer_id"] != session["customer_id"]:
            return "I couldn't verify that order for your account. Please share the correct order ID."
        session["data"]["order_id"] = text
        session["stage"] = "awaiting_reason"
        return "Got it. What's the reason for the refund?"

    if flow == "refund" and stage == "awaiting_reason":
        session["data"]["reason"] = text
        session["stage"] = "awaiting_amount"
        return "And the refund amount?"

    if flow == "refund" and stage == "awaiting_amount":
        try:
            amount = float(text)
        except ValueError:
            return "Please enter a valid number for the amount."
        result = create_refund(session["customer_id"], session["data"]["order_id"], session["data"]["reason"], amount)
        reset_flow(session)
        if "error" in result:
            return result["error"]
        return f"Your refund request for order {result['order_id']} has been created successfully."

    if flow == "payment_issue" and stage == "awaiting_order":
        session["data"]["order_id"] = text
        session["stage"] = "awaiting_description"
        return "Thanks. Briefly describe what happened with the payment."

    if flow == "payment_issue" and stage == "awaiting_description":
        issue_text = f"Payment issue for order {session['data']['order_id']}: {text}"
        ticket = create_ticket(session["customer_id"], session["customer_name"], issue_text)
        reset_flow(session)
        return f"I've created ticket {ticket['ticket_id']} for your payment issue. A representative will follow up."

    if flow == "account_issue" and stage == "awaiting_issue":
        create_account_issue(session["customer_id"], text)
        reset_flow(session)
        return "Your account issue has been recorded. A support representative will assist you shortly."

    reset_flow(session)
    return unknown()


def start_flow_after_identity(session):
    flow = session["flow"]

    if flow == "ticket":
        session["stage"] = "awaiting_issue"
        return "Please describe the issue you'd like to report."
    if flow == "complaint":
        session["stage"] = "awaiting_complaint"
        return "Please describe your complaint."
    if flow == "escalation":
        session["stage"] = "awaiting_reason"
        return "Please tell me why you'd like to escalate this issue."
    if flow == "refund":
        session["stage"] = "awaiting_order"
        return "Please provide the order ID for the refund."
    if flow == "payment_issue":
        session["stage"] = "awaiting_order"
        return "Could you provide the order ID related to the payment issue, if you have one?"
    if flow == "account_issue":
        session["stage"] = "awaiting_issue"
        return "Please describe the account issue."
    if flow == "account_details":
        customer = find_customer(session["customer_id"])
        history = get_customer_history(session["customer_id"])
        reset_flow(session)
        lines = "\n".join(f"- {h['event_date']}: {h['details']}" for h in history[-5:]) or "No history on file yet."
        return (f"Name: {customer['name']}\nEmail: {customer['email']}\nStatus: {customer['status']}\n"
                f"Last transaction: {customer['last_transaction']}\n\nRecent history:\n{lines}")
    if flow == "account_status":
        customer = find_customer(session["customer_id"])
        reset_flow(session)
        return f"Your account status is: {customer['status']}."

    reset_flow(session)
    return unknown()


def do_password_reset(session):
    reset = create_password_reset(session["customer_id"])
    reset_link = f"{frontend_base_url}/reset-password?token={reset['token']}"
    add_customer_history(session["customer_id"], "password_reset_requested",
                          f"Password reset link generated (expires {reset['expires_at']}).", date.today().isoformat())
    reset_flow(session)
    return f"I've verified your identity. Here is your password reset link (valid for 15 minutes): {reset_link}"


def do_status_check(session, kind, identifier):
    reset_flow(session)
    if kind == "ticket_status":
        t = get_ticket(identifier)
        return f"Ticket {t['ticket_id']} — status: {t['status']}. Issue: {t['issue']}" if t else "I couldn't find that ticket."
    if kind == "order_status":
        t = get_transaction(identifier)
        return f"Order {t['order_id']} — status: {t['status']}, amount: {t['amount']}." if t else "I couldn't find that order."
    if kind == "refund_status":
        r = get_refund(identifier)
        return f"Refund for order {r['order_id']} — status: {r['status']}, amount: {r['amount']}." if r else "I couldn't find a refund for that order."
    if kind == "complaint_status":
        c = get_complaint(identifier)
        return f"Complaint {c['complaint_id']} — status: {c['status']}." if c else "I couldn't find that complaint."
    if kind == "escalation_status":
        e = get_escalation(identifier)
        return f"Escalation {e['escalation_id']} — status: {e['status']}." if e else "I couldn't find that escalation."
    return unknown()


@app.get("/welcome")
def get_welcome():
    return {"message": welcome()}

@app.get("/unknown")
def get_unknown():
    return {"message": unknown()}

@app.get("/goodbye")
def get_goodbye():
    return {"message": goodbye()}


class Question(BaseModel):
    question: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

class TicketRequest(BaseModel):
    customer_id: str
    customer_name: str
    issue: str

class TicketStatusRequest(BaseModel):
    customer_id: str
    ticket_id: str
    status: str

class ComplaintRequest(BaseModel):
    customer_id: str
    customer_name: str
    complaint: str

class ComplaintStatusRequest(BaseModel):
    customer_id: str
    complaint_id: str
    status: str

class EscalationRequest(BaseModel):
    customer_id: str
    customer_name: str
    issue: str
    reason: str

class EscalationStatusRequest(BaseModel):
    customer_id: str
    escalation_id: str
    status: str

class CustomerRequest(BaseModel):
    name: str
    email: str
    phone: str
    last_transaction: date
    birthday: date
    important_dates: list
    details: list

class CustomerStatusRequest(BaseModel):
    customer_id: str

class TransactionRequest(BaseModel):
    customer_id: str
    amount: float
    details: str

class OrderIssueRequest(BaseModel):
    customer_id: str
    order_id: str
    issue: str

class OrderStatusRequest(BaseModel):
    order_id: str
    status: str

class RefundRequest(BaseModel):
    customer_id: str
    order_id: str
    reason: str
    amount: float

class RefundStatusRequest(BaseModel):
    order_id: str
    status: str

class CustomerStatusLogicRequest(BaseModel):
    customer_id: str
    last_transaction: date

class OfferRequest(BaseModel):
    offer: str

class DiscountRequest(BaseModel):
    discount: float

class PaymentRequest(BaseModel):
    customer_id: str
    order_id: str
    amount: float
    status: str

class PaymentStatusRequest(BaseModel):
    order_id: str
    status: str

class AccountIssueRequest(BaseModel):
    customer_id: str
    issue: str

class AccountIssueStatusRequest(BaseModel):
    customer_id: str
    status: str

@app.post("/tickets")
def create_ticket_endpoint(data: TicketRequest):
    ticket = create_ticket(data.customer_id, data.customer_name, data.issue)
    return ticket

@app.get("/tickets")
def list_tickets_endpoint(status: str = None):
    tickets = list_tickets(status)

    return {"tickets": tickets}

@app.get("/tickets/{ticket_id}")
def lookup_ticket(ticket_id: str):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        return {"error": "ticket not found"}

    return ticket

@app.post("/tickets/status")
def update_status(data: TicketStatusRequest):
    ticket = update_ticket_status(data.customer_id, data.ticket_id, data.status)

    if ticket is None:
        return {"error": "ticket not found"}

    return ticket


@app.post("/complaints")
def create_complaint_endpoint(data: ComplaintRequest):
    complaint = create_complaint(
        data.customer_id,
        data.customer_name,
        data.complaint
    )
    return complaint


@app.get("/complaints/{complaint_id}")
def lookup_complaint(complaint_id: str):
    complaint = get_complaint(complaint_id)

    if complaint is None:
        return {"error": "Complaint not found"}

    return complaint


@app.post("/complaints/status")
def update_complaint_status_endpoint(data: ComplaintStatusRequest):
    complaint = update_complaint_status(
        data.customer_id,
        data.complaint_id,
        data.status
    )

    if complaint is None:
        return {"error": "Complaint not found"}

    return complaint


@app.post("/escalations")
def create_escalation_endpoint(data: EscalationRequest):
    escalation = create_escalation(
        data.customer_id,
        data.customer_name,
        data.issue,
        data.reason
    )
    return escalation


@app.get("/escalations/{escalation_id}")
def lookup_escalation(escalation_id: str):
    escalation = get_escalation(escalation_id)

    if escalation is None:
        return {"error": "Escalation not found"}

    return escalation


@app.post("/escalations/status")
def update_escalation_status_endpoint(data: EscalationStatusRequest):
    escalation = update_escalation_status(
        data.customer_id,
        data.escalation_id,
        data.status
    )

    if escalation is None:
        return {"error": "Escalation not found"}

    return escalation


@app.post("/customers")
def create_customer_endpoint(data: CustomerRequest):
    customer = create_customer(
        data.name,
        data.email,
        data.phone,
        data.last_transaction,
        data.birthday,
        data.important_dates,
        data.details
    )
    return customer


@app.get("/customers")
def lookup_customer(identifier: str):
    customer = find_customer(identifier)

    if customer is None:
        return {"error": "Customer not found"}

    return customer

@app.post("/transactions")
def create_transaction_endpoint(data: TransactionRequest):
    transaction = create_transaction(
        data.customer_id,
        data.amount,
        data.details
    )

    return transaction


@app.get("/transactions/{order_id}")
def lookup_transaction(order_id: str):
    transaction = get_transaction(order_id)

    if transaction is None:
        return {"error": "Transaction not found"}

    return transaction


@app.post("/orders/issues")
def create_order_issue_endpoint(data: OrderIssueRequest):
    order_issue = create_order_issue(
        data.customer_id,
        data.order_id,
        data.issue
    )
    return order_issue


@app.get("/orders/{order_id}")
def lookup_order(order_id: str):
    order = get_order(order_id)

    if order is None:
        return {"error": "Order not found"}

    return order


@app.post("/orders/status")
def update_order_status_endpoint(data: OrderStatusRequest):
    order = update_order_status(
        data.customer_id,
        data.order_id,
        data.status
    )

    if order is None:
        return {"error": "Order not found"}

    return order


@app.post("/refunds")
def create_refund_endpoint(data: RefundRequest):
    refund = create_refund(
        data.customer_id,
        data.order_id,
        data.reason,
        data.amount
    )

    return refund


@app.get("/refunds/{order_id}")
def lookup_refund(order_id: str):
    refund = get_refund(order_id)

    if refund is None:
        return {"error": "Refund not found"}

    return refund


@app.post("/refunds/status")
def update_refund_status_endpoint(data: RefundStatusRequest):
    refund = update_refund_status(
        data.customer_id,
        data.order_id,
        data.status
    )

    if refund is None:
        return {"error": "Refund not found"}

    return refund


@app.get("/customers/{customer_id}/history")
def lookup_customer_history(customer_id: str):
    history = get_customer_history(customer_id)

    return {
        "customer_id": customer_id,
        "history": history
    }


@app.post("/customers/status")
def update_customer_status_endpoint(data: CustomerStatusRequest):

    with open("customers.json", "r") as file:
        data_file = json.load(file)

    for customer in data_file["customers"]:
        if customer["customer_id"] == data.customer_id:

            status = determine_customer_status(
                customer["last_transaction"]
            )

            customer["status"] = status

            with open("customers.json", "w") as file:
                json.dump(data_file, file, indent=2)

            add_customer_history(
                customer["customer_id"],
                "status_changed",
                f"Customer status changed to {status}",
                date.today().isoformat()
            )

            return {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "status": status
            }

    return {"error": "Customer not found"}

@app.get("/customers/birthdays")
def birthday_reminders():
    customers = check_birthday_reminders()

    return {
        "birthday_customers": customers
    }


@app.get("/customers/birthday-reminders")
def birthday_reminder_process():
    notifications = process_birthday_reminders()

    return {
        "notifications": notifications
    }


@app.get("/customers/important-date-reminders")
def important_date_reminders():
    notifications = process_important_date_reminders()

    return {
        "notifications": notifications
    }


@app.post("/customers/offer-notifications")
def offer_notifications(data: OfferRequest):
    return {
        "notifications": process_offer_notifications(data.offer)
    }


@app.post("/customers/discount-notifications")
def discount_notifications(data: DiscountRequest):
    return {
        "notifications": process_discount_notifications(data.discount)
    }


@app.get("/customers/follow-up-reminders")
def follow_up_reminders():
    return {
        "notifications": process_follow_up_reminders()
    }


@app.get("/customers/reengagement")
def reengagement():
    return {
        "notifications": process_reengagement()
    }


@app.post("/payments")
def create_payment_endpoint(data: PaymentRequest):
    payment = create_payment(
        data.customer_id,
        data.order_id,
        data.amount,
        data.status
    )

    return payment


@app.get("/payments/{order_id}")
def lookup_payment(order_id: str):
    payment = get_payment(order_id)

    if payment is None:
        return {"error": "Payment not found"}

    return payment


@app.post("/payments/status")
def update_payment_status_endpoint(data: PaymentStatusRequest):
    payment = update_payment_status(
        data.order_id,
        data.status
    )

    if payment is None:
        return {"error": "Payment not found"}

    return payment


@app.post("/account-issues")
def create_account_issue_endpoint(data: AccountIssueRequest):
    account_issue = create_account_issue(
        data.customer_id,
        data.issue
    )

    return account_issue


@app.get("/account-issues/{customer_id}")
def lookup_account_issue(customer_id: str):
    issue = get_account_issue(customer_id)

    if issue is None:
        return {"error": "Account issue not found"}

    return issue


@app.post("/account-issues/status")
def update_account_issue_status_endpoint(
    data: AccountIssueStatusRequest
):
    issue = update_account_issue_status(
        data.customer_id,
        data.status
    )

    if issue is None:
        return {"error": "Account issue not found"}

    return issue

@app.get("/help-centre")
def get_help_centre():
    return help_centre_docs


@app.get("/whatsapp/webhook")
def verify_whatsapp_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="Verification failed", status_code=403)


@app.post("/whatsapp/webhook")
async def receive_whatsapp_message(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            text = message["text"]["body"]

            answer = handle_whatsapp_text(from_number, text)
            send_whatsapp_message(from_number, answer)

    except (KeyError, IndexError):
        pass

    return {"status": "received"}


@app.post("/ask")
def ask_question(data: Question):
    result = search_question(data.question)
    answer = result["answer"]
    action = result["action"]

    if answer is None:
        return {"answer": unknown()}

    if action == "password_reset":
        customer = verify_customer_identity(data.customer_id, data.customer_name)

        if customer is None:
            return {
                "answer": (
                    "To reset your password, I first need to verify your identity. "
                    "Please make sure your customer ID and name are entered correctly "
                    "in \"Your details\", then ask again."
                )
            }

        reset = create_password_reset(customer["customer_id"])
        reset_link = f"{frontend_base_url}/reset-password?token={reset['token']}"

        add_customer_history(
            customer["customer_id"],
            "password_reset_requested",
            f"Password reset link generated (expires {reset['expires_at']}).",
            date.today().isoformat()
        )

        return {
            "answer": (
                "I've verified your identity. Here is your password reset link "
                f"(valid for 15 minutes): {reset_link}"
            )
        }

    return {"answer": answer}


@app.post("/password-reset/confirm")
def password_reset_confirm_endpoint(data: PasswordResetConfirmRequest):
    result = reset_password(data.token, data.new_password)

    if result.get("error"):
        return {"success": False, "answer": result["error"]}

    return {
        "success": True,
        "answer": "Your password has been reset successfully. You can now log in with your new password."
    }