# API Contract — autenticación

`POST /auth/login`, JSON request `{"correo":"usuario@dominio.com","password":"cadena"}`.

**200** `{"correo":"usuario@dominio.com","token":"JWT","token_type":"bearer"}`; `token` JWT HS256 con subject correo e `exp`.

**401** `{"detail":"Correo o contraseña incorrectos."}` por usuario inexistente o password incorrecta.

**422** FastAPI validation error con `detail` tipo array, para campos ausentes/vacíos y whitespace en correo; **no** se envía credencial a DB para entradas inválidas.

**Contrato de UI:** 400/401 → `Correo o contraseña incorrectos.`; error de conexión → `No se pudo conectar con el servidor.`; demás → `No se pudo iniciar sesión. Intentá de nuevo.`

**No incluir** `password_hash`, password, JWT_SECRET ni detalles internos en las respuestas.
