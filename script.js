document.addEventListener('DOMContentLoaded', () => {
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
