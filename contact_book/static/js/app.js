/**
 * Contacts Application - Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    let state = {
        contacts: [],
        selectedContactId: null,
        filterTab: "all",
        selectedOrg: "all",
        sortBy: "name_asc",
        searchQuery: ""
    };

    // DOM Elements
    const contactsList = document.getElementById("contactsList");
    const contactDetailPanel = document.getElementById("contactDetailPanel");
    const globalSearchInput = document.getElementById("globalSearchInput");
    const searchClearBtn = document.getElementById("searchClearBtn");
    const orgFilterSelect = document.getElementById("orgFilterSelect");
    const sortSelect = document.getElementById("sortSelect");
    const countAll = document.getElementById("countAll");
    const countFavorites = document.getElementById("countFavorites");

    // Header buttons
    const btnOpenAddModal = document.getElementById("btnOpenAddModal");
    const btnEmptyAdd = document.getElementById("btnEmptyAdd");
    const btnExportToggle = document.getElementById("btnExportToggle");
    const exportDropdown = document.getElementById("exportDropdown");
    const btnThemeToggle = document.getElementById("btnThemeToggle");

    // Modals
    const contactModal = document.getElementById("contactModal");
    const contactForm = document.getElementById("contactForm");
    const modalTitle = document.getElementById("modalTitle");
    const contactIdInput = document.getElementById("contactId");
    const orgOptions = document.getElementById("orgOptions");

    const deleteModal = document.getElementById("deleteModal");
    const deleteContactInfo = document.getElementById("deleteContactInfo");
    const btnConfirmDelete = document.getElementById("btnConfirmDelete");
    let contactToDelete = null;

    function getInitials(name) {
        if (!name) return "?";
        const parts = name.trim().split(/\s+/);
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.slice(0, 2).toUpperCase();
    }

    // ----------------------------------------------------
    // Toast Notification
    // ----------------------------------------------------
    function showToast(message, type = "success") {
        const toastContainer = document.getElementById("toastContainer");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.2s ease";
            setTimeout(() => toast.remove(), 200);
        }, 3000);
    }

    // ----------------------------------------------------
    // Fetch Data
    // ----------------------------------------------------
    async function loadData() {
        await Promise.all([fetchStats(), fetchOrganizations(), fetchContacts()]);
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.success) {
                countAll.textContent = data.stats.total;
                countFavorites.textContent = data.stats.favorites;
            }
        } catch (err) {
            console.error("Failed to load statistics:", err);
        }
    }

    async function fetchOrganizations() {
        try {
            const res = await fetch("/api/organizations");
            const data = await res.json();
            if (data.success) {
                const currentVal = orgFilterSelect.value;
                orgFilterSelect.innerHTML = `<option value="all">All Companies</option>`;
                orgOptions.innerHTML = "";
                data.organizations.forEach(org => {
                    const opt = document.createElement("option");
                    opt.value = org;
                    opt.textContent = org;
                    orgFilterSelect.appendChild(opt);

                    const dlOpt = document.createElement("option");
                    dlOpt.value = org;
                    orgOptions.appendChild(dlOpt);
                });
                orgFilterSelect.value = currentVal || "all";
            }
        } catch (err) {
            console.error("Failed to load organizations:", err);
        }
    }

    async function fetchContacts() {
        contactsList.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading directory...</p>
            </div>
        `;

        try {
            const url = new URL("/api/contacts", window.location.origin);
            url.searchParams.set("sort_by", state.sortBy);
            url.searchParams.set("favorite_only", state.filterTab === "favorites");
            url.searchParams.set("organization", state.selectedOrg);
            if (state.searchQuery) {
                url.searchParams.set("search", state.searchQuery);
            }

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                state.contacts = data.contacts;
                renderContactsList(data.contacts);

                if (data.contacts.length > 0) {
                    const exists = data.contacts.some(c => c.id === state.selectedContactId);
                    if (!exists) {
                        selectContact(data.contacts[0].id);
                    }
                } else {
                    state.selectedContactId = null;
                    renderEmptyDetail();
                }
            } else {
                contactsList.innerHTML = `<div class="empty-state">Error: ${data.error}</div>`;
            }
        } catch (err) {
            console.error("Failed to fetch contacts:", err);
            contactsList.innerHTML = `<div class="empty-state">Connection error.</div>`;
        }
    }

    // ----------------------------------------------------
    // Render Contacts List
    // ----------------------------------------------------
    function renderContactsList(contacts) {
        if (!contacts || contacts.length === 0) {
            contactsList.innerHTML = `
                <div class="empty-state">
                    <p>No contacts found.</p>
                </div>
            `;
            return;
        }

        contactsList.innerHTML = "";
        contacts.forEach(c => {
            const row = document.createElement("div");
            row.className = `contact-row ${c.id === state.selectedContactId ? 'active' : ''}`;
            row.setAttribute("data-id", c.id);

            row.innerHTML = `
                <div class="avatar-initials">${getInitials(c.name)}</div>
                <div class="contact-row-info">
                    <div class="contact-row-name">${escapeHtml(c.name)}</div>
                    <div class="contact-row-sub">${c.organization ? escapeHtml(c.organization) : escapeHtml(c.mobile)}</div>
                </div>
                <button class="star-toggle-btn ${c.is_favorite ? 'active' : ''}" title="Favorite" data-id="${c.id}" aria-label="Toggle favorite">
                    ★
                </button>
            `;

            row.addEventListener("click", () => selectContact(c.id));

            const starBtn = row.querySelector(".star-toggle-btn");
            starBtn.addEventListener("click", async (e) => {
                e.stopPropagation();
                await toggleFavorite(c.id);
            });

            contactsList.appendChild(row);
        });
    }

    function selectContact(id) {
        state.selectedContactId = id;

        contactsList.querySelectorAll(".contact-row").forEach(row => {
            if (parseInt(row.getAttribute("data-id")) === id) {
                row.classList.add("active");
            } else {
                row.classList.remove("active");
            }
        });

        const contact = state.contacts.find(c => c.id === id);
        if (contact) {
            renderContactDetail(contact);
        } else {
            renderEmptyDetail();
        }
    }

    // ----------------------------------------------------
    // Render Profile Detail View
    // ----------------------------------------------------
    function renderEmptyDetail() {
        contactDetailPanel.innerHTML = `
            <div class="empty-selection">
                <div class="empty-icon">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 8v4"></path>
                        <path d="M12 16h.01"></path>
                    </svg>
                </div>
                <h3>No contact selected</h3>
                <p>Select a contact from the list on the left to view details.</p>
                <button class="btn btn-secondary" id="btnEmptyAddInner">Create new contact</button>
            </div>
        `;
        const btn = document.getElementById("btnEmptyAddInner");
        if (btn) btn.addEventListener("click", openAddModal);
    }

    function renderContactDetail(c) {
        const initials = getInitials(c.name);

        const emailAction = c.email ? `
            <a href="mailto:${encodeURIComponent(c.email)}" class="action-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
                <span>Email</span>
            </a>
        ` : '';

        const callAction = `
            <a href="${toTelHref(c.mobile)}" class="action-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                <span>Call</span>
            </a>
        `;

        const mapAction = c.address ? `
            <a href="https://maps.google.com/?q=${encodeURIComponent(c.address)}" target="_blank" rel="noopener noreferrer" class="action-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <span>Directions</span>
            </a>
        ` : '';

        const copyAction = `
            <button class="action-pill" id="btnCopyContact">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                <span>Copy info</span>
            </button>
        `;

        contactDetailPanel.innerHTML = `
            <div class="profile-sheet">
                <div class="profile-sheet-header">
                    <div class="profile-identity">
                        <div class="avatar-large">${initials}</div>
                        <div class="profile-titles">
                            <h2>${escapeHtml(c.name)}</h2>
                            <div class="profile-company">${c.organization ? escapeHtml(c.organization) : 'Individual Contact'}</div>
                        </div>
                    </div>
                    <div class="profile-header-buttons">
                        <button class="star-toggle-btn ${c.is_favorite ? 'active' : ''}" id="btnHeaderStar" style="font-size: 1.25rem;" title="Favorite">
                            ★
                        </button>
                        <button class="btn btn-secondary" id="btnEditContact">Edit</button>
                        <button class="btn btn-secondary" id="btnDeleteContact">Delete</button>
                    </div>
                </div>

                <div class="profile-action-strip">
                    ${callAction}
                    ${emailAction}
                    ${mapAction}
                    ${copyAction}
                </div>

                <div class="profile-details-body">
                    <div class="info-section">
                        <div class="detail-section-title">Contact Details</div>
                        <div class="info-rows">
                            <div class="info-row">
                                <div class="info-row-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                                    </svg>
                                </div>
                                <div class="info-row-data">
                                    <span class="info-row-label">Phone</span>
                                    <span class="info-row-val"><a href="${toTelHref(c.mobile)}">${escapeHtml(c.mobile)}</a></span>
                                </div>
                            </div>

                            <div class="info-row">
                                <div class="info-row-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                        <polyline points="22,6 12,13 2,6"></polyline>
                                    </svg>
                                </div>
                                <div class="info-row-data">
                                    <span class="info-row-label">Email</span>
                                    <span class="info-row-val">${c.email ? `<a href="mailto:${encodeURIComponent(c.email)}">${escapeHtml(c.email)}</a>` : '<span style="color:var(--text-muted)">Not provided</span>'}</span>
                                </div>
                            </div>

                            <div class="info-row">
                                <div class="info-row-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                                        <circle cx="12" cy="10" r="3"></circle>
                                    </svg>
                                </div>
                                <div class="info-row-data">
                                    <span class="info-row-label">Address</span>
                                    <span class="info-row-val">${c.address ? escapeHtml(c.address) : '<span style="color:var(--text-muted)">Not provided</span>'}</span>
                                </div>
                            </div>

                            <div class="info-row">
                                <div class="info-row-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                                        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                                    </svg>
                                </div>
                                <div class="info-row-data">
                                    <span class="info-row-label">Company</span>
                                    <span class="info-row-val">${c.organization ? escapeHtml(c.organization) : '<span style="color:var(--text-muted)">None</span>'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    ${c.notes ? `
                        <div class="info-section">
                            <div class="detail-section-title">Notes</div>
                            <div class="notes-block">${escapeHtml(c.notes)}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.getElementById("btnHeaderStar").addEventListener("click", () => toggleFavorite(c.id));
        document.getElementById("btnEditContact").addEventListener("click", () => openEditModal(c));
        document.getElementById("btnDeleteContact").addEventListener("click", () => openDeleteModal(c));

        document.getElementById("btnCopyContact").addEventListener("click", () => {
            const textToCopy = `${c.name}\n${c.mobile}${c.email ? '\n' + c.email : ''}${c.organization ? '\n' + c.organization : ''}${c.address ? '\n' + c.address : ''}`;
            navigator.clipboard.writeText(textToCopy).then(() => {
                showToast("Contact information copied");
            }).catch(() => {
                showToast("Copied to clipboard");
            });
        });
    }

    // ----------------------------------------------------
    // Favorite Toggle
    // ----------------------------------------------------
    async function toggleFavorite(contactId) {
        try {
            const res = await fetch(`/api/contacts/${contactId}/toggle-favorite`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(data.contact.is_favorite ? "Added to favorites" : "Removed from favorites");
                await Promise.all([fetchStats(), fetchContacts()]);
            }
        } catch (err) {
            console.error("Favorite toggle failed:", err);
            showToast("Server error", "error");
        }
    }

    // ----------------------------------------------------
    // Create / Edit Modal
    // ----------------------------------------------------
    function openAddModal() {
        modalTitle.textContent = "New contact";
        contactForm.reset();
        contactIdInput.value = "";
        openModal(contactModal);
    }

    function openEditModal(c) {
        modalTitle.textContent = `Edit contact`;
        contactIdInput.value = c.id;
        document.getElementById("contactName").value = c.name;
        document.getElementById("contactMobile").value = c.mobile;
        document.getElementById("contactEmail").value = c.email || "";
        document.getElementById("contactOrg").value = c.organization || "";
        document.getElementById("contactAddress").value = c.address || "";
        document.getElementById("contactNotes").value = c.notes || "";
        document.getElementById("contactFavorite").checked = Boolean(c.is_favorite);
        openModal(contactModal);
    }

    contactForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = contactIdInput.value;
        const isEdit = Boolean(id);

        const payload = {
            name: document.getElementById("contactName").value.trim(),
            mobile: document.getElementById("contactMobile").value.trim(),
            email: document.getElementById("contactEmail").value.trim() || null,
            organization: document.getElementById("contactOrg").value.trim() || null,
            address: document.getElementById("contactAddress").value.trim() || null,
            notes: document.getElementById("contactNotes").value.trim() || null,
            is_favorite: document.getElementById("contactFavorite").checked ? 1 : 0
        };

        const saveBtn = document.getElementById("btnSaveContact");
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";

        try {
            const url = isEdit ? `/api/contacts/${id}` : "/api/contacts";
            const method = isEdit ? "PUT" : "POST";

            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.success) {
                showToast(isEdit ? "Contact updated" : "Contact created");
                closeModal(contactModal);
                state.selectedContactId = data.contact.id;
                await Promise.all([fetchStats(), fetchOrganizations(), fetchContacts()]);
                selectContact(data.contact.id);
            } else {
                showToast(data.error || "Save failed", "error");
            }
        } catch (err) {
            console.error("Save contact error:", err);
            showToast("Server error", "error");
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save contact";
        }
    });

    // ----------------------------------------------------
    // Delete Modal
    // ----------------------------------------------------
    function openDeleteModal(contact) {
        contactToDelete = contact;
        deleteContactInfo.textContent = `${contact.name} (${contact.mobile})`;
        openModal(deleteModal);
    }

    btnConfirmDelete.addEventListener("click", async () => {
        if (!contactToDelete) return;
        const id = contactToDelete.id;

        btnConfirmDelete.disabled = true;
        btnConfirmDelete.textContent = "Deleting...";

        try {
            const res = await fetch(`/api/contacts/${id}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                showToast("Contact deleted");
                closeModal(deleteModal);
                contactToDelete = null;
                state.selectedContactId = null;
                await Promise.all([fetchStats(), fetchOrganizations(), fetchContacts()]);
            } else {
                showToast(data.error || "Delete failed", "error");
            }
        } catch (err) {
            console.error("Delete contact error:", err);
            showToast("Server error", "error");
        } finally {
            btnConfirmDelete.disabled = false;
            btnConfirmDelete.textContent = "Delete";
        }
    });

    // ----------------------------------------------------
    // Modal Helpers
    // ----------------------------------------------------
    function openModal(modal) {
        modal.style.display = "flex";
    }

    function closeModal(modal) {
        modal.style.display = "none";
    }

    document.querySelectorAll("[data-close-modal]").forEach(btn => {
        btn.addEventListener("click", () => {
            const m = btn.closest(".modal-backdrop");
            if (m) closeModal(m);
        });
    });

    window.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal-backdrop")) {
            closeModal(e.target);
        }
        if (!e.target.closest(".dropdown-container")) {
            exportDropdown.classList.remove("show");
        }
    });

    // ----------------------------------------------------
    // Search & Filter Events
    // ----------------------------------------------------
    btnOpenAddModal.addEventListener("click", openAddModal);
    if (btnEmptyAdd) btnEmptyAdd.addEventListener("click", openAddModal);

    btnExportToggle.addEventListener("click", (e) => {
        e.stopPropagation();
        exportDropdown.classList.toggle("show");
    });

    let searchDebounce = null;
    globalSearchInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        searchClearBtn.style.display = val ? "block" : "none";
        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(() => {
            state.searchQuery = val;
            fetchContacts();
        }, 150);
    });

    searchClearBtn.addEventListener("click", () => {
        globalSearchInput.value = "";
        searchClearBtn.style.display = "none";
        state.searchQuery = "";
        fetchContacts();
    });

    document.querySelectorAll(".segment-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".segment-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            state.filterTab = tab.getAttribute("data-filter");
            fetchContacts();
        });
    });

    orgFilterSelect.addEventListener("change", (e) => {
        state.selectedOrg = e.target.value;
        fetchContacts();
    });

    sortSelect.addEventListener("change", (e) => {
        state.sortBy = e.target.value;
        fetchContacts();
    });

    // Theme toggle
    btnThemeToggle.addEventListener("click", () => {
        document.body.classList.toggle("theme-dark");
        const isDark = document.body.classList.contains("theme-dark");
        localStorage.setItem("contacts-theme", isDark ? "dark" : "light");
    });

    if (localStorage.getItem("contacts-theme") === "dark") {
        document.body.classList.add("theme-dark");
    }

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".modal-backdrop").forEach(m => closeModal(m));
            exportDropdown.classList.remove("show");
        }
    });

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Normalize a phone number for a tel: URI.
    // Keeps the leading '+' and all digits; strips spaces, dashes, parentheses, etc.
    // This prevents encodeURIComponent from turning the space in "+91 88..."
    // into %20, which WhatsApp misreads as +291.
    function toTelHref(phone) {
        if (!phone) return "";
        const cleaned = String(phone).replace(/[^\d+]/g, "");
        return "tel:" + cleaned;
    }

    // Initial load
    loadData();
});
