# Tutoriales de OpenAI Apps SDK con Python

Esta carpeta contiene tutoriales paso a paso para aprender a construir aplicaciones con OpenAI Apps SDK usando Python.

## Tutoriales Disponibles

### 1. [Tutorial de ToDo App](./todo-app-tutorial.md) ⭐ Empieza aquí

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

### 2. [Tutorial de Notes App](./notes-app-tutorial.md) 🆕 ¡MEJORADO!

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

### Empieza con ToDo App si...
- Quieres ver una app completa funcionando
- Prefieres aprender explorando código existente
- Te interesa ver patrones y mejores prácticas en acción
- Quieres extender una base sólida

### Empieza con Notes App si...
- Prefieres construir todo desde cero
- Quieres entender cada línea de código
- Es tu primer proyecto con MCP
- Prefieres un enfoque más simple y directo

## Ruta de Aprendizaje Recomendada

```
1. Tutorial de ToDo App (aquí)
   ↓
2. Documentación EXPLANATION.md
   ↓
3. Tutorial de Notes App (construcción desde cero)
   ↓
4. Documentación GUIDE.md (referencia)
   ↓
5. Tu propia aplicación
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

Comienza con [Tutorial de ToDo App](./todo-app-tutorial.md) →
