# TiendaNo15
* **Nombre:** Luis Eduardo Rochín Tan
* **Tema:** Una Tienda
* **Descripción:**
Una página web que funciona con una base de datos de MongoDB Atlas que maneja los productos y los pedidos de una tienda. El Backend se hizo con Python y está acompañado de tres archivos HTML (login, productos, pedidos) más un archivo .env para la conexión a la base de datos.
## Entidades y Relación
* **Productos:** Almacena los ítems disponibles con sus especificaciones (`nombre`, `precio`, `stock`).
* **Pedidos:** Registra las solicitudes de compra hechas por los clientes (`cliente`, `producto_id`, `cantidad`).
* Pedidos depende de productos ya que sin un producto existente no se puede realizar un pedido, razón por la cual se optó por utilizar una relación de tipo referencia (ObjetoID).
## Versión de MongoDB
Se usó la versión 8.0.26 porque MongoDB Atlas no permite el uso de la versión 7.
## Cómo correr el Seed
La aplicación cuenta con un mecanismo automatizado de provisión de datos (`@app.before_request`). Al iniciar la aplicación por primera vez en local o producción, se valida la existencia de los documentos semilla:
* Inicia con un usuario llamado "demo@demo.com".
* Los datos iniciales son tres ítems en la tabla de productos con sus respectivos datos.
