/**
 * Sistema di Archiviazione, Ricerca e Filtri per Maiorca
 * Gestisce l'archiviazione locale (localStorage), filtri per categoria, barra di ricerca e schede attive/archivio.
 * Rispetta le regole di progetto: unicamente icone SVG per tutti gli elementi grafici.
 */

(function() {
    const STORAGE_KEY = 'maiorca_archived_places';
    let activeTab = 'explore'; // 'explore' oppure 'archive'
    let currentSearchQuery = '';
    let currentCategoryFilter = 'all';

    // Carica lista ID archiviati
    function getArchivedIds() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Errore nella lettura di localStorage:', e);
            return [];
        }
    }

    // Salva lista ID archiviati
    function saveArchivedIds(ids) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
        } catch (e) {
            console.error('Errore nella scrittura su localStorage:', e);
        }
    }

    // Estrae l'ID univoco dal link (es: "cala_pi.html" -> "cala_pi")
    function getPlaceIdFromElement(el) {
        if (el.dataset.placeId) return el.dataset.placeId;
        const href = el.getAttribute('href');
        if (href) {
            return href.replace('.html', '').replace('./', '').replace('/', '');
        }
        return null;
    }

    // Icone SVG utilizzate
    const SVG_ICONS = {
        explore: `<svg class="tab-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>`,
        archive: `<svg class="tab-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M20.54 5.23l-1.39-1.68C18.88 3.21 18.47 3 18 3H6c-.47 0-.88.21-1.16.55L3.46 5.23C3.17 5.57 3 6.02 3 6.5V19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6.5c0-.48-.17-.93-.46-1.27zM6.24 5h11.52l.83 1H5.41l.83-1zM5 19V8h14v11H5zm11-5.5l-4 4-4-4 1.41-1.41L11 13.67V10h2v3.67l1.59-1.58L16 13.5z"/></svg>`,
        archiveBtn: `<svg class="btn-svg-icon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="currentColor"><path d="M20.54 5.23l-1.39-1.68C18.88 3.21 18.47 3 18 3H6c-.47 0-.88.21-1.16.55L3.46 5.23C3.17 5.57 3 6.02 3 6.5V19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6.5c0-.48-.17-.93-.46-1.27zM6.24 5h11.52l.83 1H5.41l.83-1zM5 19V8h14v11H5zm11-5.5l-4 4-4-4 1.41-1.41L11 13.67V10h2v3.67l1.59-1.58L16 13.5z"/></svg>`,
        restoreBtn: `<svg class="btn-svg-icon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="currentColor"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>`,
        emptyBox: `<svg viewBox="0 0 24 24" width="60" height="60" aria-hidden="true" fill="none" stroke="#94a3b8" stroke-width="1.5"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-14L4 7m8 4v10M4 7v10l8 4"/></svg>`
    };

    function initArchiveSystem() {
        const placesGrid = document.querySelector('.places-grid');
        if (!placesGrid) {
            initDetailPage();
            return;
        }

        const cardLinks = Array.from(placesGrid.querySelectorAll('a[href$=".html"]'));
        if (cardLinks.length === 0) return;

        // Assicura attributo data-place-id e data-category su tutti i link
        cardLinks.forEach(link => {
            const id = getPlaceIdFromElement(link);
            if (id) {
                link.dataset.placeId = id;

                // Trova testo categoria per il filtro
                const categoryEl = link.querySelector('.category-tag, p');
                if (categoryEl) {
                    const catText = categoryEl.textContent.trim().toLowerCase();
                    if (catText.includes('spiaggia')) link.dataset.category = 'spiaggia';
                    else if (catText.includes('borgo') || catText.includes('porto')) link.dataset.category = 'borgo';
                    else if (catText.includes('attrazione') || catText.includes('parco')) link.dataset.category = 'attrazione';
                    else if (catText.includes('mercato')) link.dataset.category = 'mercato';
                    else if (catText.includes('città') || catText.includes('citta')) link.dataset.category = 'citta';
                    else if (catText.includes('panorami') || catText.includes('panoramico')) link.dataset.category = 'panorami';
                    else if (catText.includes('evento') || catText.includes('esperienza')) link.dataset.category = 'esperienza';
                    else link.dataset.category = 'altro';
                }


            }
        });

        // Event listener per barra di ricerca
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                currentSearchQuery = e.target.value.toLowerCase().trim();
                renderGrid();
            });
        }

        // Event listener per chip categorie
        const categoryChips = document.getElementById('category-chips');
        if (categoryChips) {
            categoryChips.addEventListener('click', (e) => {
                const btn = e.target.closest('.chip-btn');
                if (btn && btn.dataset.category) {
                    currentCategoryFilter = btn.dataset.category;
                    categoryChips.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    renderGrid();
                }
            });
        }

        // Crea o aggancia i controlli per le schede (Tabs)
        let archiveNav = document.getElementById('archive-nav-tabs');
        if (!archiveNav) {
            archiveNav = document.createElement('div');
            archiveNav.id = 'archive-nav-tabs';
            archiveNav.className = 'archive-nav-tabs';
            archiveNav.innerHTML = `
                <button class="archive-tab-btn active" data-tab="explore" type="button">
                    ${SVG_ICONS.explore}
                    <span>Da Esplorare</span>
                    <span class="tab-badge" id="badge-explore">0</span>
                </button>
                <button class="archive-tab-btn" data-tab="archive" type="button">
                    ${SVG_ICONS.archive}
                    <span>Archivio</span>
                    <span class="tab-badge" id="badge-archive">0</span>
                </button>
            `;
            placesGrid.parentNode.insertBefore(archiveNav, placesGrid);

            // Listener cambio tab
            archiveNav.addEventListener('click', (e) => {
                const btn = e.target.closest('.archive-tab-btn');
                if (btn && btn.dataset.tab) {
                    activeTab = btn.dataset.tab;
                    archiveNav.querySelectorAll('.archive-tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    renderGrid();
                }
            });
        }

        // Container per stato vuoto
        let emptyState = document.getElementById('archive-empty-state');
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.id = 'archive-empty-state';
            emptyState.className = 'archive-empty-state';
            emptyState.style.display = 'none';
            placesGrid.parentNode.insertBefore(emptyState, placesGrid.nextSibling);
        }

        renderGrid();
    }

    function toggleArchiveStatus(placeId) {
        let archived = getArchivedIds();
        const index = archived.indexOf(placeId);
        if (index > -1) {
            archived.splice(index, 1);
        } else {
            archived.push(placeId);
        }
        saveArchivedIds(archived);

        const link = document.querySelector(`a[data-place-id="${placeId}"]`);
        if (link) {
            link.classList.add('card-transitioning');
            setTimeout(() => {
                link.classList.remove('card-transitioning');
                renderGrid();
            }, 200);
        } else {
            renderGrid();
        }
    }

    function renderGrid() {
        const archived = getArchivedIds();
        const placesGrid = document.querySelector('.places-grid');
        if (!placesGrid) return;

        const cardLinks = Array.from(placesGrid.querySelectorAll('a[data-place-id]'));
        let visibleCount = 0;
        let exploreCount = 0;
        let archiveCount = 0;

        cardLinks.forEach(link => {
            const id = link.dataset.placeId;
            const isArchived = archived.includes(id);
            const btn = link.querySelector('.place-archive-btn');

            if (isArchived) {
                archiveCount++;
            } else {
                exploreCount++;
            }

            const matchesTab = (activeTab === 'explore' && !isArchived) || (activeTab === 'archive' && isArchived);
            const textContent = link.textContent.toLowerCase();
            const matchesSearch = !currentSearchQuery || textContent.includes(currentSearchQuery);
            const matchesCategory = (currentCategoryFilter === 'all') || (link.dataset.category === currentCategoryFilter);

            const shouldShow = matchesTab && matchesSearch && matchesCategory;

            if (shouldShow) {
                link.style.display = '';
                visibleCount++;
            } else {
                link.style.display = 'none';
            }

            if (btn) {
                if (isArchived) {
                    btn.innerHTML = `${SVG_ICONS.restoreBtn} <span>Ripristina</span>`;
                    btn.title = "Ripristina nella lista attiva";
                    btn.classList.add('is-archived');
                } else {
                    btn.innerHTML = `${SVG_ICONS.archiveBtn} <span>Archivia</span>`;
                    btn.title = "Sposta in Archivio";
                    btn.classList.remove('is-archived');
                }
            }
        });

        const badgeExplore = document.getElementById('badge-explore');
        const badgeArchive = document.getElementById('badge-archive');
        if (badgeExplore) badgeExplore.textContent = exploreCount;
        if (badgeArchive) badgeArchive.textContent = archiveCount;

        const emptyState = document.getElementById('archive-empty-state');
        if (emptyState) {
            if (visibleCount === 0) {
                placesGrid.style.display = 'none';
                emptyState.style.display = 'flex';
                if (currentSearchQuery || currentCategoryFilter !== 'all') {
                    emptyState.innerHTML = `
                        ${SVG_ICONS.emptyBox}
                        <h3>Nessun risultato trovato</h3>
                        <p>Prova a modificare la ricerca o a selezionale un'altra categoria.</p>
                    `;
                } else if (activeTab === 'archive') {
                    emptyState.innerHTML = `
                        ${SVG_ICONS.emptyBox}
                        <h3>L'archivio è vuoto</h3>
                        <p>Non hai ancora archiviato alcuna spiaggia o luogo. Quando trovi posti che non ti interessano, clicca su "Archivia" per nasconderli qui.</p>
                    `;
                } else {
                    emptyState.innerHTML = `
                        ${SVG_ICONS.emptyBox}
                        <h3>Tutti i luoghi sono stati archiviati</h3>
                        <p>Puoi consultare e ripristinare i luoghi archiviati passando alla scheda <strong>Archivio</strong>.</p>
                    `;
                }
            } else {
                placesGrid.style.display = '';
                emptyState.style.display = 'none';
            }
        }
    }

    function initDetailPage() {
        const detailContainer = document.querySelector('.place-details');
        if (!detailContainer) return;

        const path = window.location.pathname;
        const pageName = path.substring(path.lastIndexOf('/') + 1);
        const placeId = pageName.replace('.html', '');
        if (!placeId || pageName === 'index.html') return;

        let actionArea = detailContainer.querySelector('.detail-archive-action');
        if (!actionArea) {
            actionArea = document.createElement('div');
            actionArea.className = 'detail-archive-action';
            detailContainer.insertBefore(actionArea, detailContainer.firstChild);
        }

        function renderDetailAction() {
            const archived = getArchivedIds();
            const isArchived = archived.includes(placeId);

            actionArea.innerHTML = `
                <button type="button" class="detail-archive-btn ${isArchived ? 'is-archived' : ''}">
                    ${isArchived ? SVG_ICONS.restoreBtn : SVG_ICONS.archiveBtn}
                    <span>${isArchived ? 'In Archivio (Ripristina)' : 'Archivia luogo'}</span>
                </button>
            `;

            const btn = actionArea.querySelector('button');
            btn.addEventListener('click', () => {
                toggleArchiveStatus(placeId);
                renderDetailAction();
            });
        }

        renderDetailAction();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initArchiveSystem);
    } else {
        initArchiveSystem();
    }
})();
