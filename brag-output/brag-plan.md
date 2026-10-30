# Brag plan: Enterprise IT Support Agentic RAG Copilot

## 9-question rubric

1. **What is the app?** An IT support copilot that routes questions, searches a private company knowledge base first, judges evidence, and uses public web search when internal evidence is insufficient.
2. **Strongest claim:** “Private company knowledge first. Public web is used only when private evidence is weak.” (Product UI copy.)
3. **Visual hook:** The three-panel dark support interface, especially the live Agent Pipeline beside the chat.
4. **Show:** The actual chat prompt and Agent Pipeline labels from `templates/index.html`, with the project’s documented VPN and current-vendor examples.
5. **Shortest satisfying length:** 20 seconds; enough to show both the private-KB path and the web fallback.
6. **Tone:** Polished; a quiet, confident enterprise product film with clear, deliberate motion.
7. **Audio:** Warm, upbeat instrumental bed; sparse UI click and soft reveal accents. No voiceover.
8. **Share caption:** “Enterprise IT support that checks the company knowledge base first, then turns to the public web only when the evidence calls for it.”
9. **User flow:** Ask an IT question → route and retrieve private evidence → grade it → answer with citations, or fall back to web search when the KB is weak.

## Creative angle

An IT answer should show its work. The film starts with a familiar VPN question, follows the copilot through its private knowledge path, then changes to a timely vendor question to show the evidence gate sending only the weak case to the web. The actual product interface and its real pipeline labels carry the story.

## Storyboard (20 seconds, 1920×1080, 30 fps)

| Time | Beat | Picture and on-screen copy | Sound |
|---|---|---|---|
| 0.00–2.12 | Hook | Dark UI stage resolves into the actual chat and pipeline. Title: “IT answers should show their work.” | Music opens; one restrained click. |
| 2.12–5.80 | Ask | Actual example question enters the real chat: “How do I connect to the company VPN?” Route → Retrieve. | Typing is represented visually, no voice. |
| 5.80–9.50 | Private evidence | Grade lands “GOOD”; answer panel states “Based on the company knowledge base” with a private source chip. | Soft reveal on the 5.80 s strong cue. |
| 9.50–13.18 | Evidence gate | The documented current Teams outage question appears; KB grade is weak, then Web Fallback → DuckDuckGo. | A single low-risk UI switch accent. |
| 13.18–17.91 | Grounded result | Web evidence is graded, rewritten/retried if needed, and the answer carries the project’s external-information caution. | Music continues; no invented speed or accuracy claims. |
| 17.91–20.00 | Payoff | Product lockup and line: “Private knowledge first. Web when needed.” | Music resolves; one soft impact. |

## Guardrails

- All feature names and behavior come from `README.md`, `templates/index.html`, and `app/rag/workflow.py`.
- Use the UI’s existing labels and colors; do not show secrets, personal data, API keys, or real customer information.
- The two support questions are the documented sample prompts. The private sample scenario is fictional.
- The video is a product overview, not a claim that an actual live API response was recorded.
