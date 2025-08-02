// --- CONFIGURATION ---
const GEMINI_API_KEY = "PLEASE SPECIFY THIS YOURSELF"; 
const CANDIDATES_JSON_URL = 'PLEASE SPECIFY THIS YOURSELF';

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', async () => {
    const candidates = await fetchCandidatesData();
    if (candidates) {
        const aiReport = await generateAiReport(candidates);
        if (aiReport) displayAiSummary(aiReport.analysisSummary);
    }
});

// --- FUNCTIONS ---

async function fetchCandidatesData() {
    try {
        const response = await fetch(`${CANDIDATES_JSON_URL}?t=${Date.now()}`);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching candidates.json:", error);
        handleError('aiSummaryContainer', `Failed to load candidate data. Check S3 URL or CORS.`);
        return null;
    }
}

async function generateAiReport(candidates) {
    if (!GEMINI_API_KEY || GEMINI_API_KEY.includes("YOUR_GEMINI_API_KEY")) {
        handleError('aiSummaryContainer', 'Gemini API key is not configured.');
        return null;
    }

    const simplifiedData = candidates.map(c => ({
        name: c.name,
        experience: c.experienceSummary,
        skills: c.skills?.technical?.slice(0, 15) || []
    }));

    const prompt = `
        As an expert technical recruiter, analyze the following candidate data:

        1. **Create a Comprehensive Summary**: Identify top candidates for roles like Full-Stack Developer, Data Scientist, and Cloud Engineer. Summarize your findings in structured paragraphs.

        Return only this structure:
        {
          "analysisSummary": "Your detailed text summary here..."
        }

        Candidate Data:
        ---
        ${JSON.stringify(simplifiedData, null, 2)}
    `;

    try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const payload = { contents: [{ parts: [{ text: prompt }] }] };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        const text = data.candidates[0].content.parts[0].text.trim();
        const cleaned = text.replace(/```json/g, '').replace(/```/g, '').trim();
        return JSON.parse(cleaned);

    } catch (error) {
        console.error("Gemini API Error:", error);
        handleError('aiSummaryContainer', `Failed to generate summary. ${error.message}`);
        return null;
    }
}

function displayAiSummary(summaryText) {
    const container = document.getElementById('aiSummaryContainer');
    container.innerHTML = summaryText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').trim();
}

function handleError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div style="color:red;"><b>Error:</b> ${message}</div>`;
    }
}
