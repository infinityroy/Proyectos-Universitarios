#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <wait.h>
#include <fcntl.h> 
#include <sys/types.h>

//Definicion de las estructuras
typedef struct {
    int *array;
    size_t used;
    size_t size;
} Array;

struct Header{
    char *key;
    char *value;
}typedef Header;

struct Request{
    char *path;
    char *method;
    Header *headers;
    int headersLength;
}typedef Request;

struct Response{
    long int contentLength;
    char *status;
    FILE *fp;
    Header *headers;
    int size;
    int type;
}typedef Response;

struct node{
    struct node *next;
    int *socketCliente; 
}typedef Node;

//Declaracion de las globales
//----- HTTP  mensajes de response
#define OK_MP3    "HTTP/1.0 200 OK\nContent-Type:cancion\n\n"
#define NOTOK_404   "HTTP/1.0 404 Not Found\nContent-Type:mp3/html\n\n"
#define MESS_404    "<html><body><h1>Archivo no encontrado :´(</h1></body></html>\r\n"
#define FIFO 1
#define THREADED 2
#define PRE_THREADED 3
#define FORKED 4
#define PRE_FORKED 5
#define MAX_PATH 4096 //max cantidad de caraceteres en el path
#define BACKLOG_SIZE 500 //cantidad de conexiones que va a poder almazenar 
#define PORT 6995
#define NOT_IMPLEMENTED 2
#define GET 1
#define POST 0

pthread_t *thread_pool;
pid_t *pid;
pthread_mutex_t lock_exit = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lockCola = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t condPool = PTHREAD_COND_INITIALIZER;
typedef struct sockaddr_in SA_IN;
typedef struct sockaddr SA;

Node *inicio;
Node *fin;


char *strreplace(char *s, const char *s1, const char *s2) {
    char *p = strstr(s, s1);
    if (p != NULL) {
        size_t len1 = strlen(s1);
        size_t len2 = strlen(s2);
        if (len1 != len2)
            memmove(p + len2, p + len1, strlen(p + len1) + 1);
        memcpy(p, s2, len2);
    }
    return s;
}

int* pop(){
    if (inicio == NULL) {
        return NULL;
    } else {
        int *result = inicio->socketCliente;
        Node *temp = inicio;
        inicio = temp->next; // cambio el inicio por el siguiente en la fila
        if (inicio == NULL) {
            fin = NULL;
        }
        free(temp);
        return result;
    }
}

void add(int *nuevo_socket){
    Node *nuevoNodo = malloc(sizeof(Node));
    nuevoNodo->socketCliente = nuevo_socket;
    nuevoNodo->next = NULL;
    if (fin == NULL) {
        inicio = nuevoNodo;
    } else {
        fin->next = nuevoNodo;
    }
    fin = nuevoNodo;

}

Request *newRequest(){
    Request *r;
    r = (Request *) malloc(sizeof(Request));
    r->path = (char *) malloc(sizeof(char) * (MAX_PATH - 1));
    r->method = (char *) malloc(sizeof(char) * 25);
    r->headersLength = 0;
    r->headers = (Header *) malloc(sizeof(Header) * 35);
    return r;
}

Header *newHeader(char *string){
    // Asigno memoria al header
    Header *header = (Header *) malloc(sizeof(Header));
    header->key = (char *) malloc(sizeof(char)*50);
    header->value = (char *) malloc(sizeof(char)*50);

    char *  tempToken = strtok(string,": ");
    strncpy(header->key,tempToken, sizeof(char)*50);
    header->key[sizeof(char)*50] = '\0';
    tempToken = strtok(NULL, ": ");
    strncpy(header->value,tempToken, sizeof(char)*50);
    header->value[sizeof(char)*50] = '\0';
    return header;
}

Response *newResponse(){
    Response *r = (Response *) malloc(sizeof(Response));
    r->contentLength = 0;
    r->status = (char *) malloc(sizeof(char) * 25);
    r->fp = NULL;
    r->headers = (Header *) malloc(sizeof(Header) * 35);
    r->size = 0;
    return r;
}

void freeRequest(Request *r){
    free(r->method);
    free(r->path);
    for(int i = 0; i < r->headersLength;i++){
        free(r->headers[i].value);
        free(r->headers[i].key);
    }
    //free(r->headers);
}

