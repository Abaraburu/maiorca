document.addEventListener('DOMContentLoaded', () => {
    // Create Lightbox Modal DOM structure if not present
    let modal = document.getElementById('lightbox-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'lightbox-modal';
        modal.className = 'lightbox-modal';
        modal.innerHTML = `
            <span class="lightbox-close">&times;</span>
            <img class="lightbox-content" id="lightbox-img" src="" alt="Foto a schermo intero">
            <div class="lightbox-caption" id="lightbox-caption"></div>
        `;
        document.body.appendChild(modal);
    }

    const modalImg = document.getElementById('lightbox-img');
    const modalCaption = document.getElementById('lightbox-caption');

    // Attach click listeners to all gallery and preview images
    function initLightbox() {
        const images = document.querySelectorAll('.gallery-img, .lightbox-trigger, .tiktok-ref-media img');
        images.forEach(img => {
            img.style.cursor = 'zoom-in';
            img.onclick = (e) => {
                e.stopPropagation();
                e.preventDefault();
                modal.style.display = 'flex';
                modalImg.src = img.src;
                modalCaption.textContent = img.alt || '';
                // Prevent body scroll while lightbox is open (mobile)
                document.body.style.overflow = 'hidden';
            };
        });
    }

    initLightbox();

    const closeModal = () => {
        modal.style.display = 'none';
        // Restore body scroll
        document.body.style.overflow = '';
    };

    // Close on tapping the backdrop (not the image)
    modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.classList.contains('lightbox-close')) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Swipe down to close (mobile gesture)
    let touchStartY = 0;
    modal.addEventListener('touchstart', (e) => {
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    modal.addEventListener('touchend', (e) => {
        const touchEndY = e.changedTouches[0].screenY;
        const swipeDistance = touchEndY - touchStartY;
        // Close if swiped down more than 80px
        if (swipeDistance > 80) {
            closeModal();
        }
    }, { passive: true });
});
