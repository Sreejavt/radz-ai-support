frontend_base_url = "http://localhost:5173"
# Resend's sandbox sender. Works for testing (delivers only to the email
# your Resend account was signed up with). Once a real domain is verified
# for a client, this becomes something like "ABC Company <support@clientdomain.com>".
email_from = "ABC Company <onboarding@resend.dev>"

company_name = "ABC Company"

welcome_message =(
    f"\nWelcome to {company_name}!\n"
    "How can I help you today?"
)

unknown_response = (
     "I'm sorry, I couldn't find an answer to that question."
)

goodbye_message = (
    "Thank you for contacting us. Have a great day!\n"
)