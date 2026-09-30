import { useState, useRef, useEffect } from "react";
import {
  askQuestion,
  confirmPasswordReset,
  lookupTicket,
  lookupTransaction,
  lookupRefund,
  lookupComplaint,
  lookupEscalation,
  createTicket,
  createComplaint,
  createEscalation,
  createRefund,
  createPayment,
  createAccountIssue,
  lookupCustomer,
  lookupCustomerHistory
} from "./api.js";

const COMPANY_NAME = "ABC Company";

function Message({ sender, text }) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;

  const parts = text.split(urlRegex);

  return (
    <div className={`message-row ${sender}`}>
      <div className={`message-bubble ${sender}`}>
        {parts.map((part, index) => {
          if (part.match(/^https?:\/\//)) {
            return (
              <a
                key={index}
                href={part}
                target="_blank"
                rel="noopener noreferrer"
              >
                {part}
              </a>
            );
          }

          return <span key={index}>{part}</span>;
        })}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="message-row agent">
      <div className="message-bubble agent typing">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  );
}

const QUICK_ACTIONS = [
  { key: "ticket", label: "Check ticket status", placeholder: "e.g. TKT-A1B2C3D4" },
  { key: "order", label: "Check order status", placeholder: "e.g. ORD-000012" },
  { key: "refund", label: "Check refund status", placeholder: "e.g. ORD-000012" },
  { key: "complaint", label: "Check complaint status", placeholder: "e.g. CMP-A1B2C3D4" },
  { key: "escalation", label: "Check escalation status", placeholder: "e.g. ESC-A1B2C3D4" }
];

export default function SupportAgent() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "agent",
      text: `Welcome to ${COMPANY_NAME}! How can I help you today?`
    }
  ]);
  const [input, setInput] = useState("");
  const [isWaiting, setIsWaiting] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [ticketFlow, setTicketFlow] = useState(null);
  const [complaintFlow, setComplaintFlow] = useState(null);
  const [escalationFlow, setEscalationFlow] = useState(null);
  const [refundFlow, setRefundFlow] = useState({
    stage: null,
    orderId: "",
    reason: ""
  });
  const [paymentFlow, setPaymentFlow] = useState({
  stage: null,
  orderId: "",
  description: ""
});
  const [accountIssueFlow, setAccountIssueFlow] = useState(null);

  const [activeLookup, setActiveLookup] = useState(null);
  const [lookupInput, setLookupInput] = useState("");

  const [customerId, setCustomerId] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [showIdentity, setShowIdentity] = useState(false);

  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isWaiting, activeLookup]);

  function addMessage(sender, text) {
    setMessages((prev) => [
      ...prev,
      { id: `${Date.now()}-${Math.random()}`, sender, text }
    ]);
  }

  /*async function handleSend(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || isWaiting) return;

    addMessage("user", question);
    setInput("");
    
    setIsWaiting(true);

    try {
      const result = await askQuestion(question, customerId, customerName);
      addMessage("agent", result.answer);

      if (result.action_available === "password_reset_ticket") {
        setPendingAction("password_reset_ticket");
      } else {
        setPendingAction(null);
      }
    } catch (err) {
      addMessage(
        "agent",
        "Sorry, I couldn't reach support right now. Please try again shortly."
      );
    } finally {
      setIsWaiting(false);
    }
  }*/
  async function handleSend(event) {
  event.preventDefault();

  const question = input.trim();
  if (!question || isWaiting) return;
  if (
  question.toLowerCase().includes("make a complaint") ||
  question.toLowerCase().includes("file a complaint") ||
  question.toLowerCase().includes("raise a complaint") ||
  question.toLowerCase().includes("want to complain")
) {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name, then describe your complaint."
    );
    setShowIdentity(true);
  } else {
    addMessage(
      "agent",
      "Please describe your complaint."
    );
  }

  setComplaintFlow("waiting_for_complaint");
  return;
}
  // Complaint creation flow
  if (complaintFlow === "waiting_for_complaint") {
    addMessage("user", question);
    setInput("");

    if (!customerId || !customerName) {
      addMessage(
        "agent",
        "Please provide your customer ID and name first."
      );
      setShowIdentity(true);
      return;
    }

    setIsWaiting(true);

    try {
      const result = await createComplaint(
        customerId,
        customerName,
        question
      );

      addMessage(
        "agent",
        `Your complaint ${result.complaint_id} has been created successfully.`
      );

      setComplaintFlow(null);
    } catch (err) {
      addMessage(
        "agent",
        "I couldn't create the complaint right now. Please try again shortly."
      );
    } finally {
      setIsWaiting(false);
    }

    return;
  }
  if (
  question.toLowerCase().includes("escalate") ||
  question.toLowerCase().includes("raise an escalation") ||
  question.toLowerCase().includes("escalate this issue")
) {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name, then describe the issue you want to escalate."
    );
    setShowIdentity(true);
  } else {
    addMessage(
      "agent",
      "Please describe the issue you would like to escalate."
    );
  }

  setEscalationFlow("waiting_for_issue");
  return;
}
  if (
  question.toLowerCase().includes("escalate") ||
  question.toLowerCase().includes("raise an escalation") ||
  question.toLowerCase().includes("escalate this issue")
) {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name, then describe the issue you want to escalate."
    );
    setShowIdentity(true);
  } else {
    addMessage(
      "agent",
      "Please describe the issue you would like to escalate."
    );
  }

  setEscalationFlow("waiting_for_issue");
  return;
}
    // Escalation creation flow
