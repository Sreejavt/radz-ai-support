import React, { useEffect, useState } from "react";
import "./HelpCentre.css";
import { getHelpCentreDocs } from "./api.js";

export default function HelpCentre({ onOpenSupport }) {
  const [docs, setDocs] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDocs() {
      try {
        const data = await getHelpCentreDocs();
        setDocs(data);
      } catch (err) {
        setError("Unable to load Help Centre documentation.");
      } finally {
        setLoading(false);
      }
    }

    loadDocs();
  }, []);

  const filteredTopics = docs.filter((topic) => {
    const searchableText = [
      topic.title,
      topic.summary,
      ...topic.articles.map(
        (article) => `${article.title} ${article.content}`
      )
    ]
      .join(" ")
      .toLowerCase();

    return searchableText.includes(searchTerm.toLowerCase());
  });

  function openTopic(topic) {
    setSelectedTopic(topic);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function backToTopics() {
    setSelectedTopic(null);
  }

  return (
    <div className="help-page">
      <header className="help-header">
        <div className="container nav">
          <div className="brand">ABC COMPANY</div>

          <nav>
            <a href="#help">Help Centre</a>
            <a href="#topics">Help Topics</a>
          </nav>
        </div>
      </header>

      <main id="help">
        {!selectedTopic ? (
          <>
            <section className="hero container">
              <p className="eyebrow">SUPPORT</p>

              <h1>How can we help you?</h1>

              <p className="hero-copy">
                Get quick answers to questions about your account, orders,
                payments, refunds, and more.
              </p>

              <div className="search-box">
                <span>⌕</span>

                <input
                  type="text"
                  placeholder="Search for help"
                  aria-label="Search for help"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </section>

            <section id="topics" className="topics container">
              <p className="eyebrow">HELP TOPICS</p>

              <h2>Browse help topics</h2>

              {loading && <p>Loading help topics...</p>}

              {error && <p>{error}</p>}

              {!loading && !error && (
                <div className="topic-grid">
                  {filteredTopics.map((topic) => (
                    <button
                      className="topic-card"
                      key={topic.id}
                      onClick={() => openTopic(topic)}
                    >
                      <span className="topic-icon">{topic.icon}</span>

                      <span className="topic-content">
                        <strong>{topic.title}</strong>
                        <span>{topic.summary}</span>
                      </span>

                      <span className="arrow">→</span>
                    </button>
                  ))}

                  {filteredTopics.length === 0 && (
                    <p className="no-results">
                      No help topics found. Try another search.
                    </p>
                  )}
                </div>
              )}
            </section>

            <section className="support-banner container">
              <div>
                <p className="eyebrow">NEED HELP?</p>

                <h2>Our Support Assistant is available to help.</h2>

                <p>
                  Ask a question and get assistance with your request.
                </p>
              </div>

              <button onClick={onOpenSupport}>
                Open Support
              </button>
            </section>
          </>
        ) : (
          <section className="documentation container">
            <button
              type="button"
              className="back-button"
              onClick={backToTopics}
            >
              ← Back to Help Topics
            </button>

            <p className="eyebrow">HELP CENTRE</p>

            <h1>{selectedTopic.title}</h1>

            <p className="hero-copy">
              {selectedTopic.summary}
            </p>

            <div className="article-list">
              {selectedTopic.articles.map((article) => (
                <article className="help-article" key={article.title}>
                  <h2>{article.title}</h2>
                  <p>{article.content}</p>
                </article>
              ))}
            </div>

            <div className="documentation-support">
              <h2>Still need help?</h2>

              <p>
                Our Support Assistant can help with your request.
              </p>

              <button onClick={onOpenSupport}>
                Open Support Assistant
              </button>
            </div>
          </section>
        )}
      </main>

      <button
        className="support-widget"
        onClick={onOpenSupport}
        aria-label="Open customer support"
      >
        <span className="widget-dot" />
        ✦
      </button>

      <footer className="footer">
        <div className="container">
          © 2026 ABC Company · Help Centre
        </div>
      </footer>
    </div>
  );
}