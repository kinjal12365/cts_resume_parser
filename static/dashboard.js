/**
 * ==============================================================================
 * Resume Parser Dashboard Script
 * ==============================================================================
 * This script powers the admin dashboard, handling data fetching, filtering,
 * sorting, pagination, and interactions for the candidate management UI.
 * ==============================================================================
 */

// --- STATE MANAGEMENT ---
let masterCandidatesData = [];
let filteredCandidatesData = [];
let currentPage = 1;
const ITEMS_PER_PAGE = 5;
let sortState = { column: null, direction: 'asc' };

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', initializeDashboard);

async function initializeDashboard() {
    try {
        const data = await fetchCandidates();
        if (!Array.isArray(data)) {
            throw new Error("Fetched data is not a valid JSON array. Please check the file content.");
        }
        masterCandidatesData = data;
        filteredCandidatesData = [...masterCandidatesData];

        setupEventListeners();
        updateDashboard();
    } catch (error) {
        console.error("Dashboard Initialization Failed:", error);
        displayFatalError("Could not load candidate data. Please check the S3 bucket permissions (CORS), ensure the file is public, or verify the file URL and try again.");
    }
}

async function fetchCandidates() {
    const dataUrl = 'PLEASE SPECIFY THIS YOURSELF';
    const response = await fetch(`${dataUrl}?t=${new Date().getTime()}`, {
        cache: 'no-cache'
    });

    if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
    }
    return await response.json();
}

function setupEventListeners() {
    document.getElementById('searchInput').addEventListener('input', filterData);
    document.getElementById('skillFilter').addEventListener('change', filterData);
}

// --- DATA MANIPULATION & DISPLAY ---
function updateDashboard() {
    updateStats();
    renderTable();
    updatePagination();
}

function updateStats() {
    const totalUploads = masterCandidatesData.length;

    let errorCount = 0;
    masterCandidatesData.forEach(candidate => {
        if (candidate?.name?.toLowerCase().includes("error")) {
            errorCount++;
        }
    });

    const successCount = totalUploads - errorCount;
    const successRate = totalUploads > 0 ? Math.round((successCount / totalUploads) * 100) : 0;

    document.getElementById('totalUploads').textContent = totalUploads.toLocaleString();
    document.getElementById('successRate').textContent = `${successRate}%`;
    document.getElementById('totalErrors').textContent = errorCount.toLocaleString();
    document.getElementById('totalCandidates').textContent = successCount.toLocaleString();
}

function filterData() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const skillFilter = document.getElementById('skillFilter').value.toLowerCase();

    filteredCandidatesData = masterCandidatesData.filter(candidate => {
        if (!candidate || !candidate.name) return false;

        const allSkills = [
            ...(candidate.skills?.technical || []),
            ...(candidate.skills?.nonTechnical || [])
        ];

        const matchesSearch = searchTerm === '' ||
            candidate.name.toLowerCase().includes(searchTerm) ||
            (candidate.email && candidate.email.toLowerCase().includes(searchTerm)) ||
            allSkills.some(skill => skill.toLowerCase().includes(searchTerm));

        const matchesSkill = skillFilter === '' ||
            allSkills.some(skill => skill.toLowerCase().includes(skillFilter));

        return matchesSearch && matchesSkill;
    });

    currentPage = 1;
    updateDashboard();
}

function renderTable() {
    const tableBody = document.getElementById('candidatesTableBody');
    tableBody.innerHTML = '';

    document.getElementById('candidateCount').textContent = `Showing ${filteredCandidatesData.length} candidate${filteredCandidatesData.length !== 1 ? 's' : ''}`;

    if (filteredCandidatesData.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="8" class="no-results">No candidates found matching your criteria.</td></tr>`;
        return;
    }

    const pageData = filteredCandidatesData.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

    pageData.forEach(candidate => {
        const row = document.createElement('tr');
        const allSkills = [
            ...(candidate.skills?.technical || []),
            ...(candidate.skills?.nonTechnical || [])
        ];
        const skillsHtml = allSkills.length > 0
            ? allSkills.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')
            : 'N/A';

        const formattedDate = formatDate(candidate.uploadDate);
        const emailLink = candidate.email ? `<a href="mailto:${escapeHtml(candidate.email)}" class="candidate-email">${escapeHtml(candidate.email)}</a>` : 'N/A';

        row.innerHTML = `
            <td><input type="checkbox" class="candidate-checkbox" value="${escapeHtml(candidate.candidateId)}"></td>
            <td><span class="candidate-name">${escapeHtml(candidate.name)}</span></td>
            <td>${emailLink}</td>
            <td><div class="skills-tags">${skillsHtml}</div></td>
            <td>${escapeHtml(candidate.experienceSummary || 'N/A')}</td>
            <td>${escapeHtml(formattedDate)}</td>
            <td><span class="status-badge status-success">success</span></td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn" onclick="viewResume('${escapeHtml(candidate.candidateId)}')" title="View Details"><i class="fas fa-eye"></i></button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function sortTable(columnIndex) {
    const columnKey = ['name', 'email', 'skills', 'experienceSummary', 'uploadDate', 'status'][columnIndex - 1];
    if (columnKey === 'status') return;

    if (sortState.column === columnKey) {
        sortState.direction = sortState.direction === 'asc' ? 'desc' : 'asc';
    } else {
        sortState.column = columnKey;
        sortState.direction = 'asc';
    }

    filteredCandidatesData.sort((a, b) => {
        let valA = a[columnKey] || '';
        let valB = b[columnKey] || '';

        if (!valA) return 1;
        if (!valB) return -1;

        if (columnKey === 'skills') {
            const skillsA = [...(a.skills?.technical || []), ...(a.skills?.nonTechnical || [])];
            const skillsB = [...(b.skills?.technical || []), ...(b.skills?.nonTechnical || [])];
            valA = skillsA.join(', ');
            valB = skillsB.join(', ');
        }

        if (typeof valA === 'string' && columnKey !== 'uploadDate') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }

        if (valA < valB) return sortState.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortState.direction === 'asc' ? 1 : -1;
        return 0;
    });

    currentPage = 1;
    updateDashboard();
}