if (escalationFlow === "waiting_for_issue") {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name first."
    );
    setShowIdentity(true);
    return;
  }

  setIsWaiting(false);
  setEscalationFlow("waiting_for_reason");

  addMessage(
    "agent",
    "Please tell me why you would like to escalate this issue."
  );

  return;
}

if (escalationFlow === "waiting_for_reason") {
  const reason = question;

  addMessage("user", reason);
  setInput("");
  setIsWaiting(true);

  try {
    const result = await createEscalation(
      customerId,
      customerName,
      "Customer support issue",
      reason
    );

    addMessage(
      "agent",
      `Your escalation ${result.escalation_id} has been created successfully.`
    );

    setEscalationFlow(null);
  } catch (err) {
    addMessage(
      "agent",
      "I couldn't create the escalation right now. Please try again shortly."
    );
  } finally {
    setIsWaiting(false);
  }

  return;
}
    if (
    question.toLowerCase().includes("raise a ticket") ||
    question.toLowerCase().includes("create a ticket") ||
    question.toLowerCase().includes("open a ticket") ||
    question.toLowerCase().includes("log a ticket")
  ) {
    addMessage("user", question);
    setInput("");

    if (!customerId || !customerName) {
      addMessage(
        "agent",
        "Please provide your customer ID and name, then tell me the issue you'd like to report."
      );
      setShowIdentity(true);
      setTicketFlow("waiting_for_issue");
      return;
    }

    addMessage(
      "agent",
      "Please describe the issue you'd like to report."
    );
    setTicketFlow("waiting_for_issue");
    return;
  }

  // If the customer is already in the ticket flow,
  // this message is their issue.
  if (ticketFlow === "waiting_for_issue") {
    addMessage("user", question);
    setInput("");

    if (!customerId || !customerName) {
      addMessage(
        "agent",
        "Please provide your customer ID and name first."
      );
      setShowIdentity(true);
      return;
    }

    setIsWaiting(true);

    try {
      const result = await createTicket(
        customerId,
        customerName,
        question
      );

      addMessage(
        "agent",
        `Your ticket ${result.ticket_id} has been created successfully.`
      );

      setTicketFlow(null);
    } catch (err) {
      addMessage(
        "agent",
        "I couldn't create the ticket right now. Please try again shortly."
      );
    } finally {
      setIsWaiting(false);
    }

    return;
  }
  if (
  question.toLowerCase().includes("refund") &&
  (
    question.toLowerCase().includes("want") ||
    question.toLowerCase().includes("request") ||
    question.toLowerCase().includes("need")
  )
) {
  addMessage("user", question);
  setInput("");

  if (!customerId) {
    addMessage(
      "agent",
      "Please provide your customer ID first."
    );
    setShowIdentity(true);
    return;
  }

  setRefundFlow({
    stage: "waiting_for_order",
    orderId: "",
    reason: ""
  });

  addMessage(
    "agent",
    "Please provide the order ID for the refund."
  );

  return;
}
  // Refund creation flow
