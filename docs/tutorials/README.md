# Tutoriales de OpenAI Apps SDK con Python

Esta carpeta contiene tutoriales paso a paso para aprender a construir aplicaciones con OpenAI Apps SDK usando Python.

## Tutoriales Disponibles

### 1. [Tutorial Hola Mundo](./hello-world-tutorial.md) 🎯 ¡EMPIEZA AQUÍ!

**Nivel**: Principiante absoluto
**Tiempo**: 30-45 minutos
**Tipo**: Tutorial de introducción básica

Este tutorial te enseña:
- ✅ Qué es MCP y cómo funciona (conceptos básicos)
- ✅ Crear tu primera herramienta MCP simple
- ✅ Entender JSON-RPC 2.0 y el protocolo MCP
- ✅ Configurar entorno con Nix
- ✅ Conectar con ChatGPT en minutos
- ✅ Probar con ngrok

**Ideal para**:
- Tu primer contacto con OpenAI Apps SDK
- Entender los conceptos fundamentales rápidamente
- Ver el flujo completo en 30 minutos
- Desarrolladores que prefieren empezar con algo simple

### 2. [Tutorial de Widgets Interactivos](./widgets-tutorial.md) 🎨 ¡NUEVO!

**Nivel**: Intermedio
**Tiempo**: 30-45 minutos
**Tipo**: Continuación del Hola Mundo
**Prerequisito**: Tutorial Hola Mundo completado

Este tutorial te enseña:
- ✅ Crear widgets HTML que ChatGPT puede mostrar
- ✅ Usar `@mcp.resource()` para registrar recursos
- ✅ Entender el MIME type `text/html+skybridge`
- ✅ Usar la API `window.openai.callTool()` desde JavaScript
- ✅ Evolución de widgets: estático → dinámico → interactivo
- ✅ Diseñar interfaces atractivas con CSS
- ✅ Manejar estado e historial en widgets

**Ideal para**:
- Completar tu conocimiento después del Hola Mundo
- Aprender a crear interfaces visuales para ChatGPT
- Entender el flujo bidireccional: Widget ↔ MCP
- Desarrolladores que quieren crear UIs interactivas

### 3. [Tutorial de ToDo App](./todo-app-tutorial.md) ⭐ App completa

**Nivel**: Principiante a Intermedio
**Tiempo**: 90-120 minutos
**Tipo**: Exploración y extensión de app existente

Este tutorial te enseña a:
- ✅ Entender una aplicación MCP completa en Python
- ✅ Ejecutar y probar el servidor localmente
- ✅ Conectar con ChatGPT vía OpenAI Platform
- ✅ Extender la aplicación con nuevas funcionalidades
- ✅ Escribir tests con pytest
- ✅ Deploy con ngrok

**Ideal para**: Aprender con una aplicación funcional que puedes explorar, modificar y extender.

### 4. [Tutorial de Notes App](./notes-app-tutorial.md) 🆕 ¡MEJORADO!

**Nivel**: Principiante
**Tiempo**: 2-3 horas (dividido en 2 partes)
**Tipo**: Construcción desde cero con enfoque evolutivo

**NUEVO**: Este tutorial ha sido completamente renovado con:
- 📚 **Explicaciones paso a paso** de cada archivo
- 🎯 **Enfoque evolutivo** para widgets (simple → complejo)
- 🔧 **Node.js incluido** en configuración Nix
- 💡 **Comentarios explicativos** en cada sección
- 📖 **Dos partes** para mejor organización

**Parte 1** ([notes-app-tutorial.md](./notes-app-tutorial.md)) te enseña a:
- ✅ Entender qué es MCP y cómo funciona
- ✅ Crear entorno reproducible con Nix (paso a paso)
- ✅ Configurar `flake.nix` con explicaciones detalladas
- ✅ Crear `justfile`, `pyproject.toml` paso a paso
- ✅ Implementar modelos Pydantic con explicaciones
- ✅ Crear capa de almacenamiento CRUD
- ✅ Implementar servidor MCP básico (sin widgets)
- ✅ Configurar `main.py` y archivos `.env`

**Parte 2** ([notes-app-tutorial-part2.md](./notes-app-tutorial-part2.md)) te enseña a:
- ✅ Crear widgets evolutivamente en 5 versiones:
  - Versión 1: HTML estático (fundamentos)
  - Versión 2: Datos dinámicos (integración)
  - Versión 3: Estilos CSS (diseño)
  - Versión 4: Interactividad básica (window.openai)
  - Versión 5: Versión final pulida (UX completa)
- ✅ Usar la API `window.openai` para llamar herramientas
- ✅ Implementar resource handlers
- ✅ Crear múltiples widgets

**Ideal para**:
- Aprender construyendo desde cero con explicaciones profundas
- Entender el "por qué" de cada decisión de diseño
- Ver la evolución de código simple a complejo
- Desarrolladores que prefieren aprender paso a paso

**Ver**: [Tutorial README](./README-notes-tutorial.md) para guía completa de uso

## ¿Cuál tutorial elegir?

