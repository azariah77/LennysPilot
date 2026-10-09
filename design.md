# Design Principles

## Aesthetic Philosophy
The UI for The Lenny Growth Assistant is built on a philosophy of "Classic Flat Elegance." We explicitly rejected the modern trend of generic AI aesthetics (no glowing orbs, no glassmorphism, no transparent gradients). 

### 1. Color Palette
- **Main Background:** Deep solid dark (`#121212`).
- **Sidebar:** Flat grey (`#1e1e1e`).
- **Input Form:** Flat dark grey (`#1a1a1a`) with a crisp, subtle 1px border (`#333333`).
- **Constraint:** Absolutely zero use of `opacity` or `rgba` for structural elements. Colors are full-blown and solid to project a premium, grounded feel.

### 2. Typography Strategy (The "Claude" Replica)
We utilize a dual-font strategy to balance readability with application usability:
- **Serif (Merriweather):** Used exclusively for the actual conversational content (chat messages, agent responses) and the main branding. This evokes a high-quality editorial feel, matching the "Ship 30 for 30" writing use-case.
- **Sans-Serif (Inter):** Used for all structural UI elements (sidebar navigation, input placeholders, headers). This ensures the application frame remains clean and modern.

### 3. Interaction & States
- **Loading:** A pure black full-screen overlay playing the `opening.mp4` video (scaled cleanly via `object-fit: contain`). It fades smoothly after exactly 3 seconds to reveal the workspace.
- **Icons:** We use Lucide icons (minimalist, consistent stroke width). Emojis are strictly banned from the UI to maintain professionalism.
- **Artifacts:** When the agent generates a large document, the UI seamlessly splits into a side-by-side view, loading the artifact in an iframe without disrupting the chat context.

### 4. Responsiveness
The layout is built with CSS Flexbox. On mobile devices (`max-width: 1024px`), the sidebar collapses cleanly off-screen, and the artifact viewer takes absolute priority over the chat when opened, ensuring a focused reading experience on small screens.
