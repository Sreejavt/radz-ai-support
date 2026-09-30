import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import ResetPasswordPage from "./ResetPasswordPage.jsx";
import "./index.css";

const path = window.location.pathname;
const RootComponent = path === "/reset-password" ? ResetPasswordPage : App;

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RootComponent />
  </React.StrictMode>
);
