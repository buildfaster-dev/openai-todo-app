# Documentación de OpenAI ToDo App

Esta carpeta contiene la documentación completa del proyecto, organizada según el framework **Diataxis**.

## 📚 Estructura de la Documentación

Este proyecto sigue el [framework Diataxis](https://diataxis.fr/) para organizar la documentación en cuatro tipos distintos, cada uno con un propósito específico:

```
┌─────────────────────────────────────────────────────┐
│                    DIATAXIS                         │
│                                                     │
│         Learning              Understanding         │
│      ┌──────────────┐      ┌──────────────┐       │
│      │   TUTORIAL   │      │ EXPLANATION  │       │
│      │              │      │              │       │
│      └──────────────┘      └──────────────┘       │
│                                                     │
│         Doing                 Information          │
│      ┌──────────────┐      ┌──────────────┐       │
│      │    GUIDE     │      │  REFERENCE   │       │
│      │              │      │              │       │
│      └──────────────┘      └──────────────┘       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 📖 Documentos Disponibles

### 1. [EXPLANATION.md](./EXPLANATION.md) - Entendimiento 🧠

**Propósito**: Explicar conceptos, arquitectura y el "por qué"
**Cuándo leer**: Cuando quieres entender cómo y por qué funciona algo

**Contenido**:
- Introducción a OpenAI Apps SDK y MCP
- Filosofía y principios de diseño
- Arquitectura completa del sistema
- Flujos de comunicación detallados
- Decisiones de diseño explicadas
- Por qué Python es ideal para MCP
- Comparaciones con alternativas

**Ideal para**: Desarrolladores que buscan comprensión profunda antes o después de implementar.

### 2. [GUIDE.md](./GUIDE.md) - Referencia de Tareas 🛠️

**Propósito**: Resolver problemas específicos y realizar tareas concretas
**Cuándo leer**: Cuando tienes un problema específico que resolver

**Contenido**:
- Configuración y setup (entornos, variables, puertos)
- Herramientas MCP (agregar, validar, manejar errores)
- Widgets (crear, hacer interactivos, estilos)
- Integración con OpenAI (configurar, testing, actualizar)
- Testing y debugging (logs, tests, CORS)
- Despliegue (Railway, PostgreSQL, producción)
- Troubleshooting (problemas comunes y soluciones)

**Ideal para**: Consulta rápida cuando necesitas hacer algo específico.

## 📦 Documentación Adicional del Proyecto

Además de esta documentación técnica, el proyecto incluye:

### 3. Tutoriales - Aprendizaje 📝

Los tutoriales están en la carpeta `tutorials/`:

#### [ToDo App Tutorial](./tutorials/todo-app-tutorial.md) ⭐
- **Nivel**: Principiante a Intermedio
- **Tiempo**: 90-120 minutos
- Explora y extiende la aplicación existente
- 20 pasos progresivos con checkpoints
- Incluye extensión y testing

#### [Notes App Tutorial](./tutorials/notes-app-tutorial.md)
- **Nivel**: Principiante
- **Tiempo**: 60-90 minutos
- Construye una aplicación desde cero
- 10 pasos fundamentales
- Enfoque en conceptos básicos

Ver [tutorials/README.md](./tutorials/README.md) para más detalles.

## 🔧 Setup del Entorno de Desarrollo

Este proyecto utiliza **Nix con flakes** para proporcionar un entorno de desarrollo completamente reproducible. Esto garantiza que todos los desarrolladores trabajen con las mismas versiones de herramientas y dependencias.

### Opción 1: Setup con Nix (Recomendado) ⭐

**Prerrequisitos**: [Instalar Nix con soporte para flakes](https://nixos.org/download.html)

```bash
# Habilitar flakes (si aún no lo has hecho)
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Entrar al entorno de desarrollo
nix develop

# El shell te mostrará las versiones instaladas:
# - Python 3.11
# - uv (gestor de paquetes)
# - just (command runner)
# - ngrok (tunneling)
```

**Beneficios de usar Nix**:
- ✅ Entorno completamente reproducible
- ✅ Sin conflictos con instalaciones del sistema
- ✅ Todas las herramientas en las versiones correctas
- ✅ Setup instantáneo (después de la primera vez)
- ✅ Funciona igual en Linux, macOS y WSL

**Siguiente paso**: Una vez en el shell de Nix, ejecuta:
```bash
just install  # Instala las dependencias Python
just dev      # Inicia el servidor de desarrollo
```

### Opción 2: Setup Manual

Si prefieres no usar Nix, necesitas instalar manualmente:

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python
- [just](https://github.com/casey/just) - Command runner
- [ngrok](https://ngrok.com/) - Para exponer tu servidor local

Ver instrucciones detalladas en [GUIDE.md § Configuración y Setup](./GUIDE.md#configuración-y-setup).

---

## 🗺️ Rutas de Aprendizaje

### Para Principiantes

```
0. Setup con Nix (5 minutos)
   ↓
1. tutorials/todo-app-tutorial.md
   ↓ (familiarízate con la app)
2. EXPLANATION.md
   ↓ (entiende los conceptos)
3. tutorials/notes-app-tutorial.md
   ↓ (construye desde cero)
4. GUIDE.md
   ↓ (referencia cuando necesites)
5. Tu propia aplicación
```

### Para Desarrolladores Experimentados

```
1. EXPLANATION.md (arquitectura completa)
   ↓
2. tutorials/todo-app-tutorial.md (ver implementación)
   ↓
3. GUIDE.md (bookmark para referencia)
   ↓
4. Tu aplicación
```

### Para Resolver un Problema Específico

```
1. GUIDE.md (busca tu problema)
   ↓
2. Si no está claro → EXPLANATION.md (contexto)
   ↓
3. Si necesitas práctica → tutorials/
```

## 🎯 Cómo Usar Esta Documentación

### Si quieres...

**...entender cómo funciona MCP**
→ Lee [EXPLANATION.md](./EXPLANATION.md)

**...aprender haciendo desde cero**
→ Sigue [tutorials/notes-app-tutorial.md](./tutorials/notes-app-tutorial.md)

**...explorar una app completa**
→ Sigue [tutorials/todo-app-tutorial.md](./tutorials/todo-app-tutorial.md)

**...resolver un problema específico**
→ Consulta [GUIDE.md](./GUIDE.md)

**...agregar una nueva herramienta MCP**
→ [GUIDE.md § Cómo agregar una nueva herramienta](./GUIDE.md#cómo-agregar-una-nueva-herramienta)

**...crear un widget interactivo**
→ [GUIDE.md § Cómo hacer un widget interactivo](./GUIDE.md#cómo-hacer-un-widget-interactivo)

**...entender por qué usar Python**
→ [EXPLANATION.md § ¿Por qué Python para MCP?](./EXPLANATION.md#por-qué-python-para-mcp)

**...desplegar a producción**
→ [GUIDE.md § Despliegue y Producción](./GUIDE.md#despliegue-y-producción)

**...debuggear problemas**
→ [GUIDE.md § Troubleshooting](./GUIDE.md#troubleshooting)

## 🔍 Índice por Tema

### Python y Desarrollo
- **Setup**: GUIDE.md § Configuración y Setup
- **Pydantic**: EXPLANATION.md § Modelo de Datos
- **Type Hints**: EXPLANATION.md § Por qué Python
- **Testing**: GUIDE.md § Testing y Debugging
- **uv/pip**: GUIDE.md § Cómo usar uv

### MCP y Protocolo
- **Conceptos básicos**: EXPLANATION.md § Model Context Protocol
- **Herramientas**: EXPLANATION.md § Herramientas y Capacidades
- **JSON-RPC**: EXPLANATION.md § Comunicación y Transporte
- **Agregar tools**: GUIDE.md § Herramientas MCP

### Widgets y UI
- **Arquitectura**: EXPLANATION.md § Widgets e Interfaces de Usuario
- **Crear widgets**: GUIDE.md § Widgets e Interfaz
- **Interactividad**: GUIDE.md § Cómo hacer un widget interactivo
- **Estilos**: GUIDE.md § Cómo estilizar un widget

### Integración
- **OpenAI Platform**: GUIDE.md § Integración con OpenAI
- **ngrok**: tutorials/todo-app-tutorial.md § Paso 13
- **CORS**: GUIDE.md § Cómo debuggear problemas de CORS
- **PUBLIC_URL**: GUIDE.md § Troubleshooting

### Producción
- **Deploy**: GUIDE.md § Despliegue y Producción
- **Databases**: GUIDE.md § Cómo usar PostgreSQL
- **Monitoring**: GUIDE.md § Cómo agregar logging

## 📦 Documentación Adicional del Proyecto

Además de esta documentación técnica, el proyecto incluye:

### En la raíz del proyecto:
- `README.md` - Overview general del proyecto
- `OPENAI_APPS_SDK.md` - Guía específica de setup de OpenAI Apps SDK
- `OPENAI_SETUP.md` - Instrucciones de configuración de OpenAI
- `CONTRIBUTING.md` - Guía para contribuidores
- `SETUP_STATUS.md` - Estado actual del setup

### Código fuente:
- `src/todo_app/` - Código fuente con docstrings detallados
- `tests/` - Tests con ejemplos de uso

## 🌐 Recursos Externos

### MCP y OpenAI
- [Model Context Protocol](https://modelcontextprotocol.io/) - Especificación oficial
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - SDK oficial
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/) - Documentación de OpenAI
- [OpenAI Apps Examples](https://github.com/openai/openai-apps-sdk-examples) - Ejemplos oficiales

### Python y Herramientas
- [Pydantic](https://docs.pydantic.dev/) - Validación de datos
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes
- [pytest](https://docs.pytest.org/) - Testing

### Framework de Documentación
- [Diataxis](https://diataxis.fr/) - Framework de documentación usado aquí

## 🤝 Contribuir a la Documentación

Si encuentras:
- ❌ Errores o información desactualizada
- 🔍 Temas que faltan o no están claros
- 💡 Sugerencias de mejora

Por favor:
1. Abre un issue describiendo el problema
2. O envía un pull request con la corrección
3. Consulta `CONTRIBUTING.md` para guías de estilo

## 📝 Notas sobre Esta Documentación

### Principios Diataxis Aplicados

**Separation of Concerns**: Cada tipo de documento tiene un propósito específico y no se mezclan.

- ❌ NO encontrarás explicaciones conceptuales en GUIDE.md
- ❌ NO encontrarás instrucciones paso a paso en EXPLANATION.md
- ✅ Cada documento hace una cosa y la hace bien

**User-First**: Organizado por las necesidades del lector, no por la estructura del código.

**Clear Paths**: Referencias cruzadas guían al lector al documento correcto para su necesidad.

### Lenguaje y Estilo

- **Python 3.10+**: Todo el código usa Python moderno
- **Ejemplos reales**: Basados en el código actual del proyecto
- **Claridad**: Preferimos ser claros antes que concisos
- **Progresivo**: De simple a complejo

---

**¿Por dónde empezar?**

Si es tu primera vez: [tutorials/todo-app-tutorial.md](./tutorials/todo-app-tutorial.md)

Si quieres entender: [EXPLANATION.md](./EXPLANATION.md)

Si necesitas hacer algo: [GUIDE.md](./GUIDE.md)

---

¡Feliz aprendizaje! 🚀