void freeResponse(Response *r){
    free(r->status);
    for(int i = 0; i < r->size;i++){
        free(r->headers[i].value);
        free(r->headers[i].key);
    }
    //free(r->headers);
}

char *toString(Request *r){
    /*
    printf("path: %s\n",r->path);
    printf("method: %s\n",r->method);
    printf("headersLength: %d\n",r->headersLength);
    for (int i = 0; i < r->headersLength; ++i) {
        printf("- Key:%s\n",r->headers[i].key);
        printf("- Value:%s\n",r->headers[i].value);
    }*/
    return NULL;
}

Request *parseMessage(char *buffer){
    char actualpath[MAX_PATH+1];
    Request *r = newRequest();
    /**
     * /home/jonder/Escritorio/Git/Sistemas_operativos_proyecto_3/datos/
     * /home/meta/CLionProjects/Sistemas_operativos_proyecto_3/datos/
     * /home/estudiante/Escritorio/Sistemas_operativos_proyecto_3/datos/
     */
    strreplace(buffer,"/","/home/estudiante/Escritorio/Sistemas_operativos_proyecto_3/datos/");
    // Separa el request por header
    char * headerToken = strtok(strdup(buffer), "\r\n");
    // Separo el method y path
    char *tempHeader = strdup(headerToken);
    //strcpy(tempHeader, headerToken);
    char* token = strtok(tempHeader, " ");
    strncpy(r->method, token, sizeof(r->method) - 1);
    r->method[sizeof(r->method)] = '\0';
    token = strtok(NULL, " ");
    if(realpath(token,actualpath)==NULL){
        printf("Error(bad path): %s\n",token);
        return NULL;
    }
    strcpy(r->path,actualpath);
    r->headersLength = 0;
    // Loop para separar cada header
    char **headersRaw;
    headersRaw = (char **) malloc(sizeof(char*)*35);
    for (int i = 0; i < 35; ++i) {
        headersRaw[i] = (char *) malloc(sizeof(char)*150);
    }
    headerToken = strtok(buffer, "\r\n");
    headerToken = strtok(NULL, "\r\n");
    while( headerToken != NULL ) {
        //printf("[%s]\n", headerToken);
        strcpy(headersRaw[r->headersLength],headerToken);
        r->headersLength++;
        headerToken = strtok(NULL, "\r\n");
    }
    for (int i = 0; i < r->headersLength; ++i) {
        Header *header = newHeader(headersRaw[i]);
        r->headers[i] = *header;
    }
    return r;
}

void sendFile(FILE *fp, int *client_socket){
    size_t bytes_read;
    char buffer[BUFSIZ] = {0};

    while((bytes_read = fread(buffer,1,BUFSIZ,fp))>0){
        printf("sending %zu bytes\n",bytes_read);
        write(*client_socket,buffer,bytes_read);
    }
    fclose(fp);
}

int writeResponse(int tipo, Response *response, int *client_socket){
    char buffer[BUFSIZ] = {0};

    sprintf(buffer,"%s\r\n",response->status);
    size_t headerLen = strlen(buffer);
    write(*client_socket,buffer,headerLen);
    for (int i = 0; i < response->size; ++i) {
        sprintf(buffer,"%s: %s\r\n",response->headers[i].key,response->headers[i].value);
        headerLen = strlen(buffer);
        printf("sending %zu bytes\n",headerLen);
        write(*client_socket,buffer,headerLen);
    }
    strcpy(buffer, "\r\n");
    write(*client_socket,buffer,strlen(buffer));

    if(tipo == GET){
        sendFile(response->fp,client_socket);
    }
    if(tipo == POST){
        //TODO Escribir archivo en el sistema de archivos
    }
    if(tipo == NOT_IMPLEMENTED){
        //TODO Escribir html de no implementado
    }
    return 1;
}

char *getMimeType(char *path){
    if(strstr(path,".html") != NULL)
        return "text/html";
    if(strstr(path,".mp3") != NULL)
        return "audio/mpeg";
    if(strstr(path,".jpg") != NULL)
        return "image/jpeg";
    if(strstr(path,".mp4") != NULL)
        return "video/mp4";
    if(strstr(path,".ico") != NULL)
        return "image/x-icon";
    return "text/html";
}

