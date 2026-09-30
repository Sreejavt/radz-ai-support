// Change this if your FastAPI backend runs somewhere other than the
// default `uvicorn api:app --reload` address.
const BASE_URL = "http://localhost:8000";

async function postJSON(path, body) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return response.json();
}

async function getJSON(path) {
  const response = await fetch(`${BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return response.json();
}

export async function getHelpCentreDocs() {
  return getJSON("/help-centre");
}

// Ask a free-form question. Optionally pass customer_id/customer_name once
// the customer is identified, so ticket-creation flows (like password
// reset) can attach to their record.
export function askQuestion(question, customerId, customerName) {
  return postJSON("/ask", {
    question,
    customer_id: customerId || null,
    customer_name: customerName || null
  });
}
export function createTicket(customerId, customerName, issue) {
  return postJSON("/tickets", {
    customer_id: customerId,
    customer_name: customerName,
    issue: issue
  });
}
export function createComplaint(customerId, customerName, complaint) {
  return postJSON("/complaints", {
    customer_id: customerId,
    customer_name: customerName,
    complaint: complaint
  });
}

export function createEscalation(customerId, customerName, issue, reason) {
  return postJSON("/escalations", {
    customer_id: customerId,
    customer_name: customerName,
    issue: issue,
    reason: reason
  });
}

export function createRefund(customerId, orderId, reason, amount) {
  return postJSON("/refunds", {
    customer_id: customerId,
    order_id: orderId,
    reason: reason,
    amount: amount
  });
}

export function createPayment(customerId, orderId, amount, status) {
  return postJSON("/payments", {
    customer_id: customerId,
    order_id: orderId,
    amount: amount,
    status: status
  });
}

export function createAccountIssue(customerId, issue) {
  return postJSON("/account-issues", {
    customer_id: customerId,
    issue: issue
  });
}

// Looks up a customer's full record by customer ID, email, or phone.
export function lookupCustomer(identifier) {
  return getJSON(`/customers?identifier=${encodeURIComponent(identifier)}`);
}

// Returns a customer's full event history (tickets, complaints, refunds,
// escalations, notifications, status changes, etc.)
export function lookupCustomerHistory(customerId) {
  return getJSON(`/customers/${encodeURIComponent(customerId)}/history`);
}

// Confirms the password-reset ticket after the customer says yes.
// Submits a reset token + new password to complete the password reset.
export function confirmPasswordReset(token, newPassword) {
  return postJSON("/password-reset/confirm", {
    token,
    new_password: newPassword
  });
}

// Quick-action lookups — these hit your existing GET endpoints directly.
export function lookupTicket(ticketId) {
  return getJSON(`/tickets/${encodeURIComponent(ticketId)}`);
}

export function lookupOrder(orderId) {
  return getJSON(`/orders/${encodeURIComponent(orderId)}`);
}

// Refunds are validated against actual purchase records (transactions),
// not order-issue tickets — use this for refund order-ID verification.
export function lookupTransaction(orderId) {
  return getJSON(`/transactions/${encodeURIComponent(orderId)}`);
}

export function lookupRefund(orderId) {
  return getJSON(`/refunds/${encodeURIComponent(orderId)}`);
}

export function lookupComplaint(complaintId) {
  return getJSON(`/complaints/${encodeURIComponent(complaintId)}`);
}

export function lookupEscalation(escalationId) {
  return getJSON(`/escalations/${encodeURIComponent(escalationId)}`);
}
