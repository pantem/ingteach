# English Learning App

Aplicación web para aprender inglés con práctica de conversación, reconocimiento de voz, conjugación de verbos y tests por módulos.

## Stack

- **Frontend:** HTML, CSS, JavaScript vanilla (Web Speech API)
- **Backend:** Python + FastAPI + Motor (MongoDB async)
- **Base de datos:** MongoDB Atlas (conexión vía `MONGO_URI`)

## Requisitos

- Python 3.10+
- Navegador Chrome o Edge (Web Speech API)
- Conexión a internet (MongoDB Atlas + Web Speech API)

## Instalación

```bash
# 1. Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# 2. (Opcional) Configurar variable de entorno para MongoDB
#    Por defecto usa: mongodb+srv://seshomaru:P4nqu3s1t0@logis.2m8j0.mongodb.net/teachlang
#    Para sobrescribir:
#    set MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/teachlang
```

## Ejecución

### Terminal 1 - Backend (API)

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

La API corre en `http://localhost:8000`

### Terminal 2 - Frontend

```bash
cd frontend
python -m http.server 5500
```

Abrir `http://localhost:5500` en el navegador.

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/modules/` | Todos los módulos |
| GET | `/api/modules/{id}` | Módulo por ID |
| GET | `/api/modules/level/{level}` | Módulos por nivel |
| GET | `/api/conversation/topics` | Temas de conversación |
| GET | `/api/conversation/topics/{id}` | Tema por ID |
| POST | `/api/conversation/chat/{topic_id}` | Enviar mensaje en chat |
| POST | `/api/conversation/evaluate` | Evaluar transcripción de voz |
| GET | `/api/conjugations/verbs` | Todos los verbos conjugados |
| GET | `/api/conjugations/verbs/{verb}` | Conjugación de un verbo |
| GET | `/api/conjugations/tenses` | Guía de tiempos verbales |
| GET | `/api/tests/` | Todos los tests |
| GET | `/api/tests/{module_id}` | Test de un módulo |
| POST | `/api/tests/submit/{module_id}` | Enviar respuestas del test |
| GET | `/api/progress/{user_id}` | Progreso del usuario |
| POST | `/api/progress/{user_id}/complete-module/{module_id}` | Completar módulo |
| POST | `/api/progress/{user_id}/update-score` | Actualizar score de test |
| POST | `/api/progress/{user_id}/practice-session` | Registrar sesión de práctica |
| GET | `/api/progress/{user_id}/recommendations` | Recomendaciones |

## Estructura del proyecto

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── modules.py       # Módulos de aprendizaje
│   │   │   ├── conversation.py  # Chat y evaluación de voz
│   │   │   ├── conjugations.py  # Conjugación de verbos
│   │   │   ├── tests.py         # Tests por módulo
│   │   │   └── progress.py      # Progreso del usuario (MongoDB)
│   │   ├── models/
│   │   │   └── learning.py      # Modelos Pydantic
│   │   ├── database.py          # Conexión MongoDB
│   │   └── main.py              # Punto de entrada FastAPI
│   └── requirements.txt
├── frontend/
│   ├── index.html               # SPA principal
│   ├── css/
│   │   └── style.css            # Estilos completos
│   └── js/
│       ├── api.js               # Cliente HTTP para la API
│       └── app.js               # Lógica de la aplicación
└── README.md
```

## Mecanismo de aprendizaje

1. **Módulos**: 8 módulos en 3 niveles (beginner, intermediate, advanced). Cada uno contiene vocabulario, frases clave, y un enfoque gramatical.

2. **Conversación**: Seleccionas un tema y practicas con un tutor AI por texto o voz. La Web Speech API transcribe tu voz y el backend evalúa:
   - **Precisión**: qué tanto coincide tu frase con las frases clave del tema
   - **Pronunciación**: calidad fonética estimada
   - **Fluidez**: longitud y completitud de la oración

3. **Conjugación de verbos**: 12 verbos irregulares conjugados en 7 tiempos verbales con ejemplos y guía gramatical.

4. **Tests**: Cada módulo tiene un test de 5 preguntas. Se necesita 70% para aprobar.

5. **Progreso**: Al aprobar un test, el módulo se marca como completado y avanzas al siguiente. Los scores bajos quedan registrados para repaso. Todo se guarda en MongoDB.
