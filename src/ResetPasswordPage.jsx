import { useState } from "react";
import { confirmPasswordReset } from "./api.js";

export default function ResetPasswordPage() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token") || "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    if (!token) {
      setMessage("This reset link is missing a token. Please request a new one.");
      return;
    }

    if (newPassword.length < 8) {
      setMessage("Password must be at least 8 characters.");
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await confirmPasswordReset(token, newPassword);
      setMessage(result.answer);
      setSuccess(Boolean(result.success));
    } catch (err) {
      setMessage("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page">
      <div className="widget" style={{ height: "auto" }}>
        <header className="widget-header">
          <div className="header-title">
            <span className="status-dot" />
            <div>
              <div className="company-name">ABC Company</div>
              <div className="header-subtitle">Reset your password</div>
            </div>
          </div>
        </header>

        <div style={{ padding: "24px" }}>
          {success ? (
            <p>{message}</p>
          ) : (
            <form
              onSubmit={handleSubmit}
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              <input
                type="password"
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
              />
              <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Resetting..." : "Reset password"}
              </button>
              {message && <p style={{ color: "#e8615a" }}>{message}</p>}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}