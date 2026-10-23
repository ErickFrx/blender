# PERÚ RACING — taller 3D con Blender en GitHub Actions

Este repositorio se utiliza para producir y revisar modelos 3D para **PERÚ RACING: CALLES SIN LEY**. No instala Blender en tu laptop.

## Cómo usarlo
1. Abre **Actions → Blender para PERÚ RACING**.
2. Selecciona **Run workflow** en la rama main. También se ejecuta al añadir o modificar scripts.
3. Abre el resultado y descarga **peru-racing-modelos-3d** desde la sección Artifacts.
4. Extrae las imágenes PNG y comprueba la calidad visual antes de incorporar los archivos GLB al juego.

La automatización instala Blender en ubuntu-24.04, genera tres fachadas genéricas de prueba (tienda, casa y esquina), renderiza previews, exporta GLB y valida los resultados.

**Atención:** son modelos de prueba del proceso de producción, **no reproducciones auténticas de San Vicente**. La próxima fase requerirá referencias fotográficas y modelos específicos. No pongas contraseñas ni archivos privados en este repositorio público.

## Archivos
- `tools/generar_fachadas.py`: generación 3D con bpy, exportación GLB y render PNG.
- `tests/validar.py`: verifica el encabezado y JSON interno GLB, las imágenes PNG y el manifest.
- `.github/workflows/blender.yml`: instalación en la nube, renderizado y descarga de modelos.
