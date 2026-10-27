# v17: integración de componentes oficiales

[C] El componente común sin edición acepta sha256_base_v11 y sha256_base_diccionario. Los tres consumidores oficiales comparten el componente mediante el consumidor central; pruebas de 60 contextos por consumidor y edición. La prueba de v16 con componentes nuevos usa un descriptor aislado con hashes recalculados; adicionalmente el descriptor v16 original se verificó con sus componentes desde Git.

[E] En el árbol de trabajo actual el descriptor activo v16 rechaza el consumidor central modificado por diferencia de hash. Mientras se espera la promoción de v17, usar v16 con sus componentes en un checkout aislado desde Git. No cambiar puntero ni alterar componentes congelados para ocultar la diferencia. Datos de extracto no demuestran vigencia histórica.
