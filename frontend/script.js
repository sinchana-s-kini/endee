const API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const docTitle = document.getElementById('doc-title');
    const docContent = document.getElementById('doc-content');
    const ingestBtn = document.getElementById('ingest-btn');
    const ingestStatus = document.getElementById('ingest-status');

    const searchQuery = document.getElementById('search-query');
    const searchBtn = document.getElementById('search-btn');
    const resultsArea = document.getElementById('results-area');

    // Helper to show status
    const showStatus = (element, message, type) => {
        element.textContent = message;
        element.className = `status-msg ${type}`;
        element.classList.remove('hidden');
        setTimeout(() => {
            element.classList.add('hidden');
        }, 5000);
    };

    // Ingest Knowledge
    const handleIngest = async () => {
        const title = docTitle.value.trim();
        const text = docContent.value.trim();

        if (!text) {
            showStatus(ingestStatus, 'Please enter some knowledge content.', 'error');
            return;
        }

        const originalBtnText = ingestBtn.innerHTML;
        ingestBtn.innerHTML = `<span>Processing...</span><i data-lucide="loader-2" class="spin"></i>`;
        lucide.createIcons();
        ingestBtn.disabled = true;

        try {
            const res = await fetch(`${API_BASE}/ingest/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title || 'Untitled Document', text })
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || 'Ingestion failed');

            showStatus(ingestStatus, `Success! Extracted and embedded ${data.chunks_inserted} chunks into Endee.`, 'success');
            docTitle.value = '';
            docContent.value = '';
        } catch (error) {
            showStatus(ingestStatus, error.message, 'error');
        } finally {
            ingestBtn.innerHTML = originalBtnText;
            lucide.createIcons();
            ingestBtn.disabled = false;
        }
    };

    ingestBtn.addEventListener('click', handleIngest);

    // Render Results
    const renderResults = (results) => {
        resultsArea.innerHTML = '';

        if (!results || results.length === 0) {
            resultsArea.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="frown"></i>
                    <p>No highly relevant results found.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        results.forEach((res, index) => {
            const delay = index * 0.1;
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${delay}s`;

            const metaTitle = res.meta?.title || 'Unknown Source';
            const chunkText = res.meta?.text_chunk || 'No text extracted.';
            const simScore = res.similarity ? res.similarity.toFixed(3) : 0;

            card.innerHTML = `
                <div class="result-meta">
                    <span class="result-title"><i data-lucide="file-text" style="width:14px;height:14px;display:inline-block;vertical-align:middle;margin-right:4px;"></i>${metaTitle}</span>
                    <span class="result-score">Score: ${simScore}</span>
                </div>
                <div class="result-text">${chunkText}</div>
            `;
            resultsArea.appendChild(card);
        });

        lucide.createIcons();
    };

    // Semantic Search
    const handleSearch = async () => {
        const query = searchQuery.value.trim();
        if (!query) return;

        searchBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i>`;
        lucide.createIcons();
        searchBtn.disabled = true;

        // Add loading state to results area
        resultsArea.innerHTML = `
            <div class="empty-state">
                <i data-lucide="loader-2" class="spin" style="animation: spin 2s linear infinite;"></i>
                <p>Searching vectors...</p>
            </div>
        `;
        lucide.createIcons();

        try {
            const res = await fetch(`${API_BASE}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: 5 })
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || 'Search failed');

            // Render AI Answer
            resultsArea.innerHTML = '';

            if (data.answer) {
                const answerCard = document.createElement('div');
                answerCard.className = 'ai-answer-card';
                answerCard.innerHTML = `
                    <div class="ai-answer-header">
                        <i data-lucide="bot"></i>
                        <span>AI Synthesized Answer</span>
                    </div>
                    <div class="ai-answer-content">
                        ${data.answer.replace(/\n/g, '<br/>')}
                    </div>
                `;
                resultsArea.appendChild(answerCard);
            }

            // Render Sources label
            if (data.results && data.results.length > 0) {
                const sourcesLabel = document.createElement('div');
                sourcesLabel.className = 'sources-label';
                sourcesLabel.innerHTML = '<h4>Retrieved Context Sources</h4>';
                resultsArea.appendChild(sourcesLabel);
            }

            // Render raw chunks (Results)
            renderResults(data.results, false); // pass false so we append instead of clear

        } catch (error) {
            resultsArea.innerHTML = `
                <div class="empty-state" style="color:var(--error)">
                    <i data-lucide="alert-circle"></i>
                    <p>Error: ${error.message}</p>
                </div>
            `;
            lucide.createIcons();
        } finally {
            searchBtn.innerHTML = `<i data-lucide="arrow-right"></i>`;
            lucide.createIcons();
            searchBtn.disabled = false;
        }
    };

    searchBtn.addEventListener('click', handleSearch);
    searchQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

});
