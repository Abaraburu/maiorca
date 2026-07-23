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
                modal.style.display = 'flex';
                modalImg.src = img.src;
                modalCaption.textContent = img.alt || '';
            };
        });
    }

    initLightbox();

    const closeModal = () => {
        modal.style.display = 'none';
    };

    modal.onclick = closeModal;
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
});