// --- UI ACTIONS & MODALS ---
function viewResume(id) {
    const candidate = masterCandidatesData.find(c => c.candidateId == id);
    if (!candidate) return;

    const allSkills = [
        ...(candidate.skills?.technical || []),
        ...(candidate.skills?.nonTechnical || [])
    ];
    const skillsHtml = allSkills.length > 0
        ? allSkills.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')
        : 'No skills listed.';

    const formattedUploadDate = formatDate(candidate.uploadDate);
    const emailLink = candidate.email ? `<a href="mailto:${escapeHtml(candidate.email)}">${escapeHtml(candidate.email)}</a>` : 'N/A';

    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="resume-details">
            <div class="detail-section">
                <h3><i class="fas fa-user"></i> Personal Information</h3>
                <div class="detail-grid">
                    <div><strong>Name:</strong> ${escapeHtml(candidate.name)}</div>
                    <div><strong>Email:</strong> ${emailLink}</div>
                    <div><strong>Phone:</strong> ${escapeHtml(candidate.phoneNumber || 'N/A')}</div>
                    <div><strong>Upload Date:</strong> ${escapeHtml(formattedUploadDate)}</div>
                </div>
            </div>
            <div class="detail-section">
                <h3><i class="fas fa-briefcase"></i> Experience Summary</h3>
                <p>${escapeHtml(candidate.experienceSummary || 'N/A')}</p>
            </div>
            <div class="detail-section">
                <h3><i class="fas fa-code"></i> Skills</h3>
                <div class="skills-tags">${skillsHtml}</div>
            </div>
            <div class="detail-section">
                <h3><i class="fas fa-language"></i> Languages</h3>
                <p>${escapeHtml(Array.isArray(candidate.languages) ? candidate.languages.join(', ') : (candidate.languages || 'N/A'))}</p>
            </div>
        </div>
    `;
    document.getElementById('resumeModal').style.display = 'block';
}

function downloadCSV() {
    const headers = ['ID', 'Name', 'Email', 'Upload Date', 'Experience Summary', 'Skills', 'Languages'];
    const rows = filteredCandidatesData.map(c => {
        const allSkills = [...(c.skills?.technical || []), ...(c.skills?.nonTechnical || [])];
        const languages = Array.isArray(c.languages) ? c.languages.join('; ') : (c.languages || 'N/A');
        return [
            c.candidateId,
            c.name,
            c.email || 'N/A',
            c.uploadDate || 'N/A',
            (c.experienceSummary || '').replace(/,/g, ''),
            allSkills.join('; '),
            languages
        ];
    });

    let csvContent = "data:text/csv;charset=utf-8," +
        headers.join(",") + "\n" +
        rows.map(e => e.map(cell => `"${(cell || '').replace(/"/g, '""')}"`).join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `candidates_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// --- PAGINATION ---
function updatePagination() {
    const totalPages = Math.ceil(filteredCandidatesData.length / ITEMS_PER_PAGE) || 1;
    document.getElementById('currentPage').textContent = currentPage;
    document.getElementById('totalPages').textContent = totalPages;

    const prevBtn = document.querySelector('.pagination-btn:first-child');
    const nextBtn = document.querySelector('.pagination-btn:last-child');
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

function changePage(direction) {
    const totalPages = Math.ceil(filteredCandidatesData.length / ITEMS_PER_PAGE);
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        renderTable();
        updatePagination();
    }
}

// --- UTILITIES ---
function formatDate(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    if (isNaN(date)) return 'Invalid Date';
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function displayFatalError(message) {
    const container = document.querySelector('.main-container');
    container.innerHTML = `<div class="fatal-error">
        <i class="fas fa-shield-alt"></i>
        <h2>Error Loading Dashboard</h2>
        <p>${message}</p>
    </div>`;
}

// --- GLOBAL FUNCTIONS ---
window.changePage = changePage;
window.sortTable = sortTable;
window.viewResume = viewResume;
window.downloadCSV = downloadCSV;
window.logout = () => { window.location.href = "/admin"; };
window.closeModal = () => document.getElementById('resumeModal').style.display = 'none';
window.clearFilters = () => {
    document.getElementById('searchInput').value = '';
    document.getElementById('skillFilter').value = '';
    filterData();
};
window.toggleSelectAll = () => {
    const isChecked = document.getElementById('selectAll').checked;
    document.querySelectorAll('.candidate-checkbox').forEach(cb => cb.checked = isChecked);
};