Response *executeGet(Request *r, char *buffer, int *client_socket){
    FILE *fp = fopen(r->path,"r");
    if(fp == NULL){
        printf("Error(open): %s\n", buffer);
        close(*client_socket);
        return NULL;
    }
    fseek(fp, 0L, SEEK_END);
    long int sz = ftell(fp);
    rewind(fp);

    Response *response = newResponse();
    response->contentLength = sz;
    strcpy(response->status,"HTTP/1.1 200 OK");
    response->fp = fp;

    char temp[100];

    strcpy (temp, "");
    sprintf(temp, "Host: 127.0.0.1:%d", PORT);
    Header *host = newHeader(temp);
    r->headers[r->headersLength] = *host;
    response->size++;
    sprintf(temp, "Content-Type: %s",getMimeType(r->path));
    Header *contentType = newHeader(temp);
    r->headers[r->headersLength] = *contentType;
    response->size++;

    sprintf(temp, "Content-Length: %ld", sz);
    Header *contentLength = newHeader(temp);
    r->headers[r->headersLength] = *contentLength;
    response->size++;

    response->type = GET;

    return response;
}

Response *executePost(){
    return NULL;
}

Response *executeNotImplemented(Request *r, char *buffer, int *client_socket){
    Response *response = newResponse();
    strcpy(r->path,"/home/estudiante/Escritorio/Sistemas_operativos_proyecto_3/datos/not_implemented.html");
    return executeGet(r,buffer,client_socket);
}

void* stdinReader(void *args){
    pthread_mutex_lock(&lock_exit);
    while(1){
        /**
         * Setea variables que voy a usar como el buffer y el File Identifier(FD)
         */
        pthread_mutex_unlock(&lock_exit);
        fd_set rfds;
        struct timeval tv;
        int retval, len;
        char buf[4096];

        /**
         * Seteo el File Identifier numero 0 que es la entrada por consola, ademas de poner un tiempo de 5s para leer
         */
        FD_ZERO(&rfds);
        FD_SET(0, &rfds);
        tv.tv_sec = 5;
        tv.tv_usec = 0;

        /**
         * Selecciono el buffer de consola previamente obtenido para leer
         */
        retval = select(1, &rfds, NULL, NULL, &tv);
        /* Don't rely on the value of tv now! */
        /**
         * Verificacion de errores
         */
        if (retval < 0) {
            perror("select()");
            exit(-1);
        }
        if (FD_ISSET(0, &rfds)) {
            len = read(0, buf, 4096);
            if (len > 0) {
                buf[len] = 0;

                if(strcmp(buf,"exit\n") == 0){
                    exit(0);
                }
            } else {
                perror("read()");
                exit(-1);
            }
        }

        pthread_mutex_lock(&lock_exit);
    }
}

void * handleMessage(int* p_client_socket){
    int client_socket = *p_client_socket;
    free(p_client_socket);
    char buffer[BUFSIZ];
    memset(buffer,0,strlen(buffer));
    size_t bytes_read;
    int msgsize = 0;
    char actualpath[MAX_PATH+1];
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(client_socket,&fds);
    char numberString[4096];

    //esperamos 1 segundo si aun no hay nada en el socket de lectura
    //while(select(FD_SETSIZE,&fds,NULL,NULL,NULL)==0){
        //sleep(1);
    //}
    msgsize=0;
    //lee al cliente y obtiene el nombre del archivo
    sleep(1);
    while((bytes_read = read(client_socket, buffer+msgsize, sizeof(buffer)-msgsize-1)) > 0 ) {
        msgsize += bytes_read;
        if (msgsize > BUFSIZ-1 || buffer[msgsize-1] == '\n') break;
    }
    if(bytes_read==-1){
        printf("error con la info recibida");
        exit(1);
    }
    buffer[msgsize-1] = 0; //se termina el msg en null y se remueve el \n
    printf("Buffer:[%s]\n",buffer);

    Request *r = parseMessage(buffer);


    if(r==NULL){
        close(client_socket);
        return NULL;
    }
    //toString(r);
    fflush(stdout);

    Response *response;
    //Veo en que metodo cae
    if (!strcmp(r->method,"GET")){
        response = executeGet(r,buffer,&client_socket);
        if(response == NULL){
            close(client_socket);
            return NULL;
        }
    }else if (!strcmp(r->method,"POST")){
        close(client_socket);
        return NULL;
    }else{
        /**
         * TODO Not Implemented response
         */
        close(client_socket);
        return NULL;
    }
    while(response->size > 0){
        writeResponse(response->type,response,&client_socket);
        response->size = 0;
        //printf("write :  %ld\n", n);
    }
    //writeResponse(response->type,response,&client_socket);

    freeRequest(r);
    freeResponse(response);
    close(client_socket);
    printf("cerrando conexion\n");
}


