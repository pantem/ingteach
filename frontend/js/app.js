let state = {
    currentView: 'dashboard',
    currentModule: null,
    currentTopic: null,
    chatHistory: [],
    selectedTestModule: null,
    testAnswers: {},
    voice: null,
    recognition: null,
    isRecording: false,
    speechResult: null,
    user: null,
    charts: {},
    usedVocabulary: new Set(),
    dictOpen: false,
};

const MODULE_NAMES = {
    'mod-1': 'Greetings and Introductions',
    'mod-2': 'Daily Routines',
    'mod-3': 'Food and Restaurants',
    'mod-4': 'Past Experiences',
    'mod-5': 'Future Plans',
    'mod-6': 'Travel and Directions',
    'mod-7': 'Opinions and Debates',
    'mod-8': 'Business English',
};

const MODULE_LIST = ['mod-1', 'mod-2', 'mod-3', 'mod-4', 'mod-5', 'mod-6', 'mod-7', 'mod-8'];

document.addEventListener('DOMContentLoaded', () => {
    const savedUser = localStorage.getItem('user');
    const token = getToken();
    if (savedUser && token) {
        try { state.user = JSON.parse(savedUser); showApp(); } catch { }
        tryLoginWithToken();
    } else if (token) {
        tryLoginWithToken();
    }
    initAuthForms();
    initNavigation();
    initLogout();
    initDictionary();
});

async function tryLoginWithToken() {
    if (!getToken()) { showAuth(); return; }
    try {
        const resp = await fetch('http://localhost:8000/api/auth/me', {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (resp.status === 401) {
            delToken();
            localStorage.removeItem('user');
            state.user = null;
            showAuth();
            return;
        }
        if (!resp.ok) {
            setTimeout(tryLoginWithToken, 2000);
            return;
        }
        state.user = await resp.json();
        localStorage.setItem('user', JSON.stringify(state.user));
        const appEl = document.getElementById('app');
        if (appEl && appEl.classList.contains('hidden')) {
            showApp();
        }
    } catch {
        setTimeout(tryLoginWithToken, 2000);
    }
}

// --- Auth ---
function showAuth() {
    document.getElementById('auth-overlay').classList.remove('hidden');
    document.getElementById('auth-overlay').querySelector('.auth-card').style.display = 'block';
    document.getElementById('app').classList.add('hidden');
}

function showApp() {
    if (!state.user) {
        const saved = localStorage.getItem('user');
        if (saved) { try { state.user = JSON.parse(saved); } catch { } }
    }
    document.getElementById('auth-overlay').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    document.getElementById('user-name').textContent = state.user?.username || 'Usuario';
    document.getElementById('user-email').textContent = state.user?.email || '';
    document.getElementById('user-avatar').textContent = (state.user?.username || 'U').charAt(0).toUpperCase();

    initSpeechRecognition();
    initVoiceSelect();
    loadDashboard();
    loadModules();
    loadTopics();
    loadConjugations();
    loadTests();
    loadProgress();
}

function initAuthForms() {
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`form-${tab.dataset.form}`).classList.add('active');
        });
    });

    document.getElementById('form-login').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');
        errorEl.classList.add('hidden');
        const btn = document.getElementById('btn-entrar');
        btn.disabled = true;
        btn.classList.add('btn-loading');
        try {
            const result = await api.login(email, password);
            setToken(result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            state.user = result.user;
            showApp();
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.classList.remove('hidden');
        } finally {
            btn.disabled = false;
            btn.classList.remove('btn-loading');
        }
    });

    document.getElementById('form-register').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        const email = document.getElementById('reg-email').value;
        const errorEl = document.getElementById('register-error');
        errorEl.classList.add('hidden');
        try {
            const result = await api.register(username, email, password);
            setToken(result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            state.user = result.user;
            showApp();
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.classList.remove('hidden');
        }
    });
}

function initLogout() {
    document.getElementById('btn-logout').addEventListener('click', () => {
        delToken();
        localStorage.removeItem('user');
        state.user = null;
        Object.values(state.charts).forEach(c => { try { c.destroy(); } catch { } });
        state.charts = {};
        showAuth();
    });
}

