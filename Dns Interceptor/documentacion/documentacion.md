
# Instalación de docker

Si no tenemos docker instalado, procedemos a instalarlo de la siguiente forma:

### <font size="5">**En Windows**</font>

1. Instalar Docker y Docker Compose, para esto se puede apoyar en la siguiente página: <https://docs.docker.com/desktop/windows/install/>
    - Puede descargar el ejecutable que incluse Docker y Docker Compose en: <https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe>

### <font size="5">**En linux**</font>

#### <font size="4">**Configurar repositorio:**</font>

1. Actualizar la lista de paquetes con:

```bash
sudo apt-get update
```

2. Permitir apt usar un repositorio por medio de HTTPS

```bash
sudo apt-get install \
ca-certificates \
curl \
gnupg \
lsb-release
```

3. Añadir la llave oficial GPG de Docker
```curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg```

4. Configurar la rama stable del Repositorio:

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### <font size="4">**Instalar Docker Engine:**</font>

1. Instalamos la última versión de Docker Engine, containerd y Docker Compose:

```bash
sudo apt-get update && \
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### <font size="4">**Instalar Docker Compose:**</font>

1. Usamos este comando para descargar la última versión estable de Docker Compose:

```bash
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker} && \
mkdir -p $DOCKER_CONFIG/cli-plugins && \
curl -SL https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-linux-x86_64 -o && \
$DOCKER_CONFIG/cli-plugins/docker-compose
```

1. Damos permisos para ejecutar el instalador:

```bash
chmod +x $DOCKER_CONFIG/cli-plugins docker-compose
```

1. Probamos la instalación con:

```bash
docker compose version
```


# Ejecutar la aplicación

Para ejecutar el servidor o calculadora de red, se habre la carpeta del proyecto y dentro de la carpeta se habre una consola en donde se ejecuta:

### <font size="5">**En Windows**</font>

```bash
docker-compose up -d --build
```

- Algunas veces en Windows es necesario añadir manualmente la carpeta de \Docker\resources\bin a la
variable de entorno PATH para que reconozca el comando ***docker-compose***.

### <font size="5">**En linux**</font>

``` bash
docker-compose up -d --build
```

- Recomendación: Utilizar Visual Studio Code para abrir la carpeta y una consola.

Para detener el proyecto o servidor, solo se utiliza el comando:

```bash
docker-compose down 
```

# Instalar Nslookup para pruebas

### <font size="5">**En Windows**</font>
```bash
Install-WindowsFeature Telnet-Client
```

### <font size="5">**En Linux**</font>
Ya viene instalado

# Componentes de la solución

## DNS interceptor

El dns interceptor recibe un paquete de tipo dns este paquete se guarda en buffer de tipo unsigned int (entero sin signo) y se explora. La exploración se realiza revisando el paquete byte por byte, específicamente al principio lo que se busca los bytes Opcode y QR, la ubicación de los bytes puede verse en el documento RFC2929.

En caso de que el byte QR o Opcode sean diferente a 0, eso significa que el paquete dns es de tipo query estándar entonces se toma el contenido del buffer, se empaqueta en un formato llamado base64 y se envía por medio de https POST a un servidor REST llamado DNS API, que está corriendo en python3. Luego el servidor responde igual con un paquete base64, se decodifica y se envía al usuario. 

Por otro lado si en el paquete el byte de QR y el del opcode son iguales a 0 eso significa que el paquete es de tipo query estándar por lo que se procede a identificar los bytes que corresponden al host, una vez identificados se extraen, luego una vez tomado el host se realiza una petición por medio de http hacia un servidor llamado Elasticsearch el cual se encarga de almacenar el ip correspondiente a ese host en caso de que haya sido guardada.

Cuando se envía el host hacia el Elasticsearch se espera a la respuesta que tiene el ip y TTL, en caso de que la respuesta traiga el ip entonces se envía un request al servidor de google y el servidor de google responde con un paquete dns, por lo que se procede a tomar ese paquete y cambiarle el ip y el TTL a ese response y una vez cambiada el ip se envía el usuario. En caso de que Elasticsearch no mande el ip, entonces se envía hacia el servidor DNS API y finalmente el response del DNS API se recibe, se decodifica de base 64 y envía hacia el usuario.

## REST Api flask

Con Flask la creación del API Restful es muy fácil, este API tendrá un solo recurso que responderá al url \api\dns_resolver donde recibirá un paquete DNS codificado en base64 en un string y devolverá un string con el paquete de respuesta codificado en base64.

## Elasticsearch

Este es un servidor de búsquedas muy poderoso que utiliza formato de comunicación web de tipo REST, la estructura de elasticsearch es muy versátil pero se fundamenta en el guardado de documentos en formato json para representar los objetos que este guarda, en nuestro caso guardamos documentos u objetos con 3 propiedades de texto y una propiedad numérica que representa un índice utilizado por el DNS interceptor para realizar un round robin, la aplicación utiliza la versión 7.17.4 y permite que elasticsearch opere en el puerto 9200, como estructura para nuestro proyecto utilizamos una estructura de single node, esto significa que se genera un solo cluster que se selecciona como maestro y no se une a ningún otro cluster.

### Initializer

Este es un servicio que existe en el proyecto con el único propósito de esperar a que elasticsearch esté listo para recibir consultas y enviar las consultas de tipo POST para crear los documentos necesarios con todas sus propiedades.

## Kibana

Kibana es un panel de visualización para Elasticsearch que nos permite interactuar con el sistema mediante una interfaz gráfica, además de llevar diferentes análisis estadísticos sobre el comportamiento y rendimiento de nuestro servidor.

En nuestro proyecto Kibana utiliza la misma versión que Elasticsearch(7.17.4), este opera utilizando el puerto 5601 y el enlace al servidor ocurre mediante el cambio de un estado de la variable “ELASTICSEARCH_URL” en el documento de configuración de docker Compose, esta variable se modifica a localhost:9200 que es el puerto por el cual opera elasticsearch.

# Conclusiones

1. Es muy útil trabajar proyectos de manera iterativa que nos permita ver progreso relativamente rápido y nos permite unir y probar distintos módulos del proyecto.
2. Extraer información local de un programa es un trabajo más difícil de realizar cuando utilizamos docker a comparación de cuando corremos ese programa localmente.
3. Elasticsearch utiliza muchísima memoria ram y dependiendo de las especificaciones del dispositivo que utilicemos para correr el proyecto puede ser importante limitar la cantidad de memoria que puede utilizar.
4. Es muy importante estar realizando pruebas de parte del código para verificar que todo esté marchando como debería, como ejemplo usar la herramienta jmeter para realizar pruebas a un servidor.
5. Docker Compose es una gran herramienta para facilitar la coordinación de proyectos usando múltiples contenedores que se comportan de manera similar a máquinas virtuales, una de las grandes ayudas que el mismo proporciona es la implementación de la capa de enlace bridge que redirige el tráfico de red al host de manera que si queremos restringir el acceso a la red de Docker podemos hacerlo desde el Host.
6. Elasticsearch es un motor sumamente poderoso y sencillo de usar a un nivel básico, este también permite personalizar el cómo se organizan los datos y en muchas formas el cómo se explorarán para lograr un mejor rendimiento.
7. Si se trabaja cada contenedor con un dockerFile es posible modularizar el proyecto y utilizar el dockerFile para agregar comandos y otros útiles necesarios para la configuración y la ejecución del contenedor en el ambiente.
8. Flask es un framework muy sencillo de usar para cualquier programador con conocimientos básicos, facilita en gran medida la creación de un API pero un problema del api es que es poco seguro y normalmente se usa en aplicaciones pequeñas o para pruebas.
9. A la hora de estimar el tiempo que tomará realizar un trabajo a la hora de delegarlo a una parte de un grupo es importante tener en consideración no solo la carga en código sino que también la carga investigativa y la cantidad de dependencias que conlleva ese trabajo, en muchos casos es muy útil llevar un repositorio de enlaces ya sea de documentación, de stackoverflow o artículos para compartir y apoyarse a finalizar más rápidamente la carga investigativa.
10. Siempre es muy importante tomarse el tiempo para leer y entender muy bien con lo que se va a trabajar ya que nos ahorrará mucho tiempo y muy probables problemas en el desarrollo.

# Recomendaciones

1. Para usar HTTPS en Flask se puede usar el contexto ssl de “adhoc” que utiliza pyopenssl para generar certificados de un solo uso fácilmente.
2. Para evitar una espera eterna de una respuesta en UDP se puede usar la función “select” de la biblioteca select de python para solo esperar respuesta por una cantidad finita de segundos.
3. Para trabajar con las cadenas de bytes de los paquetes es muy importante recordar cómo funcionan los punteros en C y cómo podemos movernos en una cadena cambiando los valores numéricos de nuestros punteros.
4. Para cargar un estado inicial para elasticsearch es muy sencillo utilizar un servicio “Inicializador” cuya única función sea esperar a que el servicio de elasticsearch esté listo para recibir consultas y solicitar la creación de este estado inicial.
5. Sí está trabajando en el lenguaje c y necesita trabajar con bytes, se debe utilizar array de enteros y sin signo, por ejemplo tener un arreglo de unsigned int para que la existencias de ceros en hexadecimal no sean problema, ya que si se trabaja con un arreglo de tipo char el cero lo reconoce como fin de línea.

6. Al trabajar con bytes es muy importante guardar estados en archivos de textos y utiliza herramientas de visualización como hexyl para ver cómo están estructuradas esas cadenas de bytes.
7. Cuando se trabaja con una biblioteca externa en c, se debe asegurar que la biblioteca esté instalada en el sistema, luego al momento de compilar el archivo de c se debe de asegurar incluirla en la compilación.
8. Se recomienda siempre tener un archivo para comandos del contenedor o archivo.bash, esto para facilitar agregar comandos al contenedor después de iniciado.
9. Si estamos trabajando un contenedor con un sistema operativo como ubuntu y necesitamos instalarle un nuevo paquete, lo más recomendable es añadir otro RUN al docker file ya que si añadimos el comando a la lista de comandos de instalación, se volverán de nuevo a descargar todos los paquetes que están en la lista y duraría mucho tiempo.
10. Siempre es recomendable leer la documentación de cómo funciona una pieza de software, esto nos ayuda a entenderla a profundidad y a poder usarla y modificarla a nuestra necesidad.

# Bibliografía

1. Install Elasticsearch with Docker | Elasticsearch Guide [8.2] | Elastic. Elastic.co. (2022). Recuperado: 27 Mayo 2022, de <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html>.

2. Running the Elastic Stack ("ELK") on Docker | Getting Started [8.2] | Elastic. Elastic.co. (2022). Recuperado: 27 Mayo 2022, de <https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-stack-docker.html#run-docker-secure>.

3. Krebs, B. (2021). Developing RESTful APIs with Python and Flask. Auth0 - Blog. Recuperado: 27 Mayo 2022, de <https://auth0.com/blog/developing-restful-apis-with-python-and-flask/>.

4. Dudycz, O. (2022). A few tricks on how to set up related Docker images with docker-compose - Event-Driven.io. Event-driven.io. Recuperado: 27 Mayo 2022, de <https://event-driven.io/en/tricks_on_how_to_set_up_related_docker_images/>.

5. Nachtimwald, J. (2017). Base64 Encode and Decode in C. Nachtimwald.com. Retrieved 27 May 2022, from <https://nachtimwald.com/2017/11/18/base64-encode-and-decode-in-c/>.

6. UDP Server-Client implementation in C - GeeksforGeeks. GeeksforGeeks. (2022). Retrieved 27 May 2022, from <https://www.geeksforgeeks.org/udp-server-client-implementation-c/>.

7. Dholakia, J. (2020). Creating RESTful Web APIs using Flask and Python. Medium. Retrieved 27 May 2022, from <https://towardsdatascience.com/creating-restful-apis-using-flask-and-python-655bad51b24>.

8. How to capturs system() output. Unix.com. (2009). Retrieved 27 May 2022, from <https://www.unix.com/programming/108753-how-capturs-system-output.html>.

9. https.c. Curl.se. (2022). Retrieved 27 May 2022, from <https://curl.se/libcurl/c/https.html>.

10. Nachtimwald, J. (2017). Base64 Encode and Decode in C. Nachtimwald.com. Retrieved 27 May 2022, from <https://nachtimwald.com/2017/11/18/base64-encode-and-decode-in-c/>.

11. Rancel, M. (2022). Escribir (guardar datos) en ficheros o archivos en lenguaje C. fputc, putc, fputs, fprintf. Ejemplos (CU00537F). Aprenderaprogramar.com. Retrieved 27 May 2022, from <https://www.aprenderaprogramar.com/index.php?option=com_content&view=article&id=936:escribir-guardar-datos-en-ficheros-o-archivos-en-lenguaje-c-fputc-putc-fputs-fprintf-ejemplos-cu00537f&catid=82&Itemid=210>.

12. GitHub - elzoughby/Base64: C library to encode and decode strings with base64 format. GitHub. (2018). Retrieved 27 May 2022, from <https://github.com/elzoughby/Base64>.

13. command, P., & Joy, J. (2012). Pass a variable to popen command. Stack Overflow. Retrieved 27 May 2022, from <https://stackoverflow.com/questions/11151926/pass-a-variable-to-popen-command>.

14. UDP Socket Programming: DNS — Computer Systems Fundamentals. jmu.edu/cise/cs/index.shtml. (2022). Retrieved 27 May 2022, from <https://w3.cs.jmu.edu/kirkpams/OpenCSF/Books/csf/html/UDPSockets.html>.
