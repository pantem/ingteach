const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : 'https://ingteach.onrender.com/api';

function setToken(token) {
    localStorage.setItem('token', token);
    document.cookie = `token=${token};path=/;max-age=2592000`;
}

function getToken() {
    let t = localStorage.getItem('token');
    if (!t) {
        const m = document.cookie.match(/(?:^|;\s*)token=([^;]*)/);
        if (m) { t = m[1]; localStorage.setItem('token', t); }
    }
    return t;
}

function delToken() {
    localStorage.removeItem('token');
    document.cookie = 'token=;path=/;max-age=0';
}

async function apiRequest(path, options = {}) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || `Request failed: ${res.status}`);
    }
    return data;
}

function apiGet(path) { return apiRequest(path); }

function apiPost(path, body = {}) {
    return apiRequest(path, { method: 'POST', body: JSON.stringify(body) });
}

const api = {
    login: (email, password) => apiPost('/auth/login', { email, password }),
    register: (username, email, password) => apiPost('/auth/register', { username, email, password }),
    getMe: () => apiGet('/auth/me'),

    getModules: () => apiGet('/modules/'),
    getModule: (id) => apiGet(`/modules/${id}`),

    getTopics: (moduleId) => apiGet(`/conversation/topics${moduleId ? `?module_id=${moduleId}` : ''}`),
    getTopic: (id) => apiGet(`/conversation/topics/${id}`),
    chat: (topicId, content) => apiPost(`/conversation/chat/${topicId}`, { role: 'user', content }),
    evaluateSpeech: (transcript, expected) => apiPost('/conversation/evaluate', { transcript, expected_phrases: expected }),

    getVerbs: (tense) => apiGet(`/conjugations/verbs${tense ? `?tense=${tense}` : ''}`),
    getVerb: (verb, tense) => apiGet(`/conjugations/verbs/${verb}${tense ? `?tense=${tense}` : ''}`),
    getTenses: () => apiGet('/conjugations/tenses'),

    getTests: () => apiGet('/tests/'),
    getModuleTest: (id) => apiGet(`/tests/${id}`),
    submitTest: (moduleId, answers) => apiPost(`/tests/submit/${moduleId}`, { module_id: moduleId, answers }),

    getProgress: (userId = 'default') => apiGet(`/progress/${userId}`),
    getRecommendations: (userId = 'default') => apiGet(`/progress/${userId}/recommendations`),

    getMyProgress: () => apiGet('/progress/me'),
    completeMyModule: (moduleId) => apiPost(`/progress/me/complete-module/${moduleId}`),
    updateMyScore: (moduleId, score) => apiPost('/progress/me/update-score', { module_id: moduleId, score }),
    recordPracticeSession: (durationSeconds) => apiPost('/progress/me/practice-session', { duration_seconds: durationSeconds }),
    getMyRecommendations: () => apiGet('/progress/me/recommendations'),
};
