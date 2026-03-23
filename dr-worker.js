/* Distant Reading worker: heavy aggregation off the UI thread */
self.onmessage = (e) => {
    const payload = e.data || {};
    const reqId = payload.reqId;
    const datasets = payload.datasets || {};
    const activeMetric = payload.activeMetric || 'alignment_score';
    const scoreRange = payload.scoreRange || [0, 1];
    const enrichedData = payload.enrichedData || null;

    function getScore(cand) {
        const val = cand[activeMetric];
        if (val != null && !isNaN(val)) return val;
        return cand.alignment_score ?? cand.norm_score ?? cand.score ?? 0;
    }
    function inRange(s) {
        return s >= scoreRange[0];
    }
    function getNliId(location) {
        if (!location) return null;
        const m = String(location).match(/Geniza_(\d{12,20})/);
        return m ? m[1] : null;
    }

    const allFragments = {};
    for (const [bookName, indexData] of Object.entries(datasets)) {
        for (const [unitId, unit] of Object.entries(indexData || {})) {
            const cands = unit.candidates || [];
            for (const cand of cands) {
                const s = getScore(cand);
                if (!inRange(s)) continue;
                const loc = cand.location || cand.elastic_id || '';
                const nliId = getNliId(loc);
                if (!nliId) continue;
                if (!allFragments[nliId]) allFragments[nliId] = { nliId: nliId, matches: [] };
                allFragments[nliId].matches.push({ book: bookName, unitId, score: s, location: loc });
            }
        }
    }

    const subjectIndex = {};
    if (enrichedData) {
        const subjPatterns = [
            /בראשית רבה/,/שמות רבה/,/ויקרא רבה/,/במדבר רב/,/דברים רבה/,
            /תנחומא/,/תהלים/,/משלי/,/קהלת/,/שיר השירים/,/איכה/,/רות/,/אסתר/,
            /בראשית/,/שמות/,/ויקרא/,/במדבר/,/דברים/,/ישעיה/,/ירמיה/,/יחזקאל/,
            /תלמוד/,/משנה/,/תוספת/,/פיוט/,/הלכ/,/תרגום/,/פרשנות/,/דרש/,
            /ספרי/,/ספרא/,/מכילת/,/פסיקתא/,/ילקוט/,/אבות דרבי נתן/
        ];
        for (const [nliId, frag] of Object.entries(allFragments)) {
            const meta = enrichedData[nliId];
            if (!meta) continue;
            const text = [meta.title || '', meta.general_notes || '', meta.title_alt || ''].join(' ');
            for (const pat of subjPatterns) {
                const m = text.match(pat);
                if (m) {
                    const key = m[0];
                    if (!subjectIndex[key]) subjectIndex[key] = new Set();
                    subjectIndex[key].add(nliId);
                }
            }
        }
    }

    const subjectIndexOut = {};
    for (const [k, v] of Object.entries(subjectIndex)) {
        subjectIndexOut[k] = Array.from(v);
    }

    self.postMessage({ reqId, allFragments, subjectIndex: subjectIndexOut });
};
