/* ===== ONOE VOTING SIMULATOR — ADVANCED LAYOUT LOGIC ===== */ 

function playBeep() {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return; 
    
    const audioCtx = new AudioContext();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(950, audioCtx.currentTime); 
    
    gainNode.gain.setValueAtTime(1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 1.5);
}

document.addEventListener('DOMContentLoaded', () => { 

    function enforceLandscape() {
        const rotator = document.getElementById('main-rotator');
        const scaleWrapper = document.getElementById('scale-wrapper');
        const navH = 65; 
        const screenW = window.innerWidth;
        const screenH = window.innerHeight;

        const targetW = 1450;
        const targetH = 780; // Height increased for Text Box + Button below

        if (screenH > screenW) {
            // PORTRAIT: Force Landscape orientation underneath the nav
            const availH = screenH - navH;
            
            rotator.style.width = availH + 'px';
            rotator.style.height = screenW + 'px';
            
            rotator.style.top = (navH + availH / 2) + 'px';
            rotator.style.left = (screenW / 2) + 'px';
            rotator.style.transform = 'translate(-50%, -50%) rotate(90deg)';
            
            const scale = Math.min(availH / targetW, screenW / targetH) * 0.95;
            scaleWrapper.style.transform = `scale(${scale})`;
        } else {
            // LANDSCAPE: Native
            const availH = screenH - navH;
            
            rotator.style.width = screenW + 'px';
            rotator.style.height = availH + 'px';
            
            rotator.style.top = (navH + availH / 2) + 'px';
            rotator.style.left = (screenW / 2) + 'px';
            rotator.style.transform = 'translate(-50%, -50%) rotate(0deg)';
            
            const scale = Math.min(screenW / targetW, availH / targetH) * 0.95;
            scaleWrapper.style.transform = `scale(${scale})`;
        }
    }
    
    window.addEventListener('resize', enforceLandscape);
    window.addEventListener('orientationchange', enforceLandscape);
    setTimeout(enforceLandscape, 50);

    const candidates = [ 
        { bu: 1, sl: 1, id: 'bjp', eng: 'A. Sharma', hin: 'BJP - Lotus', sym: '🪷' }, 
        { bu: 1, sl: 2, id: 'inc', eng: 'R. Singh', hin: 'INC - Hand', sym: '✋' }, 
        { bu: 1, sl: 3, id: 'aap', eng: 'S. Yadav', hin: 'AAP - Broom', sym: '🧹' }, 
        { bu: 1, sl: 4, id: 'bsp', eng: 'M. Kumar', hin: 'BSP - Elephant', sym: '🐘' }, 
        { bu: 1, sl: 5, id: 'ncp', eng: 'G. Khan', hin: 'NCP - Clock', sym: '⏰' }, 
        { bu: 1, sl: 6, id: 'sp', eng: 'K. Patel', hin: 'SP - Bicycle', sym: '🚲' }, 
        { bu: 1, sl: 7, id: 'nota1', eng: 'NOTA', hin: '', sym: '' }, 

        { bu: 2, sl: 17, id: 'tmc', eng: 'P. Rai', hin: 'TMC - Flowers', sym: '🌸' }, 
        { bu: 2, sl: 18, id: 'cpi', eng: 'S. Das', hin: 'CPI(M) - Hammer', sym: '🔨' }, 
        { bu: 2, sl: 19, id: 'trs', eng: 'J. Rao', hin: 'TRS/BRS - Car', sym: '🚗' }, 
        { bu: 2, sl: 20, id: 'ysr', eng: 'V. Reddy', hin: 'YSRCP - Fan', sym: '🌀' }, 
        { bu: 2, sl: 21, id: 'rjd', eng: 'R. Sharma', hin: 'RJD - Lamp', sym: '🏮' }, 
        { bu: 2, sl: 22, id: 'sad', eng: 'K. Kaur', hin: 'SAD - Scales', sym: '⚖️' }, 
        { bu: 2, sl: 23, id: 'nota2', eng: 'NOTA', hin: '', sym: '' }, 

        { bu: 3, sl: 33, id: 'tdp', eng: 'S. Naidu', hin: 'TDP - Bicycle', sym: '🚲' }, 
        { bu: 3, sl: 34, id: 'dmk', eng: 'M. Stalin', hin: 'DMK - Sun', sym: '☀️' }, 
        { bu: 3, sl: 35, id: 'jdu', eng: 'A. Prasad', hin: 'JD(U) - Arrow', sym: '🏹' }, 
        { bu: 3, sl: 36, id: 'jmm', eng: 'S. Soreng', hin: 'JMM - Bow/Arrow', sym: '🏹' }, 
        { bu: 3, sl: 37, id: 'rld', eng: 'G. Singh', hin: 'RLD - Pump', sym: '🚰' }, 
        { bu: 3, sl: 38, id: 'ljp', eng: 'LJP', hin: 'Bungalow', sym: '🏠' }, 
        { bu: 3, sl: 39, id: 'nota3', eng: 'NOTA', hin: '', sym: '' }, 
    ]; 

    let currentBU = 1; 
    let busy = false; 

    const cuText = document.getElementById('cu-text'); 
    const vvpatPaper = document.getElementById('vvpat-paper'); 
    const slipSn = document.getElementById('slip-sn'); 
    const slipSym = document.getElementById('slip-sym'); 
    const slipName = document.getElementById('slip-name'); 
    const slipParty = document.getElementById('slip-party'); 
    const instructionText = document.getElementById('instruction-text'); 
    const restartBtn = document.getElementById('restart-btn');

    // Render BUs
    [1, 2, 3].forEach(buNum => { 
        const grid = document.getElementById(`bu${buNum}-grid`); 
        const cands = candidates.filter(c => c.bu === buNum); 
         
        cands.forEach(c => { 
            const isNota = c.eng === 'NOTA'; 
            const rowHtml = ` 
            <div class="bu-row" data-id="${c.id}"> 
                <div class="bu-cell bu-col-sl ${isNota ? 'nota-cell' : ''}" style="${isNota ? 'color:#111' : ''}">${c.sl}</div> 
                <div class="bu-cell bu-col-name ${isNota ? 'nota-cell' : ''}"> 
                    <span class="name-eng">${c.eng}</span> 
                    ${!isNota ? `<span class="name-party">${c.hin}</span>` : ''} 
                </div> 
                <div class="bu-cell bu-col-sym ${isNota ? 'nota-cell' : ''}">${c.sym}</div> 
                <div class="bu-cell bu-col-vote"> 
                    <div class="vote-led" id="led-${c.id}"></div> 
                    <div class="vote-btn" data-id="${c.id}" data-bu="${buNum}">PRESS</div> 
                </div> 
            </div>`; 
            grid.insertAdjacentHTML('beforeend', rowHtml); 
        }); 
    }); 

    // Voting Logic
    document.querySelectorAll('.vote-btn').forEach(btn => { 
        btn.addEventListener('click', function() { 
            if (busy) return; 
            const buNum = parseInt(this.dataset.bu, 10); 
            if (buNum !== currentBU) return; 
             
            busy = true; 
            const cId = this.dataset.id; 
            const cand = candidates.find(c => c.id === cId); 

            playBeep();

            this.classList.add('pressed'); 
            this.textContent = cand.sl; 
            document.getElementById(`led-${cId}`).classList.add('on'); 
            cuText.innerHTML = `VOTE REG<br>BU-${buNum}`; 

            slipSn.textContent = String(Math.floor(Math.random() * 90000) + 10000); 
            slipSym.textContent = cand.sym || '🚫'; 
            slipName.textContent = cand.eng; 
            slipParty.textContent = cand.hin || 'None of the Above'; 
             
            vvpatPaper.classList.remove('show');
            void vvpatPaper.offsetWidth; 
            vvpatPaper.classList.add('show'); 
            instructionText.innerHTML = `Printing VVPAT slip... Please wait.`; 

            setTimeout(() => { 
                document.getElementById(`led-${cId}`).classList.remove('on'); 
                vvpatPaper.classList.remove('show'); 
                 
                document.getElementById(`bu${buNum}`).classList.add('disabled'); 
                document.getElementById(`bled${buNum}`).style.background = '#7a8a9a';

                currentBU++; 
                 
                if (currentBU <= 3) { 
                    document.getElementById(`bu${currentBU}`).classList.remove('disabled'); 
                    document.getElementById(`bled${currentBU}`).style.background = '#3c3'; 
                    cuText.innerHTML = `READY<br>BU-${currentBU} LIVE`; 
                    instructionText.innerHTML = `Press the blue <strong>PRESS</strong> button next to your candidate on Ballot Unit ${currentBU}.`; 
                    busy = false; 
                } else { 
                    cuText.innerHTML = `ALL VOTES<br>RECORDED`; 
                    instructionText.innerHTML = `<strong>Voting Complete!</strong><br>You have successfully cast your ONOE votes.`; 
                    restartBtn.style.display = 'inline-block'; // Show Restart Button
                } 
            }, 5600); 
        }); 
    }); 

    // Reset Logic
    function resetSimulation() {
        if(busy && currentBU <= 3) return; 
        currentBU = 1; 
        busy = false; 
         
        [1, 2, 3].forEach(buNum => { 
            const bu = document.getElementById(`bu${buNum}`); 
            if (buNum === 1) bu.classList.remove('disabled'); 
            else bu.classList.add('disabled'); 

            document.getElementById(`bled${buNum}`).style.background = buNum === 1 ? '#3c3' : '#7a8a9a'; 
        }); 

        document.querySelectorAll('.vote-btn').forEach(btn => { 
            btn.classList.remove('pressed'); 
            btn.textContent = 'PRESS'; 
        }); 
        document.querySelectorAll('.vote-led').forEach(led => led.classList.remove('on')); 

        cuText.innerHTML = `READY<br>ECI 2024`; 
        vvpatPaper.classList.remove('show'); 
        
        restartBtn.style.display = 'none'; // Hide Restart Button
        instructionText.innerHTML = `Click a blue <strong>PRESS</strong> button on the active Ballot Unit.`; 
    }

    document.getElementById('cu-reset').addEventListener('click', resetSimulation);
    document.getElementById('restart-btn').addEventListener('click', resetSimulation);

});