const DICT = [
    {en:"hello",es:"hola"},{en:"goodbye",es:"adiós"},{en:"good morning",es:"buenos días"},{en:"good night",es:"buenas noches"},{en:"please",es:"por favor"},{en:"thank you",es:"gracias"},{en:"sorry",es:"lo siento"},{en:"yes",es:"sí"},{en:"no",es:"no"},{en:"maybe",es:"tal vez"},{en:"okay",es:"está bien"},{en:"help",es:"ayuda"},{en:"name",es:"nombre"},{en:"friend",es:"amigo"},{en:"family",es:"familia"},{en:"mother",es:"madre"},{en:"father",es:"padre"},{en:"brother",es:"hermano"},{en:"sister",es:"hermana"},{en:"child",es:"niño"},{en:"teacher",es:"maestro"},{en:"student",es:"estudiante"},{en:"doctor",es:"médico"},{en:"person",es:"persona"},{en:"people",es:"personas"},{en:"man",es:"hombre"},{en:"woman",es:"mujer"},{en:"boy",es:"niño"},{en:"girl",es:"niña"},{en:"day",es:"día"},{en:"night",es:"noche"},{en:"morning",es:"mañana"},{en:"afternoon",es:"tarde"},{en:"evening",es:"noche"},{en:"today",es:"hoy"},{en:"tomorrow",es:"mañana"},{en:"yesterday",es:"ayer"},{en:"week",es:"semana"},{en:"month",es:"mes"},{en:"year",es:"año"},{en:"time",es:"tiempo"},{en:"hour",es:"hora"},{en:"minute",es:"minuto"},{en:"now",es:"ahora"},{en:"later",es:"después"},{en:"always",es:"siempre"},{en:"never",es:"nunca"},{en:"sometimes",es:"a veces"},{en:"usually",es:"usualmente"},{en:"often",es:"a menudo"},{en:"here",es:"aquí"},{en:"there",es:"allí"},{en:"where",es:"dónde"},{en:"when",es:"cuándo"},{en:"why",es:"por qué"},{en:"what",es:"qué"},{en:"how",es:"cómo"},{en:"who",es:"quién"},{en:"which",es:"cuál"},{en:"big",es:"grande"},{en:"small",es:"pequeño"},{en:"hot",es:"caliente"},{en:"cold",es:"frío"},{en:"good",es:"bueno"},{en:"bad",es:"malo"},{en:"new",es:"nuevo"},{en:"old",es:"viejo"},{en:"young",es:"joven"},{en:"tall",es:"alto"},{en:"short",es:"bajo"},{en:"long",es:"largo"},{en:"fast",es:"rápido"},{en:"slow",es:"lento"},{en:"easy",es:"fácil"},{en:"difficult",es:"difícil"},{en:"cheap",es:"barato"},{en:"expensive",es:"caro"},{en:"beautiful",es:"hermoso"},{en:"ugly",es:"feo"},{en:"happy",es:"feliz"},{en:"sad",es:"triste"},{en:"angry",es:"enojado"},{en:"tired",es:"cansado"},{en:"hungry",es:"hambriento"},{en:"thirsty",es:"sediento"},{en:"sick",es:"enfermo"},{en:"healthy",es:"saludable"},{en:"rich",es:"rico"},{en:"poor",es:"pobre"},{en:"important",es:"importante"},{en:"different",es:"diferente"},{en:"same",es:"mismo"},{en:"first",es:"primero"},{en:"last",es:"último"},{en:"next",es:"siguiente"},{en:"go",es:"ir"},{en:"come",es:"venir"},{en:"arrive",es:"llegar"},{en:"leave",es:"salir"},{en:"stay",es:"quedarse"},{en:"travel",es:"viajar"},{en:"walk",es:"caminar"},{en:"run",es:"correr"},{en:"eat",es:"comer"},{en:"drink",es:"beber"},{en:"cook",es:"cocinar"},{en:"breakfast",es:"desayuno"},{en:"lunch",es:"almuerzo"},{en:"dinner",es:"cena"},{en:"food",es:"comida"},{en:"water",es:"agua"},{en:"milk",es:"leche"},{en:"bread",es:"pan"},{en:"meat",es:"carne"},{en:"rice",es:"arroz"},{en:"fruit",es:"fruta"},{en:"vegetable",es:"verdura"},{en:"coffee",es:"café"},{en:"tea",es:"té"},{en:"beer",es:"cerveza"},{en:"wine",es:"vino"},{en:"do",es:"hacer"},{en:"make",es:"hacer/fabricar"},{en:"have",es:"tener"},{en:"get",es:"obtener"},{en:"give",es:"dar"},{en:"take",es:"tomar"},{en:"buy",es:"comprar"},{en:"sell",es:"vender"},{en:"pay",es:"pagar"},{en:"find",es:"encontrar"},{en:"lose",es:"perder"},{en:"keep",es:"guardar"},{en:"need",es:"necesitar"},{en:"want",es:"querer"},{en:"like",es:"gustar"},{en:"love",es:"amar"},{en:"hate",es:"odiar"},{en:"know",es:"saber/conocer"},{en:"think",es:"pensar"},{en:"believe",es:"creer"},{en:"understand",es:"entender"},{en:"learn",es:"aprender"},{en:"teach",es:"enseñar"},{en:"read",es:"leer"},{en:"write",es:"escribir"},{en:"speak",es:"hablar"},{en:"say",es:"decir"},{en:"tell",es:"contar"},{en:"ask",es:"preguntar"},{en:"answer",es:"responder"},{en:"show",es:"mostrar"},{en:"work",es:"trabajar"},{en:"study",es:"estudiar"},{en:"play",es:"jugar"},{en:"sing",es:"cantar"},{en:"dance",es:"bailar"},{en:"swim",es:"nadar"},{en:"sleep",es:"dormir"},{en:"wake up",es:"despertarse"},{en:"wash",es:"lavar"},{en:"clean",es:"limpiar"},{en:"open",es:"abrir"},{en:"close",es:"cerrar"},{en:"start",es:"empezar"},{en:"finish",es:"terminar"},{en:"try",es:"intentar"},{en:"change",es:"cambiar"},{en:"use",es:"usar"},{en:"can",es:"poder"},{en:"must",es:"deber"},{en:"should",es:"debería"},{en:"may",es:"puede que"},{en:"will",es:"va a"},{en:"would",es:"quisiera"},{en:"house",es:"casa"},{en:"apartment",es:"departamento"},{en:"room",es:"habitación"},{en:"door",es:"puerta"},{en:"window",es:"ventana"},{en:"table",es:"mesa"},{en:"chair",es:"silla"},{en:"bed",es:"cama"},{en:"bathroom",es:"baño"},{en:"kitchen",es:"cocina"},{en:"car",es:"coche"},{en:"bus",es:"autobús"},{en:"train",es:"tren"},{en:"airplane",es:"avión"},{en:"bicycle",es:"bicicleta"},{en:"street",es:"calle"},{en:"city",es:"ciudad"},{en:"country",es:"país"},{en:"store",es:"tienda"},{en:"restaurant",es:"restaurante"},{en:"hospital",es:"hospital"},{en:"school",es:"escuela"},{en:"office",es:"oficina"},{en:"park",es:"parque"},{en:"beach",es:"playa"},{en:"mountain",es:"montaña"},{en:"river",es:"río"},{en:"sea",es:"mar"},{en:"sky",es:"cielo"},{en:"sun",es:"sol"},{en:"moon",es:"luna"},{en:"star",es:"estrella"},{en:"rain",es:"lluvia"},{en:"snow",es:"nieve"},{en:"wind",es:"viento"},{en:"weather",es:"clima"},{en:"color",es:"color"},{en:"red",es:"rojo"},{en:"blue",es:"azul"},{en:"green",es:"verde"},{en:"yellow",es:"amarillo"},{en:"white",es:"blanco"},{en:"black",es:"negro"},{en:"one",es:"uno"},{en:"two",es:"dos"},{en:"three",es:"tres"},{en:"four",es:"cuatro"},{en:"five",es:"cinco"},{en:"six",es:"seis"},{en:"seven",es:"siete"},{en:"eight",es:"ocho"},{en:"nine",es:"nueve"},{en:"ten",es:"diez"},{en:"hundred",es:"cien"},{en:"thousand",es:"mil"},{en:"monday",es:"lunes"},{en:"tuesday",es:"martes"},{en:"wednesday",es:"miércoles"},{en:"thursday",es:"jueves"},{en:"friday",es:"viernes"},{en:"saturday",es:"sábado"},{en:"sunday",es:"domingo"},{en:"january",es:"enero"},{en:"february",es:"febrero"},{en:"march",es:"marzo"},{en:"april",es:"abril"},{en:"may",es:"mayo"},{en:"june",es:"junio"},{en:"july",es:"julio"},{en:"august",es:"agosto"},{en:"september",es:"septiembre"},{en:"october",es:"octubre"},{en:"november",es:"noviembre"},{en:"december",es:"diciembre"},{en:"spring",es:"primavera"},{en:"summer",es:"verano"},{en:"autumn",es:"otoño"},{en:"winter",es:"invierno"},{en:"dog",es:"perro"},{en:"cat",es:"gato"},{en:"bird",es:"pájaro"},{en:"fish",es:"pez"},{en:"horse",es:"caballo"},{en:"cow",es:"vaca"},{en:"pig",es:"cerdo"},{en:"chicken",es:"pollo"},{en:"animal",es:"animal"},{en:"tree",es:"árbol"},{en:"flower",es:"flor"},{en:"plant",es:"planta"},{en:"book",es:"libro"},{en:"pen",es:"bolígrafo"},{en:"paper",es:"papel"},{en:"phone",es:"teléfono"},{en:"computer",es:"computadora"},{en:"internet",es:"internet"},{en:"email",es:"correo electrónico"},{en:"money",es:"dinero"},{en:"price",es:"precio"},{en:"job",es:"trabajo"},{en:"meeting",es:"reunión"},{en:"problem",es:"problema"},{en:"idea",es:"idea"},{en:"question",es:"pregunta"},{en:"answer",es:"respuesta"},{en:"example",es:"ejemplo"},{en:"word",es:"palabra"},{en:"sentence",es:"oración"},{en:"letter",es:"carta"},{en:"number",es:"número"},{en:"map",es:"mapa"},{en:"music",es:"música"},{en:"movie",es:"película"},{en:"game",es:"juego"},{en:"sport",es:"deporte"},{en:"football",es:"fútbol"},{en:"basketball",es:"baloncesto"},{en:"tennis",es:"tenis"},{en:"clothes",es:"ropa"},{en:"shirt",es:"camisa"},{en:"pants",es:"pantalones"},{en:"shoes",es:"zapatos"},{en:"hat",es:"sombrero"},{en:"jacket",es:"chaqueta"},{en:"weather",es:"clima"},{en:"cloud",es:"nube"},{en:"fog",es:"niebla"},{en:"storm",es:"tormenta"},{en:"earthquake",es:"terremoto"},{en:"fire",es:"fuego"},{en:"accident",es:"accidente"},{en:"road",es:"carretera"},{en:"bridge",es:"puente"},{en:"corner",es:"esquina"},{en:"left",es:"izquierda"},{en:"right",es:"derecha"},{en:"straight",es:"derecho"},{en:"near",es:"cerca"},{en:"far",es:"lejos"},{en:"up",es:"arriba"},{en:"down",es:"abajo"},{en:"in",es:"en"},{en:"on",es:"sobre"},{en:"at",es:"en"},{en:"with",es:"con"},{en:"without",es:"sin"},{en:"for",es:"para"},{en:"to",es:"a"},{en:"from",es:"de"},{en:"about",es:"acerca de"},{en:"between",es:"entre"},{en:"under",es:"debajo"},{en:"over",es:"encima"},{en:"before",es:"antes"},{en:"after",es:"después"},{en:"during",es:"durante"},{en:"because",es:"porque"},{en:"but",es:"pero"},{en:"and",es:"y"},{en:"or",es:"o"},{en:"if",es:"si"},{en:"so",es:"entonces"},{en:"very",es:"muy"},{en:"too",es:"también"},{en:"also",es:"también"},{en:"only",es:"solo"},{en:"just",es:"solo"},{en:"more",es:"más"},{en:"less",es:"menos"},{en:"some",es:"algunos"},{en:"any",es:"cualquier"},{en:"many",es:"muchos"},{en:"much",es:"mucho"},{en:"a lot",es:"mucho"},{en:"enough",es:"suficiente"},{en:"all",es:"todo"},{en:"nothing",es:"nada"},{en:"everything",es:"todo"},{en:"something",es:"algo"},{en:"every",es:"cada"},{en:"other",es:"otro"},{en:"another",es:"otro"},{en:"each",es:"cada"},{en:"both",es:"ambos"},{en:"few",es:"pocos"},{en:"several",es:"varios"},{en:"such",es:"tal"},{en:"own",es:"propio"},{en:"same",es:"mismo"},{en:"different",es:"diferente"},{en:"whole",es:"todo"},{en:"part",es:"parte"},{en:"kind",es:"tipo"},{en:"way",es:"manera"},{en:"side",es:"lado"},{en:"top",es:"parte superior"},{en:"bottom",es:"fondo"},{en:"front",es:"frente"},{en:"back",es:"atrás"},{en:"inside",es:"dentro"},{en:"outside",es:"fuera"},{en:"middle",es:"medio"},{en:"center",es:"centro"},{en:"end",es:"fin"},{en:"beginning",es:"principio"},{en:"morning",es:"mañana (del día)"},{en:"hello",es:"hola"},{en:"goodbye",es:"adiós"},{en:"see you later",es:"hasta luego"},{en:"nice to meet you",es:"mucho gusto"},{en:"how are you?",es:"¿cómo estás?"},{en:"i am fine",es:"estoy bien"},{en:"what is your name?",es:"¿cómo te llamas?"},{en:"my name is",es:"me llamo"},{en:"where are you from?",es:"¿de dónde eres?"},{en:"i am from",es:"soy de"},{en:"how old are you?",es:"¿cuántos años tienes?"},{en:"i am years old",es:"tengo años"},{en:"do you speak english?",es:"¿hablas inglés?"},{en:"i don't understand",es:"no entiendo"},{en:"can you repeat?",es:"¿puedes repetir?"},{en:"what does it mean?",es:"¿qué significa?"},{en:"how do you say?",es:"¿cómo se dice?"},{en:"excuse me",es:"disculpe"},{en:"i'm sorry",es:"lo siento"},{en:"no problem",es:"no hay problema"},{en:"you're welcome",es:"de nada"},{en:"cheers",es:"salud"},{en:"congratulations",es:"felicidades"},{en:"good luck",es:"buena suerte"},{en:"have a nice day",es:"que tengas buen día"},{en:"take care",es:"cuídate"},{en:"i love you",es:"te amo"},{en:"i miss you",es:"te extraño"},{en:"see you soon",es:"nos vemos pronto"},
];