if (refundFlow.stage === "waiting_for_order") {
  addMessage("user", question);
  setInput("");
  setIsWaiting(true);

  try {
    const order = await lookupTransaction(question);

    if (order.error) {
      addMessage(
        "agent",
        "I couldn't find that order ID. Please enter the correct order ID."
      );

      // Stay in waiting_for_order
      setIsWaiting(false);
      return;
    }

    if (order.customer_id !== customerId) {
      addMessage(
        "agent",
        "That order does not belong to this customer. Please enter the correct order ID."
      );

      // Stay in waiting_for_order
      setIsWaiting(false);
      return;
    }

    setRefundFlow({
      ...refundFlow,
      stage: "waiting_for_reason",
      orderId: question
    });

    addMessage(
      "agent",
      "Please tell me the reason for the refund."
    );

  } catch (err) {
    addMessage(
      "agent",
      "I couldn't verify that order right now. Please enter the order ID again."
    );
  } finally {
    setIsWaiting(false);
  }

  return;
}

if (refundFlow.stage === "waiting_for_reason") {
  addMessage("user", question);
  setInput("");

  setRefundFlow({
    ...refundFlow,
    stage: "waiting_for_amount",
    reason: question
  });

  addMessage(
    "agent",
    "Please provide the refund amount."
  );

  return;
}

if (refundFlow.stage === "waiting_for_amount") {
  addMessage("user", question);
  setInput("");

  const amount = Number(question);

  if (Number.isNaN(amount)) {
    addMessage(
      "agent",
      "I couldn't verify that order amount. Please enter the correct refund amount."
    );
    return;
  }

  setIsWaiting(true);

  try {
    const result = await createRefund(
      customerId,
      refundFlow.orderId,
      refundFlow.reason,
      amount
    );

    if (result.error) {
      addMessage("agent", result.error);
      return;
    }

    addMessage(
      "agent",
      `Your refund request for order ${result.order_id} has been created successfully.`
    );

    setRefundFlow({
      stage: null,
      orderId: "",
      reason: ""
    });

  } catch (err) {
    addMessage(
      "agent",
      "I couldn't verify that order amount. Please enter the correct refund amount."
    );
  } finally {
    setIsWaiting(false);
  }

  return;
}
if (
  question.toLowerCase().includes("payment issue") ||
  question.toLowerCase().includes("problem with my payment") ||
  question.toLowerCase().includes("payment problem")
) {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name first."
    );
    setShowIdentity(true);
    return;
  }

  setPaymentFlow({
    stage: "waiting_for_order",
    orderId: "",
    description: ""
  });

  addMessage(
    "agent",
    "I'm sorry to hear that. Could you provide the order ID related to the payment issue, if you have one?"
  );

  return;
}
if (paymentFlow.stage === "waiting_for_order") {
  addMessage("user", question);
  setInput("");

  setPaymentFlow({
    ...paymentFlow,
    stage: "waiting_for_description",
    orderId: question
  });

  addMessage(
    "agent",
    "Thanks. Could you briefly describe what happened with the payment?"
  );

  return;
}

if (paymentFlow.stage === "waiting_for_description") {
  addMessage("user", question);
  setInput("");
  setIsWaiting(true);

  const issueText = paymentFlow.orderId
    ? `Payment issue for order ${paymentFlow.orderId}: ${question}`
    : `Payment issue: ${question}`;

  try {
    const result = await createTicket(customerId, customerName, issueText);

    if (result.error) {
      addMessage("agent", result.error);
      return;
    }

    addMessage(
      "agent",
      `I've created ticket ${result.ticket_id} for your payment issue. A human representative will contact you shortly.`
    );

    setPaymentFlow({
      stage: null,
      orderId: "",
      description: ""
    });

  } catch (err) {
    addMessage(
      "agent",
      "I couldn't create that ticket right now. Please try again shortly."
    );
  } finally {
    setIsWaiting(false);
  }

  return;
}
// Account issue flow
if (accountIssueFlow === "waiting_for_issue") {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name first."
    );
    setShowIdentity(true);
    return;
  }

  setIsWaiting(true);

  try {
    const result = await createAccountIssue(
      customerId,
      question
    );

    if (result.error) {
      addMessage("agent", result.error);
      return;
    }

    addMessage(
      "agent",
      "Your account issue has been recorded successfully. A support representative will assist you shortly."
    );

    setAccountIssueFlow(null);

  } catch (err) {
    addMessage(
      "agent",
      "I couldn't record the account issue right now. Please try again shortly."
    );
  } finally {
    setIsWaiting(false);
  }

  return;
}

