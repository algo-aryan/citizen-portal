document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    const msg = document.getElementById('loader-msg');
    let timerInterval;

    // 1. OTP Auto-tabbing Logic
    const otpBoxes = document.querySelectorAll('.otp-box');
    otpBoxes.forEach((box, index) => {
        box.addEventListener('input', (e) => {
            if (e.target.value.length === 1 && index < otpBoxes.length - 1) {
                otpBoxes[index + 1].focus();
            }
        });
        box.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                otpBoxes[index - 1].focus();
            }
        });
    });

    // 2. Navigation Simulation
    document.getElementById('to-otp-btn').addEventListener('click', () => {
        loader.classList.remove('hidden');
        msg.innerText = "Connecting to DigiLocker...";
        setTimeout(() => {
            loader.classList.add('hidden');
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');
            startTimer();
        }, 2200);
    });

    document.getElementById('to-consent-btn').addEventListener('click', () => {
        loader.classList.remove('hidden');
        msg.innerText = "Verifying OTP...";
        setTimeout(() => {
            clearInterval(timerInterval);
            loader.classList.add('hidden');
            document.getElementById('step-2').classList.add('hidden');
            document.getElementById('step-3').classList.remove('hidden');
        }, 1800);
    });

    // Step 3 Logic
    document.getElementById('allow-btn').addEventListener('click', () => {
        const isChecked = document.getElementById('consent-check').checked;
        if (!isChecked) {
            alert("Please provide your consent to continue.");
            return;
        }

        const loader = document.getElementById('loader');
        const msg = document.getElementById('loader-msg');
        
        loader.classList.remove('hidden');
        msg.innerText = "Processing Consent...";

        setTimeout(() => {
            msg.innerText = "Requesting ECI Database...";
            setTimeout(() => {
                msg.innerText = "Establishing Secure Voter Token...";
                setTimeout(() => {
                    window.location.href = "home.html";
                }, 1800);
            }, 2000);
        }, 1200);
    });

    document.getElementById('deny-btn').addEventListener('click', () => {
        if(confirm("Access is required for verification. Are you sure?")) {
            location.reload();
        }
    });

    function startTimer() {
        let timeLeft = 59;
        const timerElem = document.getElementById('timer');
        timerInterval = setInterval(() => {
            timeLeft--;
            timerElem.innerText = `00:${timeLeft < 10 ? '0' + timeLeft : timeLeft}`;
            if (timeLeft <= 0) clearInterval(timerInterval);
        }, 1000);
    }
});