const DICT_API_CACHE = new Map();

function initDictionary() {
    const toggle = document.getElementById('btn-dict-toggle');
    const close = document.getElementById('btn-dict-close');
    const panel = document.getElementById('dict-panel');
    const search = document.getElementById('dict-search');
    const results = document.getElementById('dict-results');

    function show() {
        panel.classList.remove('hidden');
        state.dictOpen = true;
        search.focus();
        search.value = '';
        renderDictResults('');
    }
    function hide() {
        panel.classList.add('hidden');
        state.dictOpen = false;
    }

    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        state.dictOpen ? hide() : show();
    });
    close.addEventListener('click', hide);

    let debounceTimer;
    search.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        if (search.value.trim()) {
            debounceTimer = setTimeout(() => renderDictResults(search.value.trim()), 150);
        } else {
            renderDictResults('');
        }
    });
}

async function renderDictResults(query) {
    const results = document.getElementById('dict-results');
    if (!query) {
        results.innerHTML = '<div class="dict-empty">Escribe una palabra para buscar</div>';
        return;
    }
    const q = query.toLowerCase();
    const local = DICT.filter(e => e.en.includes(q) || e.es.includes(q)).slice(0, 50);

    if (local.length) {
        results.innerHTML = local.map(e =>
            `<div class="dict-entry"><span class="dict-en">${escapeHtml(e.en)}</span><span class="dict-es">${escapeHtml(e.es)}</span></div>`
        ).join('');
        return;
    }

    results.innerHTML = '<div class="dict-empty">Buscando en l&iacute;nea...</div>';

    const cacheKey = q;
    if (DICT_API_CACHE.has(cacheKey)) {
        const entry = DICT_API_CACHE.get(cacheKey);
        results.innerHTML = entry.map(e =>
            `<div class="dict-entry"><span class="dict-en">${escapeHtml(e.en)}</span><span class="dict-es">${escapeHtml(e.es)}</span></div>`
        ).join('');
        return;
    }

    try {
        const [transRes, dictRes] = await Promise.all([
            fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(q)}&langpair=en|es`).then(r => r.json()).catch(() => null),
            fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(q)}`).then(r => r.json()).catch(() => null)
        ]);

        const entries = [];

        if (transRes && transRes.responseData && transRes.responseData.translatedText) {
            const spanish = transRes.responseData.translatedText;
            entries.push({ en: q, es: spanish, source: 'api' });
        }

        if (dictRes && Array.isArray(dictRes)) {
            dictRes.slice(0, 2).forEach(entry => {
                if (entry.meanings) {
                    entry.meanings.forEach(m => {
                        if (m.definitions) {
                            m.definitions.slice(0, 2).forEach(d => {
                                if (d.definition) {
                                    entries.push({ en: q, es: `(${m.partOfSpeech}) ${d.definition}`, source: 'def' });
                                }
                            });
                        }
                    });
                }
            });
        }

        if (entries.length) {
            DICT_API_CACHE.set(cacheKey, entries);
            results.innerHTML = entries.map(e =>
                `<div class="dict-entry${e.source === 'api' ? ' dict-api' : ''}"><span class="dict-en">${escapeHtml(e.en)}</span><span class="dict-es">${escapeHtml(e.es)}</span></div>`
            ).join('');
        } else {
            results.innerHTML = '<div class="dict-empty">Sin resultados</div>';
        }
    } catch {
        results.innerHTML = '<div class="dict-empty">Error al buscar</div>';
    }
}