// Account issue trigger
if (
  question.toLowerCase().includes("account issue") ||
  question.toLowerCase().includes("account problem") ||
  question.toLowerCase().includes("problem with my account") ||
  question.toLowerCase().includes("issue with my account") ||
  question.toLowerCase().includes("can't access my account") ||
  question.toLowerCase().includes("cannot access my account") ||
  question.toLowerCase().includes("account is locked") ||
  question.toLowerCase().includes("locked account") ||
  question.toLowerCase().includes("account locked")
) {
  addMessage("user", question);
  setInput("");

  if (!customerId || !customerName) {
    addMessage(
      "agent",
      "Please provide your customer ID and name first."
    );
    setShowIdentity(true);
    return;
  }

  setAccountIssueFlow("waiting_for_issue");

  addMessage(
    "agent",
    "Please describe the account issue."
  );

  return;
}
  addMessage("user", question);
  setInput("");
  setIsWaiting(true);

  try {
    const result = await askQuestion(
      question,
      customerId,
      customerName
    );

    addMessage("agent", result.answer);

    if (result.action_available === "password_reset_ticket") {
      setPendingAction("password_reset_ticket");
    } else {
      setPendingAction(null);
    }

  } catch (err) {
    addMessage(
      "agent",
      "Sorry, I couldn't reach support right now. Please try again shortly."
    );
  } finally {
    setIsWaiting(false);
  }
}


  async function handlePasswordResetConfirm(confirmed) {
    setPendingAction(null);

    if (!confirmed) {
      addMessage("agent", "No problem — let me know if there's anything else I can help with.");
      return;
    }

    if (!customerId || !customerName) {
      addMessage(
        "agent",
        "I need your name and customer ID before I can log that ticket — add them above, then ask again."
      );
      setShowIdentity(true);
      return;
    }

    setIsWaiting(true);
    try {
      const result = await confirmPasswordReset(customerId, customerName);
      addMessage("agent", result.answer);
    } catch (err) {
      addMessage("agent", "I couldn't create that ticket just now. Please try again shortly.");
    } finally {
      setIsWaiting(false);
    }
  }

  function openLookup(key) {
    setActiveLookup(key);
    setLookupInput("");
  }

  async function handleLookupSubmit(event) {
    event.preventDefault();
    const id = lookupInput.trim();
    if (!id) return;

    const action = QUICK_ACTIONS.find((a) => a.key === activeLookup);
    addMessage("user", `${action.label}: ${id}`);
    setActiveLookup(null);
    setIsWaiting(true);

    try {
      let record;
      if (action.key === "ticket") record = await lookupTicket(id);
      if (action.key === "order") record = await lookupTransaction(id);
      if (action.key === "refund") record = await lookupRefund(id);
      if (action.key === "complaint") record = await lookupComplaint(id);
      if (action.key === "escalation") record = await lookupEscalation(id);

      if (record.error) {
        addMessage("agent", `I couldn't find that — ${record.error}.`);
      } else {
        addMessage("agent", formatRecord(action.key, record));
      }
    } catch (err) {
      addMessage("agent", "Sorry, I couldn't look that up right now. Please try again shortly.");
    } finally {
      setIsWaiting(false);
    }
  }

  function formatRecord(kind, record) {
    if (kind === "ticket") {
      return `Ticket ${record.ticket_id} — status: ${record.status}. Issue: ${record.issue}`;
    }
    if (kind === "order") {
      return `Order ${record.order_id} — status: ${record.status}, amount: ${record.amount}, purchased on ${record.transaction_date}.`;
    }
    if (kind === "refund") {
      return `Refund for order ${record.order_id} — status: ${record.status}, amount: ${record.amount}.`;
    }
    if (kind === "complaint") {
      return `Complaint ${record.complaint_id} — status: ${record.status}. Details: ${record.complaint}`;
    }
    if (kind === "escalation") {
      return `Escalation ${record.escalation_id} — status: ${record.status}. Reason: ${record.reason}`;
    }
    return "Here's what I found.";
  }
  
 async function verifyIdentity() {
  if (!customerId) {
    addMessage(
      "agent",
      "Please enter your customer ID, email, or phone number in \"Your details\" first."
    );
    setShowIdentity(true);
    return null;
  }

  const record = await lookupCustomer(customerId);

  if (record.error) {
    addMessage(
      "agent",
      `I couldn't find that customer — ${record.error}.`
    );
    return null;
  }

  if (
    customerName &&
    record.name.trim().toLowerCase() !==
      customerName.trim().toLowerCase()
  ) {
    addMessage(
      "agent",
      "The name doesn't match our records. Please double-check your details."
    );
    return null;
  }

  return record;
}

