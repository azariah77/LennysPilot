document.addEventListener("DOMContentLoaded", () => {
    // 1. Loading Overlay Logic
    const overlay = document.getElementById("loading-overlay");
    const video = document.getElementById("loading-video");
    
    // Play video and set 3 second timeout
    setTimeout(() => {
        overlay.classList.add("fade-out");
        setTimeout(() => {
            overlay.style.display = "none";
            video.pause();
        }, 500); // match CSS transition duration
    }, 3000);

    // 2. Chat Logic
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const history = document.getElementById("chat-history");
    const sendBtn = document.getElementById("send-button");
    const artifactSection = document.getElementById("artifact-section");
    const artifactIframe = document.getElementById("artifact-iframe");

    let currentSessionId = null;

    // Auto-resize textarea
    input.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    input.addEventListener("keydown", function(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            form.dispatchEvent(new Event("submit"));
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Reset input
        input.value = "";
        input.style.height = "auto";
        sendBtn.disabled = true;

        // Hide empty state if present
        const emptyState = document.getElementById("empty-state");
        if (emptyState) {
            emptyState.style.display = "none";
        }

        // Ensure session
        if (!currentSessionId) {
            try {
                const res = await fetch("/sessions", { method: "POST" });
                const data = await res.json();
                currentSessionId = data.session_id;
            } catch (err) {
                console.error("Failed to create session", err);
                sendBtn.disabled = false;
                return;
            }
        }

        // Add user message
        appendMessage("user", text);

        // Add loading state
        const loadingId = "loading-" + Date.now();
        appendMessage("assistant", "...", loadingId);

        try {
            const res = await fetch(`/sessions/${currentSessionId}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            
            // Remove loading
            document.getElementById(loadingId).remove();
            
            // Render response
            renderAssistantResponse(data.response);
            
        } catch (err) {
            console.error("Chat error", err);
            document.getElementById(loadingId).innerText = "An error occurred.";
        }

        sendBtn.disabled = false;
        history.scrollTop = history.scrollHeight;
    });

    function appendMessage(role, text, id = null) {
        const div = document.createElement("div");
        div.className = `message ${role}-message`;
        if (id) div.id = id;
        
        const content = document.createElement("div");
        content.className = "message-content";
        
        // Simple text replace for newlines
        content.innerHTML = text.replace(/\n/g, "<br>");
        
        div.appendChild(content);
        history.appendChild(div);
        history.scrollTop = history.scrollHeight;
    }

    function renderAssistantResponse(text) {
        // Check if there's an artifact link like [View Artifact 123](/artifacts/123)
        const artifactRegex = /\[(.*?)\]\((\/artifacts\/.*?)\)/g;
        let match;
        let hasArtifact = false;
        
        const parsedText = text.replace(artifactRegex, (m, label, url) => {
            hasArtifact = true;
            return `<a href="#" onclick="openArtifact('${url}'); return false;">${label}</a>`;
        });
        
        appendMessage("assistant", parsedText);
        
        // If it was an explicit artifact generation, auto-open it
        if (hasArtifact) {
            const urlMatch = text.match(/\/artifacts\/[a-zA-Z0-9\-]+/);
            if (urlMatch) {
                openArtifact(urlMatch[0]);
            }
        }
    }

    // 3. Artifact Logic
    window.openArtifact = function(url) {
        artifactIframe.src = url;
        artifactSection.classList.remove("hidden");
        // Shrink chat width slightly to accommodate
        document.getElementById("chat-section").style.maxWidth = "100%";
    };

    window.closeArtifact = function() {
        artifactSection.classList.add("hidden");
        artifactIframe.src = "about:blank";
        document.getElementById("chat-section").style.maxWidth = "800px";
    };

    window.startNewSession = function() {
        currentSessionId = null;
        history.innerHTML = "";
        const emptyState = document.getElementById("empty-state");
        if (emptyState) {
            emptyState.style.display = "flex";
        }
        closeArtifact();
    };
});