// --- Navigation ---
function navigateTo(view) {
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`.nav-link[data-view="${view}"]`)?.classList.add('active');
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${view}`)?.classList.add('active');
    state.currentView = view;
    document.getElementById('sidebar').classList.remove('open');
    if (view === 'dashboard') loadDashboard();
    if (view === 'modules') loadModules();
    if (view === 'conversation') loadTopics();
    if (view === 'conjugations') loadConjugations();
    if (view === 'tests') loadTests();
    if (view === 'progress') loadProgress();
}

function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            if (!link.dataset.view) return;
            e.preventDefault();
            navigateTo(link.dataset.view);
        });
    });
    document.getElementById('mobile-menu-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });
    document.getElementById('btn-send').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    document.getElementById('btn-speech').addEventListener('click', toggleRecording);
    document.getElementById('btn-stop-speech').addEventListener('click', stopRecording);
    document.getElementById('btn-suggest-phrase').addEventListener('click', suggestPhrase);
    document.getElementById('verb-select').addEventListener('change', loadConjugationTable);
    document.getElementById('tense-select').addEventListener('change', loadConjugationTable);
    document.getElementById('btn-submit-test').addEventListener('click', submitTest);
}

function initVoiceSelect() {
    if (!window.speechSynthesis) return;
    const select = document.getElementById('voice-select');
    const populate = () => {
        const voices = speechSynthesis.getVoices().filter(v => v.lang.startsWith('en'));
        select.innerHTML = '<option value="">Voz por defecto</option>';
        voices.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.name;
            opt.textContent = `${v.name} (${v.lang})`;
            select.appendChild(opt);
        });
    };
    populate();
    speechSynthesis.onvoiceschanged = populate;
    select.addEventListener('change', () => {
        const voices = speechSynthesis.getVoices().filter(v => v.lang.startsWith('en'));
        state.voice = voices.find(v => v.name === select.value) || null;
    });
}

// --- Speech Recognition ---
function initSpeechRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        document.getElementById('btn-speech').disabled = true;
        document.getElementById('btn-speech').textContent = 'Micr\u00f3fono no disponible';
        return;
    }
    state.recognition = new SR();
    state.recognition.lang = 'en-US';
    state.recognition.continuous = true;
    state.recognition.interimResults = true;
    state.recognition.maxAlternatives = 1;
    state._silenceTimer = null;
    state._lastTranscript = '';

    state.recognition.onresult = async (event) => {
        if (state._silenceTimer) clearTimeout(state._silenceTimer);

        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript + ' ';
            }
        }

        if (finalTranscript.trim()) {
            state._lastTranscript = finalTranscript.trim();
        }

        if (state._lastTranscript) {
            document.getElementById('transcript-text').textContent = state._lastTranscript;
        }

        state._silenceTimer = setTimeout(() => {
            const text = state._lastTranscript;
            if (!text) return;
            state._lastTranscript = '';
            state.isRecording = false;
            updateMicButton();
            if (state.recognition) {
                try { state.recognition.stop(); } catch { }
            }

            document.getElementById('speech-result').classList.remove('hidden');

            const expected = state.currentTopic ? state.currentTopic.key_phrases : [];
            document.getElementById('speech-feedback').textContent = 'Evaluando...';

            addChatMessage('user', text);
            trackVocabulary(text);

            api.evaluateSpeech(text, expected).then(evaluation => {
                displaySpeechEvaluation(evaluation);
                state.speechResult = evaluation;
            }).catch(() => {
                document.getElementById('speech-feedback').textContent = 'Error al evaluar. Intenta de nuevo.';
            });
        }, 2500);
    };

    state.recognition.onerror = (event) => {
        if (state._silenceTimer) clearTimeout(state._silenceTimer);
        state.isRecording = false;
        state._lastTranscript = '';
        updateMicButton();
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
            console.error('Speech error:', event.error);
        }
    };

    state.recognition.onend = () => {
        state.isRecording = false;
        updateMicButton();
    };
}

function toggleRecording() {
    if (!state.recognition) return;
    state.isRecording ? stopRecording() : startRecording();
}

function startRecording() {
    if (!state.recognition) return;
    if (!state.currentTopic) { alert('Selecciona un tema de conversaci\u00f3n primero.'); return; }
    state.isRecording = true;
    state.recognition.start();
    updateMicButton();
}

function stopRecording() {
    if (!state.recognition) return;
    state.isRecording = false;
    state.recognition.stop();
    updateMicButton();
}

function updateMicButton() {
    const btn = document.getElementById('btn-speech');
    const stopBtn = document.getElementById('btn-stop-speech');
    if (state.isRecording) {
        btn.classList.add('recording');
        btn.innerHTML = '<span class="mic-icon">\u{1F3A4}</span> Grabando...';
        stopBtn.disabled = false;
    } else {
        btn.classList.remove('recording');
        btn.innerHTML = '<span class="mic-icon">\u{1F3A4}</span> Hablar';
        stopBtn.disabled = true;
    }
}

function displaySpeechEvaluation(eval) {
    const cls = (v) => v >= 0.7 ? 'good' : v >= 0.4 ? 'average' : 'poor';
    document.getElementById('score-accuracy').textContent = `${Math.round(eval.accuracy_score * 100)}%`;
    document.getElementById('score-accuracy').className = `score-value ${cls(eval.accuracy_score)}`;
    document.getElementById('score-pronunciation').textContent = `${Math.round(eval.pronunciation_score * 100)}%`;
    document.getElementById('score-pronunciation').className = `score-value ${cls(eval.pronunciation_score)}`;
    document.getElementById('score-fluency').textContent = `${Math.round(eval.fluency_score * 100)}%`;
    document.getElementById('score-fluency').className = `score-value ${cls(eval.fluency_score)}`;
    document.getElementById('speech-feedback').textContent = eval.feedback;
    const ul = document.getElementById('speech-improvements');
    ul.innerHTML = '';
    eval.suggested_improvements.forEach(imp => {
        const li = document.createElement('li');
        li.textContent = imp;
        ul.appendChild(li);
    });

    showGrammarCorrection(eval.grammar_correction, eval.grammar_changes, eval.has_grammar_errors);
    if (eval.has_grammar_errors && eval.grammar_correction) {
        setTimeout(() => speak(eval.grammar_correction, 0.7), 500);
    } else {
        setTimeout(() => speak(eval.transcript, 0.7), 500);
    }
}

function speak(text, rate = 0.9) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = rate;
    if (state.voice) u.voice = state.voice;
    window.speechSynthesis.speak(u);
}

window.playTranscript = function () {
    const text = document.getElementById('transcript-text').textContent;
    if (text) speak(text, 0.7);
};

window.playCorrected = function () {
    const text = document.getElementById('corrected-text').textContent;
    if (text) speak(text, 0.7);
};

// --- Dashboard ---
async function loadDashboard() {
    try {
        const [progress, recs] = await Promise.all([
            api.getMyProgress(),
            api.getMyRecommendations(),
        ]);
        document.querySelector('#stats-modules .stat-number').textContent =
            `${progress.completed_modules.length}/8`;
        document.querySelector('#stats-sessions .stat-number').textContent =
            progress.conversation_sessions;
        document.querySelector('#stats-time .stat-number').textContent =
            Math.floor(progress.total_practice_time / 60);
        document.querySelector('#stats-current .stat-text').textContent =
            MODULE_NAMES[progress.current_module] || progress.current_module;

        renderDashboardChart(progress);
    } catch (err) {
        console.error('Dashboard error:', err);
    }
}

function renderDashboardChart(progress) {
    const canvas = document.getElementById('dashboard-chart');
    if (!canvas) return;
    if (state.charts.dashboard) state.charts.dashboard.destroy();

    const scores = progress.test_scores || {};
    const labels = [];
    const data = [];
    MODULE_LIST.forEach(m => {
        if (scores[m] !== undefined) {
            labels.push((MODULE_NAMES[m] || m).substring(0, 12));
            data.push(Math.round(scores[m] * 100));
        }
    });

    if (data.length === 0) {
        data.push(0);
        labels.push('Sin datos');
    }

    state.charts.dashboard = new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Puntaje (%)',
                data,
                backgroundColor: data.map(v => v >= 70 ? '#10b981' : v >= 40 ? '#f59e0b' : '#ef4444'),
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

// --- Modules ---
async function loadModules(level = 'all') {
    try {
        const modules = await api.getModules();
        const container = document.getElementById('modules-container');
        const filtered = level === 'all' ? modules : modules.filter(m => m.level === level);

        if (filtered.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay m\u00f3dulos para este nivel.</p>';
            return;
        }

        container.innerHTML = filtered.map(m => {
            const lc = m.level;
            const ll = m.level.charAt(0).toUpperCase() + m.level.slice(1);
            return `
                <div class="module-card" onclick="selectModule('${m.id}')">
                    <span class="level-badge ${lc}">${ll}</span>
                    <h3>${m.title}</h3>
                    <p>${m.description}</p>
                    <p><strong>Gram\u00e1tica:</strong> ${m.grammar_focus}</p>
                    <div class="vocab-tags">
                        ${m.vocabulary.slice(0, 8).map(v => `<span class="vocab-tag">${v}</span>`).join('')}
                    </div>
                </div>
            `;
        }).join('');

        document.querySelectorAll('.btn-filter').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                loadModules(btn.dataset.level);
            });
        });
    } catch (err) {
        document.getElementById('modules-container').innerHTML =
            '<p class="text-muted">Error al cargar m\u00f3dulos.</p>';
    }
}

async function selectModule(moduleId) {
    try {
        state.currentModule = await api.getModule(moduleId);
        state.usedVocabulary = new Set();
        navigateTo('conversation');
        await loadTopics(moduleId);
    } catch (err) { console.error(err); }
}

// --- Conversation ---
async function loadTopics(moduleId = null) {
    try {
        const topics = await api.getTopics(moduleId);
        const list = document.getElementById('topic-list');
        const btn = document.getElementById('btn-speech');
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('btn-send');

        if (topics.length === 0) {
            list.innerHTML = '<p class="text-muted">No hay temas para este m\u00f3dulo.</p>';
            btn.disabled = true; input.disabled = true; sendBtn.disabled = true;
            document.getElementById('btn-suggest-phrase').disabled = true;
            return;
        }

        list.innerHTML = topics.map(t =>
            `<div class="topic-item" data-id="${t.id}" onclick="selectTopic('${t.id}')">${t.title}</div>`
        ).join('');

        if (!state.currentTopic) await selectTopic(topics[0].id);
        btn.disabled = false; input.disabled = false; sendBtn.disabled = false;
    } catch (err) { console.error(err); }
}

async function selectTopic(topicId) {
    try {
        const topic = await api.getTopic(topicId);
        state.currentTopic = topic;
        state.chatHistory = [];
        state.usedVocabulary = new Set();
        document.querySelectorAll('.topic-item').forEach(t => t.classList.remove('active'));
        document.querySelector(`.topic-item[data-id="${topicId}"]`)?.classList.add('active');
        document.getElementById('key-phrases').innerHTML =
            topic.key_phrases.map(p => `<span class="phrase-chip">${p}</span>`).join('');
        updateVocabTracker();
        document.getElementById('btn-suggest-phrase').disabled = false;

        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = `
            <div class="chat-message assistant">
                <div class="role-label">Tutor</div>
                <div>${topic.scenario}</div>
            </div>`;
        state.chatHistory.push({ role: 'assistant', content: topic.scenario });
        speak(topic.scenario);
    } catch (err) { console.error(err); }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || !state.currentTopic) return;
    input.value = '';
    addChatMessage('user', text);
    trackVocabulary(text);
    document.getElementById('speech-result').classList.add('hidden');
    try {
        const response = await api.chat(state.currentTopic.id, text);
        addChatMessage('assistant', response.content);
        showGrammarCorrection(response.grammar_correction, response.grammar_changes, response.has_grammar_errors);
        speak(response.content);
    } catch { addChatMessage('assistant', 'Lo siento, hubo un error de conexi\u00f3n.'); }
}

function showGrammarCorrection(corrected, changes, hasErrors) {
    const box = document.getElementById('grammar-correction-box');
    if (hasErrors && corrected) {
        const correctedText = document.getElementById('corrected-text');
        const changesList = document.getElementById('grammar-changes-list');
        correctedText.textContent = corrected;
        changesList.innerHTML = '';
        (changes || []).forEach(c => {
            const li = document.createElement('li');
            li.textContent = c;
            changesList.appendChild(li);
        });
        box.classList.remove('hidden');
    } else {
        box.classList.add('hidden');
    }
}

function addChatMessage(role, content) {
    const chatBox = document.getElementById('chat-box');
    const msg = document.createElement('div');
    msg.className = `chat-message ${role}`;
    const safeContent = escapeHtml(content);
    msg.innerHTML = `
        <div class="role-label">${role === 'user' ? 'T\u00fa' : 'Tutor'}</div>
        <div>${safeContent}</div>
        <button onclick="speak('${safeContent.replace(/'/g, "\\'")}')" class="btn-speak-msg" title="Escuchar">\u{1F50A}</button>
    `;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    state.chatHistory.push({ role, content });
}

function trackVocabulary(text) {
    if (!state.currentModule && !state.currentTopic) return;
    const vocabSet = new Set(
        (state.currentModule?.vocabulary || state.currentTopic?.vocabulary || []).map(v => v.toLowerCase())
    );
    const words = text.toLowerCase().split(/\W+/);
    words.forEach(w => {
        if (vocabSet.has(w)) state.usedVocabulary.add(w);
    });
    updateVocabTracker();
}

function updateVocabTracker() {
    const container = document.getElementById('vocab-tracker');
    const vocab = state.currentModule?.vocabulary || state.currentTopic?.vocabulary || [];
    if (vocab.length === 0) {
        container.innerHTML = '<p class="text-muted" style="font-size:0.8rem">Selecciona un tema</p>';
        return;
    }
    container.innerHTML = vocab.map(v => {
        const used = state.usedVocabulary.has(v.toLowerCase());
        return `<span class="vocab-tag ${used ? 'vocab-used' : ''}">${used ? '\u2705' : '\u25CB'} ${v}</span>`;
    }).join(' ');
}

window.suggestPhrase = function () {
    if (!state.currentTopic || state.currentTopic.key_phrases.length === 0) return;
    const unused = state.currentTopic.key_phrases.filter(p => {
        const words = p.toLowerCase().split(/\W+/);
        return !words.some(w => state.usedVocabulary.has(w));
    });
    const pool = unused.length > 0 ? unused : state.currentTopic.key_phrases;
    const phrase = pool[Math.floor(Math.random() * pool.length)];
    addChatMessage('assistant', 'Try saying: "' + phrase + '"');
    speak('Try saying: ' + phrase);
};
async function loadConjugations() {
    try {
        const [verbs, tensesData] = await Promise.all([api.getVerbs(), api.getTenses()]);
        const verbSelect = document.getElementById('verb-select');
        const uniqueVerbs = [...new Set(verbs.map(v => v.verb))];
        verbSelect.innerHTML = uniqueVerbs.map(v => `<option value="${v}">${v}</option>`).join('');

        const tenseSelect = document.getElementById('tense-select');
        const tenseNames = {
            present_simple: 'Present Simple', present_continuous: 'Present Continuous',
            present_perfect: 'Present Perfect', past_simple: 'Past Simple',
            past_continuous: 'Past Continuous', future_simple: 'Future Simple',
            conditional: 'Conditional',
        };
        tenseSelect.innerHTML = Object.entries(tenseNames).map(([k, v]) =>
            `<option value="${k}">${v}</option>`
        ).join('');

        document.getElementById('tense-list').innerHTML =
            Object.entries(tensesData).map(([key, d]) => `
                <div class="tense-card">
                    <h4>${tenseNames[key] || key}</h4>
                    <p>${d.description}</p>
                    <div class="formula">${d.formula}</div>
                    <ul>${d.examples.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
                </div>
            `).join('');

        await loadConjugationTable();
    } catch (err) { console.error('Conjugations error:', err); }
}

async function loadConjugationTable() {
    const verb = document.getElementById('verb-select').value;
    const tense = document.getElementById('tense-select').value;
    if (!verb) return;
    const container = document.getElementById('conjugation-table-container');

    try {
        const data = await api.getVerb(verb, tense);
        if (!data.conjugations || Object.keys(data.conjugations).length === 0) {
            container.innerHTML = '<p class="text-muted">No hay datos para esta combinaci\u00f3n.</p>';
            return;
        }

        const tenseNames = {
            present_simple: 'Present Simple', present_continuous: 'Present Continuous',
            present_perfect: 'Present Perfect', past_simple: 'Past Simple',
            past_continuous: 'Past Continuous', future_simple: 'Future Simple',
            conditional: 'Conditional',
        };

        let html = `
            <div class="card" style="margin-bottom:16px;">
                <h3>${verb} - ${tenseNames[tense] || tense}</h3>
                <table class="conjugation-table">
                    <thead><tr><th>Pronombre</th><th>Verbo conjugado</th></tr></thead>
                    <tbody>`;

        ['I', 'you', 'he/she/it', 'we', 'they'].forEach(p => {
            if (data.conjugations[p]) {
                html += `<tr><td><strong>${p}</strong></td><td>${data.conjugations[p]}</td></tr>`;
            }
        });

        html += `</tbody></table>
            ${data.examples.length ? `<h4>Ejemplos:</h4><ul>${data.examples.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul>` : ''}
            </div>`;
        container.innerHTML = html;
    } catch { container.innerHTML = '<p class="text-muted">Error al cargar conjugaci\u00f3n.</p>'; }
}

// --- Tests ---
async function loadTests() {
    try {
        const tests = await api.getTests();
        document.getElementById('test-module-select').innerHTML = tests.map(t => `
            <div class="test-module-btn" onclick="selectTest('${t.module_id}')">
                <strong>${MODULE_NAMES[t.module_id] || t.module_id}</strong>
                <p class="text-muted">${t.questions.length} preguntas | Pasa con ${Math.round(t.passing_score * 100)}%</p>
            </div>`).join('');
    } catch (err) { console.error(err); }
}

async function selectTest(moduleId) {
    try {
        const test = await api.getModuleTest(moduleId);
        state.selectedTestModule = moduleId;
        state.testAnswers = {};

        document.querySelectorAll('.test-module-btn').forEach(b => b.classList.remove('active'));
        document.querySelector(`.test-module-btn[onclick*="'${moduleId}'"]`)?.classList.add('active');

        document.getElementById('test-container').classList.remove('hidden');
        document.getElementById('test-result').classList.add('hidden');
        document.getElementById('test-title').textContent = MODULE_NAMES[moduleId] || moduleId;

        document.getElementById('test-questions').innerHTML = test.questions.map((q, i) => `
            <div class="question-card" data-qid="${q.id}">
                <div><span class="q-number">${i + 1}</span><span class="q-text">${escapeHtml(q.question)}</span></div>
                <div class="options">
                    ${(q.options || []).map(opt => {
                        const val = escapeHtml(opt).replace(/'/g, "\\'");
                        return `<label class="option">
                            <input type="radio" name="q-${q.id}" value="${escapeHtml(opt)}"
                                onchange="recordAnswer('${q.id}', '${val}')">
                            <span>${escapeHtml(opt)}</span>
                        </label>`;
                    }).join('')}
                </div>
            </div>`).join('');
        document.getElementById('btn-submit-test').disabled = false;
    } catch (err) { console.error(err); }
}

window.recordAnswer = function (qId, answer) { state.testAnswers[qId] = answer; };

async function submitTest() {
    if (!state.selectedTestModule) return;
    const btn = document.getElementById('btn-submit-test');
    btn.disabled = true; btn.textContent = 'Evaluando...';
    try {
        const result = await api.submitTest(state.selectedTestModule, state.testAnswers);
        displayTestResult(result);
    } catch { alert('Error al enviar el test.'); btn.disabled = false; btn.textContent = 'Enviar respuestas'; }
}

function displayTestResult(result) {
    document.getElementById('test-container').classList.add('hidden');
    document.getElementById('test-result').classList.remove('hidden');

    document.getElementById('result-title').textContent = `${MODULE_NAMES[result.module_id] || result.module_id} - Resultado`;
    document.getElementById('result-title').style.color = result.passed ? 'var(--accent)' : 'var(--danger)';
    document.getElementById('result-score').textContent = `${Math.round(result.score * 100)}%`;
    document.getElementById('result-score').style.color = result.passed ? 'var(--accent)' : 'var(--danger)';
    document.getElementById('result-message').textContent = result.message;

    const details = document.getElementById('result-details');
    details.innerHTML = '<h4>Detalle de respuestas:</h4>';
    result.results.forEach(r => {
        const div = document.createElement('div');
        div.className = `result-detail ${r.is_correct ? 'correct' : 'incorrect'}`;
        div.innerHTML = `
            <strong>${escapeHtml(r.question)}</strong><br>
            ${r.is_correct
                ? '<span>\u2705 Correcto</span>'
                : `<span>\u274C Tu respuesta: "${escapeHtml(r.user_answer)}" - Correcta: "${escapeHtml(r.correct_answer)}"</span>`}
            <br><em>${escapeHtml(r.explanation)}</em>`;
        details.appendChild(div);
    });

    if (result.passed) { api.completeMyModule(result.module_id); }
    api.updateMyScore(result.module_id, result.score);
}

window.resetTestView = function () {
    document.getElementById('test-result').classList.add('hidden');
    document.getElementById('test-container').classList.add('hidden');
    state.selectedTestModule = null; state.testAnswers = {};
    loadTests();
};

// --- Progress ---
async function loadProgress() {
    try {
        const [progress, recs] = await Promise.all([
            api.getMyProgress(),
            api.getMyRecommendations(),
        ]);

        const pct = Math.round((progress.completed_modules.length / 8) * 100);
        document.getElementById('progress-bar').style.width = `${pct}%`;
        document.getElementById('progress-percent').textContent = `${pct}%`;

        const cd = document.getElementById('completed-list');
        if (progress.completed_modules.length === 0) {
            cd.innerHTML = '<p class="text-muted">Ninguno a\u00fan.</p>';
        } else {
            cd.innerHTML = progress.completed_modules.map(m =>
                `<p>\u2705 ${MODULE_NAMES[m] || m}</p>`).join('');
        }

        renderScoresChart(progress);
        renderProgressPie(progress);

        document.getElementById('recommendations').innerHTML = `
            <p><strong>M\u00f3dulo actual:</strong> ${recs.current_module}</p>
            <p><strong>Recomendaci\u00f3n:</strong> ${recs.next_recommendation}</p>
            ${recs.modules_to_review.length ? `<p><strong>M\u00f3dulos a repasar:</strong> ${recs.modules_to_review.join(', ')}</p>` : ''}
            <p><strong>Sesiones:</strong> ${recs.practice_sessions} | <strong>Tiempo:</strong> ${recs.total_practice_minutes} min</p>`;
    } catch (err) { console.error('Progress error:', err); }
}

function renderScoresChart(progress) {
    const canvas = document.getElementById('scores-chart');
    if (!canvas) return;
    if (state.charts.scores) state.charts.scores.destroy();

    const scores = progress.test_scores || {};
    const labels = [];
    const data = [];
    const colors = [];

    MODULE_LIST.forEach(m => {
        if (scores[m] !== undefined) {
            labels.push((MODULE_NAMES[m] || m).substring(0, 15));
            const v = Math.round(scores[m] * 100);
            data.push(v);
            colors.push(v >= 70 ? '#10b981' : v >= 40 ? '#f59e0b' : '#ef4444');
        }
    });

    if (data.length === 0) {
        labels.push('Sin datos');
        data.push(0);
        colors.push('#94a3b8');
    }

    state.charts.scores = new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Puntaje (%)', data, backgroundColor: colors, borderRadius: 6 }] },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderProgressPie(progress) {
    const canvas = document.getElementById('progress-chart-pie');
    if (!canvas) return;
    if (state.charts.pie) state.charts.pie.destroy();

    const completed = progress.completed_modules.length;
    const remaining = 8 - completed;

    state.charts.pie = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Completados', 'Pendientes'],
            datasets: [{
                data: [completed, remaining],
                backgroundColor: ['#10b981', '#e2e8f0'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true } }
            }
        }
    });
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}