async function handleCustomerLookup() {
  addMessage("user", "Show me my account details");
  setIsWaiting(true);

  try {
    const record = await verifyIdentity();
    if (!record) return;

    const historyResult = await lookupCustomerHistory(record.customer_id);
    const history = historyResult.history || [];

    const historyLines = history.length
      ? history
          .map((h) => `• ${h.event_date} — ${h.event_type}: ${h.details}`)
          .join("\n")
      : "No history on file yet.";

    addMessage(
      "agent",
      `Here's what we have on file for you:\n\n` +
        `Name: ${record.name}\n` +
        `Email: ${record.email}\n` +
        `Phone: ${record.phone}\n` +
        `Status: ${record.status}\n` +
        `Last transaction: ${record.last_transaction}\n\n` +
        `Recent history:\n${historyLines}`
    );
  } catch (err) {
    addMessage("agent", "I couldn't retrieve your details right now. Please try again shortly.");
  } finally {
    setIsWaiting(false);
  }
}

async function handleAccountStatus() {
  addMessage("user", "What is my account status?");
  setIsWaiting(true);

  try {
    const record = await verifyIdentity();
    if (!record) return;

    addMessage("agent", `Your account status is: ${record.status}.`);
  } catch (err) {
    addMessage("agent", "I couldn't check your account status right now. Please try again shortly.");
  } finally {
    setIsWaiting(false);
  }
}
  return (
    <div className="page">
      <div className="widget">
        <header className="widget-header">
          <div className="header-title">
            <span className="status-dot" />
            <div>
              <div className="company-name">{COMPANY_NAME}</div>
              <div className="header-subtitle">Support chat</div>
            </div>
          </div>
          <button
            type="button"
            className="identity-toggle"
            onClick={() => setShowIdentity((v) => !v)}
          >
            {showIdentity ? "Hide details" : "Your details"}
          </button>
        </header>

        {showIdentity && (
          <div className="identity-panel">
            <input
              type="text"
              placeholder="Customer ID, email, or phone number"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
            />
            <input
              type="text"
              placeholder="Your name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </div>
        )}

        <div className="messages">
          {messages.map((m) => (
            <Message key={m.id} sender={m.sender} text={m.text} />
          ))}

          {pendingAction === "password_reset_ticket" && (
            <div className="action-row">
              <button className="action-btn primary" onClick={() => handlePasswordResetConfirm(true)}>
                Yes, log a ticket
              </button>
              <button className="action-btn" onClick={() => handlePasswordResetConfirm(false)}>
                No thanks
              </button>
            </div>
          )}

          {isWaiting && <TypingIndicator />}
          <div ref={scrollRef} />
        </div>

        <div className="quick-actions">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.key}
              type="button"
              className="quick-action-btn"
              onClick={() => openLookup(action.key)}
            >
              {action.label}
            </button>
            
          ))}
          <button
            type="button"
            className="quick-action-btn"
            onClick={handleCustomerLookup}
          >
            My account details
          </button>
          <button
            type="button"
            className="quick-action-btn"
            onClick={handleAccountStatus}
          >
            My account status
          </button>
        </div>

        {activeLookup && (
          <form className="lookup-form" onSubmit={handleLookupSubmit}>
            <input
              type="text"
              autoFocus
              placeholder={QUICK_ACTIONS.find((a) => a.key === activeLookup)?.placeholder}
              value={lookupInput}
              onChange={(e) => setLookupInput(e.target.value)}
            />
            <button type="submit">Check</button>
            <button type="button" className="cancel" onClick={() => setActiveLookup(null)}>
              Cancel
            </button>
          </form>
        )}

        <form className="input-row" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isWaiting}
          />
          <button type="submit" disabled={isWaiting || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
