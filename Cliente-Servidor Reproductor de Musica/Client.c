#include <stdio.h>
#include <stdlib.h>
//#include <math.h>
#include <time.h>
//#include <setjmp.h>
#include <netdb.h> 
#include <sys/ioctl.h>
#include <errno.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#include<pthread.h>

//Estructura de datos
struct node{
    struct node *next;
    long double data; 
}typedef Node;

/*
 *  DECLARACIONES INICIALES
*/ 
//Puerto
//#define SERVER_PORT 6995 //ESTE es el puerto del server
#define MAXLINE 4096
#define SA struct sockaddr

int SERVER_PORT, iteraciones, cantHilos;
long double tiempoEsperaTotal, tiempoAtencionTotal;
unsigned long  int totalBytesRecibidos;
pthread_mutex_t lockEspera = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lockAtencion = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lockBytes = PTHREAD_MUTEX_INITIALIZER;
char IP[50];
Node *inicioEspera;
Node *finEspera;
Node *inicioAtencion;
Node *finAtencion;



void addEspera(double datos){
    Node *nuevoNodo = malloc(sizeof(Node));
    nuevoNodo->data = datos;
    nuevoNodo->next = NULL;

    if (inicioEspera == NULL) {
        inicioEspera = nuevoNodo;
    } else {
        finEspera->next = nuevoNodo;
    }
    finEspera = nuevoNodo;
}
void addAtencion(double datos){
    Node *nuevoNodo = malloc(sizeof(Node));
    nuevoNodo->data = datos;
    nuevoNodo->next = NULL;

    if (inicioAtencion == NULL) {
        inicioAtencion = nuevoNodo;
    } else {
        finAtencion->next = nuevoNodo;
    }
    finAtencion = nuevoNodo;
}

void * clientThread(void *arg){
    char ** argv = (char ** ) arg;
    printf("[%lu] Me cree\n",pthread_self());
    char message[MAXLINE];
    char buffer[MAXLINE];
    int clientSocket, iteracionesCliente,bytesRecibidos;
    struct sockaddr_in serverAddr;
    socklen_t addr_size;
    iteracionesCliente = iteraciones;
    
    while (iteracionesCliente>0){
    // Create the socket. 
    if((clientSocket = socket(AF_INET,SOCK_STREAM,0)) < 0){
        //msg_and_die("Error while creating the socket");
        perror("Error creando el socket\n");
        pthread_exit(NULL);
    }
    //printf("[%lu] Genere el socket:{%d}\n",pthread_self(),clientSocket);
    bzero(&serverAddr, sizeof(serverAddr));
    //Configure settings of the server address
    // Address family is Internet 
    serverAddr.sin_family = AF_INET;

    //Set port number, using htons function 
    serverAddr.sin_port = htons(SERVER_PORT);

    //Set IP address to localhost
    //serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    if (inet_pton(AF_INET, IP, &serverAddr.sin_addr) <= 0){
        perror("inet_pton error for %s \n");
        close(clientSocket);
        pthread_exit(NULL);
    }

    //memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);
    
    clock_t begin = clock();
    if (connect(clientSocket,(SA *) &serverAddr,sizeof(serverAddr))<0){
        //El cliente no se pudo conectar al server
        //msg_and_die("connect failed");
        printf("[%lu] Error conectando con el server: %d\n",pthread_self(),errno);
        close(clientSocket);
        pthread_exit(NULL);
    }

    sprintf(message, "GET /%s HTTP/1.1\r\nConnection: keep-alive\r\n\r\n", argv[3]);
    //opcion 2
    //sprintf(message, "GET /%s HTTP/1.1\rKeep-Alive: %d\n\rConnection: keep-alive\n\r\n\r\n", argv[3],iteraciones);
    clock_t end = clock();
    pthread_mutex_lock(&lockEspera);
    addEspera((double)(end-begin)/CLOCKS_PER_SEC);
    tiempoEsperaTotal+= (double)(end-begin)/CLOCKS_PER_SEC;
    pthread_mutex_unlock(&lockEspera);
    
        begin = clock();
        if(write(clientSocket,message,strlen(message)) < 0){
            perror("Error de escritura\n");
            close(clientSocket);
            pthread_exit(NULL);
        }
        

        //limpia el buffer
        memset(buffer,0,MAXLINE);
        //se lee una respuesta
        while(bytesRecibidos = recv(clientSocket, buffer, MAXLINE, 0) > 0){
            //Se imprime la data recibida
            puts("Server response : ");
            printf( "%s\n", buffer );
            //puts(buffer);
            pthread_mutex_lock(&lockBytes);
            totalBytesRecibidos+= bytesRecibidos;
            pthread_mutex_unlock(&lockBytes);
            break;
        }
        pthread_mutex_lock(&lockAtencion);
        addAtencion((double)(end-begin)/CLOCKS_PER_SEC); 
        pthread_mutex_unlock(&lockAtencion);
        if (bytesRecibidos < 0){
            perror("Error al leer datos del server");
        }
        end = clock();
        pthread_mutex_lock(&lockEspera); 
        tiempoAtencionTotal+= (double)(end-begin)/CLOCKS_PER_SEC;
        pthread_mutex_unlock(&lockEspera);
        iteracionesCliente-=1;  
    }

    //Print the received message
    //printf("Data received: %s\n",buffer);
    close(clientSocket);
    pthread_exit(NULL);
}

long double calcVar(Node *ini, long double promedio){
    long double result =0;
    Node *actual=ini;
    while(actual->next!=NULL){
        result+=(ini->data-promedio)*(ini->data-promedio);
        actual=actual->next;
    }
    return result/(iteraciones*cantHilos);
}

int main(int argc, char **argv) {

    //Recibo y guardo los argumentos
    sscanf(argv[1],"%d",&iteraciones);
    sscanf(argv[2],"%d",&cantHilos);

    char* recurso = malloc(10 * sizeof(500));
    recurso = argv[3];

    strcpy(IP,argv[4]);

    //Guardo el puerto en una global
    sscanf(argv[5],"%d",&SERVER_PORT);

    /*
    printf("\nIteraciones: %d", iteraciones);
    printf("\ncantHilos: %d", cantHilos);
    printf("\nRecurso: %s", recurso);
    printf("\nIP: %s", IP);
    printf("\nPuerto: %d", SERVER_PORT);
    */
    int i = 0;
    pthread_t tid[cantHilos];
    /*
    pthread_create(&tid[0], NULL, clientThread, argv);
    pthread_join(tid[0],NULL);
    */
    while(cantHilos > i){
        if(pthread_create(&tid[i], NULL, clientThread, argv) != 0 ){
            printf("Failed to create thread\n");
        }
        i++;
    }

    i = 0;
    while(i< cantHilos){
        pthread_join(tid[i++],NULL);
        printf("%d:\n",i);
    }
    long double promedioEspera = (long double) tiempoAtencionTotal/(iteraciones*cantHilos);
    long double promedioAtencion = (long double) tiempoAtencionTotal/(iteraciones*cantHilos);
    printf("Resultados:\n");
    printf("Total Bytes Recibidos: %lu\n",totalBytesRecibidos);
    printf("Total Espera: %Lf\n",tiempoEsperaTotal);
    printf("Promedio Espera: %Lf\n", promedioEspera);
    printf("Varianza Espera: %Lf\n", calcVar(inicioEspera,promedioEspera));
    printf("Total Atencion: %Lf\n",tiempoAtencionTotal);
    printf("Promedio Atencion: %Lf\n", promedioAtencion);
    printf("Varianza Atencion: %Lf\n", calcVar(inicioAtencion,promedioAtencion));

  return 0;
}