void * thread_function(void *arg) {
    while (1) {
        int *pclient;
        pthread_mutex_lock(&lockCola);
        if ((pclient = pop()) == NULL) {
            pthread_cond_wait(&condPool, &lockCola);
            //reintenta
            pclient = pop();
        }
        pthread_mutex_unlock(&lockCola); 
        
        if (pclient != NULL) {
            //encontro cliente
            handleMessage(pclient);
        }
    }
}


int main(int argc, char **argv){
    int modo,k,index;;
    sscanf(argv[1],"%d",&modo);
    if(modo == PRE_FORKED || modo == PRE_THREADED){
        sscanf(argv[2],"%d",&k);
    }
    int server;
    unsigned int addr_size;
    SA_IN direccionServer, client_addr;

    pthread_t hilo_consola;
    pthread_create(&hilo_consola, NULL, stdinReader,NULL);

    //Limpiemoas la estructura
    memset(&direccionServer, 0, sizeof(direccionServer));

    //Se establece el objeto socket
    server = socket(AF_INET , SOCK_STREAM , 0);

    //AF_INET es una familia de direcciones
    direccionServer.sin_family = AF_INET;
    //INADDR_ANY = en realidad es la IP especial 0.0.0.0
    direccionServer.sin_addr.s_addr = INADDR_ANY;
    //Este es el puerto del servidor
    direccionServer.sin_port = htons(6995);

    //Esto es para no esperar despues de matar el servidor
    int activado = 1;
    setsockopt(server,SOL_SOCKET, SO_REUSEADDR, &activado, sizeof(activado));

    if (bind(server,(SA*)&direccionServer, sizeof(direccionServer)) == -1){
        perror("Falló el bind del socket");
        return 1;
    }
    
    if (listen(server,BACKLOG_SIZE) == -1) {
        perror("Falló el listen del socket");
        return 1;
    }
    if(modo == PRE_THREADED){
        thread_pool = (pthread_t*)malloc(sizeof(pthread_t)*k);
        for (int i=0; i < k; i++) {
            pthread_create(&thread_pool[i], NULL, thread_function, NULL);
        }
    }
    if(modo == PRE_FORKED){
        pid = (pid_t*)malloc(sizeof(pid_t)*k);
    }
    
    pthread_mutex_lock(&lock_exit);
    while (1) {
        int client_socket;
        printf("Esperando conexiones\n");
        //esperando clientes
        addr_size = sizeof(SA_IN);
        client_socket = accept(server, (void*)&client_addr, &addr_size);
        printf("Nuevo cliente\n");

        int *pclient = malloc(sizeof(int));
        *pclient = client_socket;

        if(modo == FIFO){
            handleMessage(pclient);
        }
        if(modo == THREADED){
            pthread_t thread;
            pthread_create(&thread, NULL, (void *) handleMessage, pclient);
        }
        if(modo == PRE_THREADED){
            pthread_mutex_lock(&lockCola); 
            add(pclient);
            pthread_mutex_unlock(&lockCola);
            pthread_cond_signal(&condPool);
        }
        if(modo == FORKED){
            //handleMessage(pclient);
            int child = fork();
            if(!child){
                handleMessage(pclient);
                return 1;
                //kill(child, SIGKILL);
                //AQUI Pegarle un balazo a cada hijo
            }
        }
        if(modo == PRE_FORKED){
            int forkstatus = fork();
            if(forkstatus==0){
                handleMessage(pclient);
                return 1;
            }
            else{
                pid[index++] = forkstatus;
                if(index>=k){
                    index=0;
                    waitpid(pid[index],NULL,0);
                }
                
            }
        }
    }

    return 0;
}
