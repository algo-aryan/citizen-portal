(function() {
    // 1. Inject High-Fidelity Styles (No changes here)
    const style = document.createElement('style');
    style.innerHTML = `
        #citizen-bot-wrapper {
            position: fixed; bottom: 25px; right: 25px;
            z-index: 10000; font-family: 'Inter', sans-serif;
        }
        #bot-trigger {
            width: 54px; height: 54px; 
            background: #3498db; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            cursor: pointer; box-shadow: 0 6px 16px rgba(0,0,0,0.15);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #bot-trigger:hover { transform: scale(1.1); background: #2980b9; }
        #bot-window {
            position: absolute; bottom: 70px; right: 0;
            width: 315px; height: 430px;
            background: #fff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            display: none; flex-direction: column; overflow: hidden;
            animation: botFade 0.3s ease;
        }
        @media (max-width: 600px) { #bot-window { position: fixed; bottom: 90px; left: 15px; right: 15px; width: auto; height: 60vh; } }
        @keyframes botFade { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        .bot-header { background: #002D58; color: white; padding: 16px; display: flex; justify-content: space-between; align-items: center; }
        .bot-header h4 { font-size: 13px; margin: 0; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
        #bot-messages { flex: 1; padding: 15px; overflow-y: auto; background: #fcfcfc; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 85%; padding: 12px 14px; border-radius: 14px; font-size: 13px; line-height: 1.5; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .msg.bot { background: #fff; color: #2c3e50; align-self: flex-start; border: 1px solid #edf2f7; border-bottom-left-radius: 2px; }
        .msg.user { background: #002D58; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .typing { display: flex; gap: 4px; padding: 12px; background: #fff; border: 1px solid #edf2f7; border-radius: 12px; align-self: flex-start; }
        .dot { width: 5px; height: 5px; background: #3498db; border-radius: 50%; animation: wavy 1.3s infinite; }
        .dot:nth-child(2) { animation-delay: 0.15s; }
        .dot:nth-child(3) { animation-delay: 0.3s; }
        @keyframes wavy { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-5px); } }
        #bot-suggestions { padding: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #f8fafc; border-top: 1px solid #eee; }
        .chip { background: #fff; border: 1px solid #e2e8f0; color: #002D58; padding: 12px 8px; border-radius: 10px; font-size: 10px; font-weight: 800; text-align: center; cursor: pointer; transition: all 0.2s; line-height: 1.3; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .chip:hover { border-color: #3498db; color: #3498db; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
        .bot-input { padding: 12px; border-top: 1px solid #eee; display: flex; gap: 8px; background: #fff; }
        .bot-input input { flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 13.5px; outline: none; transition: 0.2s; }
        .bot-input input:focus { border-color: #3498db; }
    `;
    document.head.appendChild(style);

    // 2. HTML Structure (Strictly same)
    const botHTML = `
    <div id="citizen-bot-wrapper">
        <div id="bot-window">
            <div class="bot-header">
                <div><h4>CITIZEN ASSIST</h4></div>
                <span style="cursor:pointer; font-size:18px; opacity:0.7;" onclick="toggleBot()">✕</span>
            </div>
            <div id="bot-messages">
                <div class="msg bot">
                    <strong>Namaste!</strong> 🇮🇳<br>
                    I am your digital guide to the Indian Democratic process. How can I assist your journey as a citizen today?
                </div>
            </div>
            <div id="bot-suggestions">
                <div class="chip" onclick="handleChip('How do I register to vote?')">VOTER<br>ENROLLMENT</div>
                <div class="chip" onclick="handleChip('Who is the current PM?')">GOVERNMENT<br>HIERARCHY</div>
                <div class="chip" onclick="handleChip('One Nation One Election?')">O.N.O.E.<br>INSIGHTS</div>
                <div class="chip" onclick="handleChip('Next General Election?')">UPCOMING<br>SCHEDULE</div>
            </div>
            <div class="bot-input">
                <input type="text" id="bot-query" placeholder="Ask about elections or policy...">
                <button onclick="userSend()" style="background:#002D58; color:white; border:none; border-radius:8px; padding:0 14px; cursor:pointer;">➔</button>
            </div>
        </div>
        <div id="bot-trigger" onclick="toggleBot()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', botHTML);

    // 3. Logic: All functions bound to window to ensure HTML attributes work
    window.toggleBot = () => {
        const win = document.getElementById('bot-window');
        win.style.display = (win.style.display === 'flex') ? 'none' : 'flex';
    };

    window.handleChip = (text) => {
        document.getElementById('bot-query').value = text;
        window.userSend();
    };

    window.userSend = async () => {
        const input = document.getElementById('bot-query');
        const container = document.getElementById('bot-messages');
        const val = input.value.trim();
        if(!val) return;

        // UI: Add User Message
        container.innerHTML += `<div class="msg user">${val}</div>`;
        input.value = '';
        container.scrollTop = container.scrollHeight;

        // UI: Add Thinking Animation
        const thinkingId = 'thinking-' + Date.now();
        container.innerHTML += `
            <div class="typing" id="${thinkingId}">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>`;
        container.scrollTop = container.scrollHeight;

        try {
            // REAL BACKEND CALL
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: val })
            });

            const data = await response.json();
            
            const thinkingEl = document.getElementById(thinkingId);
            if(thinkingEl) thinkingEl.remove();

            // Append response from Python/Gemini
            container.innerHTML += `<div class="msg bot">${data.reply}</div>`;
            
        } catch (error) {
            const thinkingEl = document.getElementById(thinkingId);
            if(thinkingEl) thinkingEl.remove();
            container.innerHTML += `<div class="msg bot"><strong>Error:</strong> Backend unreachable. Please start your Python server.</div>`;
        }
        
        container.scrollTop = container.scrollHeight;
    };

    document.addEventListener('keypress', (e) => {
        if(e.which === 13 && document.activeElement.id === 'bot-query') window.userSend();
    });
})();