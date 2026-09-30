import { useState } from "react";
import HelpCentre from "./HelpCentre";
import SupportAgent from "./SupportAgent";

function App() {
  const [supportOpen, setSupportOpen] = useState(false);

  const openSupport = () => {
    setSupportOpen(true);
  };

  const closeSupport = () => {
    setSupportOpen(false);
  };

  return (
    <>
      <HelpCentre onOpenSupport={openSupport} />

      {supportOpen && (
        <div className="support-agent-overlay">
          <div className="support-agent-panel">
            <button
              type="button"
              className="support-agent-close"
              onClick={closeSupport}
              aria-label="Close support"
            >
              ×
            </button>

            <SupportAgent />
          </div>
        </div>
      )}
    </>
  );
}

export default App;