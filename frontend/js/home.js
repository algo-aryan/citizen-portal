document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Side Drawer (Hamburger) Logic ---
    const menuBtn = document.getElementById('menu-btn');
    const drawer = document.getElementById('side-drawer');
    const backdrop = document.querySelector('.drawer-backdrop');
    const logoutBtn = document.getElementById('logout-btn');

    function toggleDrawer() {
        // Remove the utility hidden class if it exists
        if (drawer.classList.contains('hidden')) {
            drawer.classList.remove('hidden');
        }
        // Toggle the active animation class
        drawer.classList.toggle('active');
    }

    if(menuBtn) menuBtn.addEventListener('click', toggleDrawer);
    if(backdrop) backdrop.addEventListener('click', toggleDrawer);

    if (logoutBtn) logoutBtn.addEventListener('click', () => {
        if(confirm("Are you sure you want to log out?")) {
            window.location.href = "login.html";
        }
    });

    // --- 2. FAQ Accordion Logic ---
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            faqItems.forEach(other => {
                if(other !== item) other.classList.remove('active');
            });
            item.classList.toggle('active');
        });
    });

    // --- 3. Carousel Auto-Scroll Logic ---
    // --- 3. Carousel Logic (With Dots) ---
    const track = document.getElementById('carousel-track');
    const dotsContainer = document.getElementById('carousel-dots');
    const slides = document.querySelectorAll('.slide');
    
    if (track && slides.length > 0) {
        
        // 1. Generate Dots
        slides.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (index === 0) dot.classList.add('active');
            dotsContainer.appendChild(dot);
        });

        const dots = document.querySelectorAll('.dot');

        // 2. Update Dots on Scroll
        track.addEventListener('scroll', () => {
            const slideWidth = slides[0].getBoundingClientRect().width;
            // Calculate which slide index is mostly visible
            const scrollIndex = Math.round(track.scrollLeft / slideWidth);
            
            dots.forEach((d, i) => {
                if (i === scrollIndex) d.classList.add('active');
                else d.classList.remove('active');
            });
        });

        // 3. Auto-Scroll
        let currentIndex = 0;
        const totalSlides = slides.length;
        const gap = 15; // Must match CSS gap

        setInterval(() => {
            // Only auto-scroll if user isn't touching (optional refinement, but simple for now)
            currentIndex = (currentIndex + 1) % totalSlides;
            const slideWidth = slides[0].getBoundingClientRect().width;
            const scrollPosition = (slideWidth + gap) * currentIndex;

            track.scrollTo({
                left: scrollPosition,
                behavior: 'smooth'
            });
        }, 4000);
    }

    // --- 4. Dock Active State ---
    const dockItems = document.querySelectorAll('.dock-item');
    dockItems.forEach(item => {
        item.addEventListener('click', (e) => {
            dockItems.forEach(d => d.classList.remove('active'));
            if(!item.classList.contains('onoe-big')) {
                item.classList.add('active');
            }
        });
    });
});