### Empieza con Hola Mundo si...
- **Es tu primer contacto con MCP** 🎯
- Quieres entender lo básico en menos de 1 hora
- Prefieres ver algo funcionar rápidamente
- Necesitas entender el flujo antes de profundizar
- **Recomendado para todos los principiantes**

### Continúa con Widgets si...
- Ya completaste el Hola Mundo 🎨
- Quieres agregar interfaces visuales a tu app
- Te interesa la interactividad con `window.openai`
- Quieres aprender diseño de widgets paso a paso
- **Progresión natural después del Hola Mundo**

### Explora ToDo App si...
- Ya hiciste Hola Mundo + Widgets (o entiendes MCP básico)
- Quieres ver una app completa funcionando
- Prefieres aprender explorando código existente
- Te interesa ver patrones y mejores prácticas en acción
- Quieres extender una base sólida con CRUD

### Profundiza con Notes App si...
- Prefieres construir todo desde cero con explicaciones detalladas
- Quieres entender cada línea de código y el "por qué"
- Te gusta ver la evolución de simple a complejo
- Tienes 2-3 horas para un tutorial profundo

## Ruta de Aprendizaje Recomendada

### Para Principiantes Absolutos (Ruta Completa)

```
1. Tutorial Hola Mundo (30 min) ← ¡EMPIEZA AQUÍ!
   ↓ (aprende herramientas MCP básicas)
2. Tutorial de Widgets (45 min) ← ¡NUEVO!
   ↓ (agrega interfaces visuales)
3. Tutorial de ToDo App (90 min)
   ↓ (ve una app completa con CRUD)
4. Documentación EXPLANATION.md
   ↓ (conceptos profundos)
5. Tutorial de Notes App (opcional, construcción desde cero)
   ↓
6. Documentación GUIDE.md (referencia)
   ↓
7. Tu propia aplicación 🚀
```

### Para Desarrolladores con Experiencia en APIs

```
1. Tutorial Hola Mundo (20 min) - Conceptos MCP
   ↓
2. Tutorial de Widgets (30 min) - Interfaces interactivas
   ↓
3. Tutorial de ToDo App (60 min) - Patrones completos
   ↓
4. Tu propia aplicación 🚀
```

### Ruta Express (Mínimo Viable)

```
1. Tutorial Hola Mundo (30 min)
   ↓
2. Tutorial de Widgets (30 min)
   ↓
3. ¡Listo para construir tu primera app! 🚀
```

## Estructura de los Tutoriales

Cada tutorial sigue la metodología **Diataxis** para documentación:

- **Learning-oriented**: Enfocado en el aprendizaje progresivo
- **Hands-on**: Ejercicios prácticos en cada paso
- **Checkpoints**: Verificaciones para confirmar progreso
- **Conceptos claros**: Explicaciones del "por qué" además del "cómo"

## Prerrequisitos para Todos los Tutoriales

### Opción 1: Con Nix (Recomendado) ⭐

Si usas Nix, solo necesitas:
- **[Nix con flakes habilitados](https://nixos.org/download.html)**
- **Editor de código** (VS Code recomendado)
- **Cuenta en [ngrok](https://ngrok.com)** (gratuita)

Nix te proporcionará automáticamente:
- ✅ Python 3.11
- ✅ uv (gestor de paquetes)
- ✅ just (command runner)
- ✅ ngrok
- ✅ git y curl

**Setup rápido**:
```bash
# Habilitar flakes
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Clonar proyecto y entrar al entorno
git clone <url-del-repositorio>
cd openai-todo-app
nix develop
```

### Opción 2: Instalación Manual

Si prefieres no usar Nix:
- Python 3.10 o superior
- Git
- Editor de código (VS Code recomendado)
- Terminal (bash/zsh)
- Cuenta en ngrok (gratuita)
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python
- [just](https://github.com/casey/just) - Command runner

### Conocimientos
- Python básico (funciones, clases)
- HTTP y APIs REST (conceptos básicos)
- JSON (formato de datos)

No te preocupes si no dominas estos temas - los tutoriales explican conforme avanzas.

## Recursos Complementarios

### Documentación Principal
- `../docs/EXPLANATION.md` - Conceptos profundos y arquitectura
- `../docs/GUIDE.md` - Guía de referencia para tareas específicas
- `../OPENAI_APPS_SDK.md` - Setup y configuración detallada

### Referencias Externas
- [MCP Specification](https://modelcontextprotocol.io/)
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Ayuda y Soporte

Si encuentras problemas:

1. **Revisa el Troubleshooting**: Cada tutorial tiene su sección
2. **Consulta GUIDE.md**: Soluciones a problemas comunes
3. **Verifica tu setup**: Asegúrate que Python, uv y dependencias están instaladas
4. **Revisa los logs**: Los errores suelen dar pistas claras

## Contribuir

¿Encontraste un error o tienes una sugerencia?
- Abre un issue en el repositorio
- Propón mejoras vía pull request

---

**¡Feliz aprendizaje!** 🚀

**Comienza aquí**:
1. [Tutorial Hola Mundo](./hello-world-tutorial.md) → (30 min, perfecto para empezar)
2. [Tutorial de Widgets](./widgets-tutorial.md) → (45 min, agrega UIs interactivas)
