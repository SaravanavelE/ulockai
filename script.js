document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Switcher Logic ---
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const navLogo = document.getElementById('nav-logo');
    const footerLogo = document.getElementById('footer-logo');
    const favicon = document.getElementById('favicon');
    const heroLogo = document.getElementById('hero-logo');

    const moonPath = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    const sunPath = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (theme === 'light') {
            themeIcon.innerHTML = moonPath;
            navLogo.src = 'light.png';
            footerLogo.src = 'light.png';
            heroLogo.src = 'light.png';
            favicon.href = 'web small logo.png';
        } else {
            themeIcon.innerHTML = sunPath;
            navLogo.src = 'dark.png';
            footerLogo.src = 'dark.png';
            heroLogo.src = 'dark.png';
            favicon.href = 'web small logo.png';
        }
    }

    // Toggle theme
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    // Initialize theme
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    setTheme(savedTheme);

    // --- Original Logic ---
    // Copy to Clipboard Functionality
    const copyBtn = document.getElementById('copy-btn');
    const installCommand = document.getElementById('install-command');

    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const command = installCommand.innerText;
            navigator.clipboard.writeText(command).then(() => {
                // Change icon to checkmark for 2 seconds
                const originalIcon = copyBtn.innerHTML;
                copyBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>`;
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalIcon;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    }

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Add fadeIn triggers to sections/cards
    document.querySelectorAll('.card, .feature-item, .section-header, .visual-content, .code-showcase').forEach(el => {
        el.classList.add('fade-in-trigger');
        observer.observe(el);
    });

    // Simple smooth scroll for nav links (handled by CSS, but extra JS as progressive enhancement)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const navHeight = 70;
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navHeight;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});
