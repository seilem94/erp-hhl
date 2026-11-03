# 0001. Migración de Next.js a React + Vite

- **Fecha:** 2026-11-03
- **Estado:** Aceptado
- **Ámbito:** arquitectura de entrega del cliente web

## Contexto

La interfaz inicial utilizaba Next.js 16 con App Router, React y TypeScript. Su estructura incluía layout y página en `src/app`, configuración de Next y Turbopack, y fuentes Geist y Geist Mono mediante `next/font/google`. Los scripts dependían de comandos de Next, incluido un comando de lint que dejó de ser válido en esa versión.

Next.js ofrece renderizado de servidor, componentes de servidor y generación estática. Esta aplicación necesita principalmente interacción autenticada con una API separada y no tiene un requisito identificado de SEO público ni de HTML personalizado generado en el servidor. El proyecto inicial no justificaba un segundo entorno de lógica de servidor para la interfaz. Esto no significa que toda instalación de Next exija SSR: la exportación estática también era una alternativa técnica.

El uso prioritario es móvil, con conectividad limitada en terreno y alojamiento en un servidor casero. Se busca una entrega estática ligera que deje los recursos del servidor disponibles para la API y la base de datos. La generación de fuentes mediante solicitudes a Google produjo bloqueos de compilación en la red restringida del entorno de desarrollo.

La combinación de convenciones de servidor innecesarias para el alcance actual, fricción de herramientas y descargas de fuentes durante el build motivó simplificar el cliente, en lugar de mantener configuración para capacidades no requeridas.

## Decisión

1. Sustituir Next.js por React 19 y Vite con TypeScript estricto, como SPA de cliente y salida estática.
2. Mantener la API como servicio separado. La interfaz consume contratos HTTP y no incorpora persistencia ni lógica de negocio del servidor.
3. Usar TanStack Router para navegación tipada y TanStack Query para gestionar el estado remoto cuando se integre la API.
4. Mantener Tailwind CSS como sistema de estilos y empaquetar las fuentes mediante dependencias locales, sin Google Fonts ni CDNs necesarios para compilar o mostrar la interfaz.
5. Diseñar las capacidades PWA y offline sobre esta base mediante decisiones posteriores de caché, sincronización y conflictos. La elección de Vite no implementa estas capacidades automáticamente.
6. Servir el resultado como archivos estáticos, sin mantener un proceso Node de renderizado de la interfaz en producción. El servidor estático continúa consumiendo recursos y requiere una configuración de rutas SPA.

Las instrucciones de desarrollo y publicación se mantienen en el [README del frontend](../../frontend/README.md); su estado de adopción se registra en [PROJECT_STATE.md](../PROJECT_STATE.md).

## Consecuencias

### Positivas

- Se elimina el SSR de la arquitectura elegida y se reduce la complejidad operativa del cliente para el alcance actual.
- Se evita un proceso residente de renderizado Node, favoreciendo el presupuesto de RAM del servidor casero. No se dispone de un benchmark comparativo; no se afirman porcentajes de ahorro ni que Vite produzca siempre un bundle menor.
- La salida estática puede distribuirse y almacenarse en caché de manera independiente de la API.
- Las fuentes auto-alojadas eliminan esa dependencia de red durante el build, una vez instalados los paquetes, y facilitan su futura inclusión en la caché offline.
- La SPA ofrece una base coherente para navegación móvil y futura instalación PWA.

### Negativas y compensaciones

- Se renuncia al SSR y a las convenciones de servidor de Next. La SPA depende de JavaScript para presentar su interfaz y debe controlar el peso y costo de ejecución en móviles.
- Hay que definir rutas de cliente, redirección a la entrada estática, manejo de errores y actualización de datos explícitamente.
- Autenticación, almacenamiento de sesión y políticas de seguridad requieren un diseño propio compatible con la API.
- Offline exige trabajo adicional: service worker, gestión de versiones, caché, cola de operaciones y resolución de conflictos.
- Auto-alojar tipografías aumenta los recursos del despliegue; deben limitarse subconjuntos y pesos a los necesarios.
