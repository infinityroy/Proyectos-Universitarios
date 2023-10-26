#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h>
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <math.h>
#include <curl/curl.h>
#include <ctype.h>
#include <pthread.h>

#include <b64/cencode.h>
#include <b64/cdecode.h>
#include <assert.h>

#include <json-c/json.h>

#define PORT 53 
#define unInt unsigned int

int index_xd = 0;

//Variable global para largo de un response
pthread_mutex_t sockfd_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t curl_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t elk_mutex = PTHREAD_MUTEX_INITIALIZER;

const char b64chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

int b64invs[] = { 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58,
	59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5,
	6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
	21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28,
	29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
	43, 44, 45, 46, 47, 48, 49, 50, 51 };
/* arbitrary buffer size */
#define SIZE 100

#define SKIP_PEER_VERIFICATION
#define SKIP_HOSTNAME_VERIFICATION

struct string {
    char *ptr;
    size_t len;
};

struct decoded_response {
    unInt *response;
    size_t len;
};

struct args {
    unInt *bufferBytes;
    int n;
    int sockfd;
    struct sockaddr_in *cliaddr;
}typedef Args;

struct host {
    char *TTL;
    char *IP;
} typedef Host;

typedef struct json_object JsonObject;

size_t b64_encoded_size(size_t inlen) {
	size_t ret;

	ret = inlen;
	if (inlen % 3 != 0)
		ret += 3 - (inlen % 3);
	ret /= 3;
	ret *= 4;

	return ret;
}

char *b64_encode(const unsigned char *in, size_t len) {
	char   *out;
	size_t  elen;
	size_t  i;
	size_t  j;
	size_t  v;

	if (in == NULL || len == 0)
		return NULL;

	elen = b64_encoded_size(len);
	out  = malloc(elen+1);
	out[elen] = '\0';

	for (i=0, j=0; i<len; i+=3, j+=4) {
		v = in[i];
		v = i+1 < len ? v << 8 | in[i+1] : v << 8;
		v = i+2 < len ? v << 8 | in[i+2] : v << 8;

		out[j]   = b64chars[(v >> 18) & 0x3F];
		out[j+1] = b64chars[(v >> 12) & 0x3F];
		if (i+1 < len) {
			out[j+2] = b64chars[(v >> 6) & 0x3F];
		} else {
			out[j+2] = '=';
		}
		if (i+2 < len) {
			out[j+3] = b64chars[v & 0x3F];
		} else {
			out[j+3] = '=';
		}
	}

	return out;
}

size_t b64_decoded_size(const char *in) {
	size_t len;
	size_t ret;
	size_t i;

	if (in == NULL)
		return 0;

	len = strlen(in);
	ret = len / 4 * 3;

	for (i=len; i-->0; ) {
		if (in[i] == '=') {
			ret--;
		} else {
			break;
		}
	}

	return ret;
}

int b64_isvalidchar(char c) {
	if (c >= '0' && c <= '9')
		return 1;
	if (c >= 'A' && c <= 'Z')
		return 1;
	if (c >= 'a' && c <= 'z')
		return 1;
	if (c == '+' || c == '/' || c == '=')
		return 1;
	return 0;
}

int b64_decode(const char *in, unsigned char *out, size_t outlen) {
	size_t len;
	size_t i;
	size_t j;
	int    v;

	if (in == NULL || out == NULL)
		return 0;

	len = strlen(in);
	if (outlen < b64_decoded_size(in) || len % 4 != 0)
		return 0;

	for (i=0; i<len; i++) {
		if (!b64_isvalidchar(in[i])) {
			return 0;
		}
	}

	for (i=0, j=0; i<len; i+=4, j+=3) {
		v = b64invs[in[i]-43];
		v = (v << 6) | b64invs[in[i+1]-43];
		v = in[i+2]=='=' ? v << 6 : (v << 6) | b64invs[in[i+2]-43];
		v = in[i+3]=='=' ? v << 6 : (v << 6) | b64invs[in[i+3]-43];

		out[j] = (v >> 16) & 0xFF;
		if (in[i+2] != '=')
			out[j+1] = (v >> 8) & 0xFF;
		if (in[i+3] != '=')
			out[j+2] = v & 0xFF;
	}

	return 1;
}

char* codeBase64(unInt *bufferBytes,int n) {
    size_t elen = b64_encoded_size(n);
    char *enc = (char *) malloc(elen+1);
    strcpy(enc , b64_encode((unsigned char *)bufferBytes, n));
    return enc;
}

struct decoded_response decodeBase64(char *enc) {
   
    struct decoded_response response;

    /* +1 for the NULL terminator. */
	response.len = b64_decoded_size(enc)+2;
	response.response = malloc(response.len);
    memset(response.response, 0, response.len);

    printf("Banda antes de decode\n");

    if (!b64_decode(enc, (unsigned char *)response.response, response.len)) {
        FILE* response_file;
        response_file = fopen("decode_error.txt", "wb");
        fwrite(enc, strlen(enc), 1, response_file);
        fclose(response_file);
		printf("Decode Failure\n");
        free(response.response);
        response.response = NULL;
		return response;
	}

    return response;
}

void init_string(struct string *s) {
  s->len = 0;
  s->ptr = malloc(s->len+1);
  if (s->ptr == NULL) {
    fprintf(stderr, "malloc() failed\n");
    exit(EXIT_FAILURE);
  }
  s->ptr[0] = '\0';
}

void appendStr(void *ptr, size_t size, size_t nmemb, struct string *s) {
    size_t new_len = s->len + size*nmemb;
    s->ptr = realloc(s->ptr, new_len+1);
    if (s->ptr == NULL) {
        fprintf(stderr, "realloc() failed\n");
        exit(EXIT_FAILURE);
    }
    memcpy(s->ptr+s->len, ptr, size*nmemb);
    s->ptr[new_len] = '\0';
    s->len = new_len;
}

static size_t writefunc(void *ptr, size_t size, size_t nmemb, struct string *s) {
    appendStr(ptr, size, nmemb, s);

    return size*nmemb;
}

char *curlRequest(char *url, char *rawContent, struct curl_slist *headers, int post, int saveResponse){
    CURL *curl;
    CURLcode res;
    curl = NULL;

    pthread_mutex_lock(&curl_mutex);
    curl = curl_easy_init();
    pthread_mutex_unlock(&curl_mutex);

    if(curl) {
        struct string s;

        curl_easy_setopt(curl, CURLOPT_URL, url);

        if (saveResponse) {
            init_string(&s);
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writefunc);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&s);
        }

        if (post) {
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, rawContent);

        #ifdef SKIP_PEER_VERIFICATION
            /*
            * If you want to connect to a site who is not using a certificate that is
            * signed by one of the certs in the CA bundle you have, you can skip the
            * verification of the server's certificate. This makes the connection
            * A LOT LESS SECURE.
            *
            * If you have a CA cert for the server stored someplace else than in the
            * default bundle, then the CURLOPT_CAPATH option might come handy for
            * you.
            */
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
        #endif
        
        #ifdef SKIP_HOSTNAME_VERIFICATION
            /*
            * If the site you are connecting to uses a different host name that what
            * they have mentioned in their server certificate's commonName (or
            * subjectAltName) fields, libcurl will refuse to connect. You can skip
            * this check, but this will make the connection less secure.
            */
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);
        #endif
        }

        if (headers != NULL) {
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        }
        
        /* Perform the request, res will get the return code */
        curl_easy_setopt(curl, CURLOPT_UPLOAD_BUFFERSIZE, 120000L);
        res = curl_easy_perform(curl);
        
        curl_easy_reset(curl);
        
        /* Check for errors */
        if(res != CURLE_OK)
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
        /* always cleanup */
        curl_easy_cleanup(curl);
        if (saveResponse) {
            return s.ptr;
        }
        return "";
    }
    /* always cleanup */
    curl_easy_cleanup(curl);
    return "";
}

char *trimwhitespace(char *str) {
    char *end;

    // Trim leading space
    while(isspace((unsigned char)*str)) str++;

    if(*str == 0)  // All spaces?
        return str;

    // Trim trailing space
    end = str + strlen(str) - 1;
    while(end > str && isspace((unsigned char)*end)) end--;

    // Write new null terminator character
    end[1] = '\0';

    return str;
}

struct decoded_response cliente_resolver(unInt* request, int largo_request) {

    struct decoded_response response;
    response.response = (unInt *) malloc( sizeof(unInt)*100); // allocate 8 unsigned int

    int sockfd; 
    struct sockaddr_in     servaddr; 

    // Creating socket file descriptor 
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 

    memset(&servaddr, 0, sizeof(servaddr)); 

    // Filling server information 
    servaddr.sin_family = AF_INET; 
    //Puerto 53
    servaddr.sin_port = htons(PORT); 
    //Me conecto a google
    servaddr.sin_addr.s_addr = inet_addr("8.8.8.8"); 

    int n;
    socklen_t len;

    sendto(sockfd, (unInt *)request, largo_request, 
        MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
            sizeof(servaddr)); 

    n = recvfrom(sockfd,response.response, sizeof(unInt)*100,  
                MSG_WAITALL, ( struct sockaddr *) &servaddr,
                &len);
    
    response.len = n;
    
    return response; 
}

Host *RoundRobin(char *jsonResponse) {
    /*
     * Obtener los elementos del Json
    */
    JsonObject *parsedJson;
    JsonObject *hits;
    JsonObject *hitsTotal;
    JsonObject *hitsTotalValue;
    JsonObject *docs;
    /*
     * Parseo el Json para obtener cantidad de matchs
    */
    parsedJson = json_tokener_parse(jsonResponse);
    json_object_object_get_ex(parsedJson, "hits", &hits);
    json_object_object_get_ex(hits, "total", &hitsTotal);
    json_object_object_get_ex(hitsTotal, "value", &hitsTotalValue);

    int nMatch = json_object_get_int(hitsTotalValue);
    if(!nMatch){
        free(hitsTotalValue);
        free(hitsTotal);
        free(hits);
        free(parsedJson);
        return NULL;
    }

    json_object_object_get_ex(hits, "hits", &docs);
    JsonObject *doc, *ID, *source, *TTL, *IP, *INDEX;
    doc = json_object_array_get_idx(docs, 0);
    json_object_object_get_ex(doc, "_source", &source);
    json_object_object_get_ex(doc, "_id", &ID);
    json_object_object_get_ex(source, "TTL", &TTL);
    json_object_object_get_ex(source, "IP", &IP);
    json_object_object_get_ex(source, "index", &INDEX);

    char *ttlStr = (char *)malloc(sizeof(char)*32);
    strcpy(ttlStr, json_object_get_string(TTL));
    char *ipStr = (char *)malloc(sizeof(char)*255);
    strcpy(ipStr, json_object_get_string(IP));
    int index = json_object_get_int(INDEX);
    char *id = (char *)malloc(sizeof(char)*32);
    strcpy(id, json_object_get_string(ID));
    printf("index:%d\n",index);

    char *token;
    token = strtok(ipStr,",");
    Host *hosts = (Host *) malloc(sizeof(Host)*64);
    int i = 0;
    while (token != NULL) {
        hosts[i].IP = (char *) malloc(sizeof(char)*32);
        hosts[i].TTL = (char *) malloc(sizeof(char)*32);
        strcpy(hosts[i].TTL, ttlStr);
        // Es un puntero a un substring del Token por lo que no se puede establer en lugar de token
        // Se hace free a token, NO a trimmedToken
        char *trimmedToken = trimwhitespace(token);
        strcpy(hosts[i].IP, trimmedToken);
        i++;
        token = strtok(NULL, ",");
    }
    /*
     * Libera toda la memoria usada para sacar los Hosts
     * 
     */
    free(ttlStr);
    free(ipStr);
    free(source);
    free(doc);
    free(docs);
    free(IP);
    free(TTL);
    free(INDEX);
    free(hitsTotalValue);
    free(hitsTotal);
    free(hits);
    free(parsedJson);
    /* Aqui va el round robin a "hosts" */
    char buffer[1024];
    char *url = "http://172.24.2.3:9200/zones/_update/";
    strcpy(buffer, url);
    strcat(buffer, id);

    struct curl_slist *list = NULL;
    list = curl_slist_append(list, "Content-Type: application/json");
    list = curl_slist_append(list, "Accept: */*");

    char data[] = "{\"script\":{\"source\":\"ctx._source.index += params.index\",\"lang\":\"painless\",\"params\":{\"index\":1}}}";
    curlRequest(buffer, data, list, 1, 1);

    return &hosts[(index%i)];
}

void sendToApi(unInt *bufferBytes, int n, int sockfd, struct sockaddr_in *cliaddr) {
    // La codifico a base 64
    char *encodeBytes = codeBase64(bufferBytes,n);

    printf("Encoded request: %s\n", encodeBytes);

    // Se generan los headers necesarios
    struct curl_slist *list = NULL;
    list = curl_slist_append(list, "Content-Type: text/plain");
    list = curl_slist_append(list, "Accept: */*");

    // Luego la envio al cliente https 
    struct decoded_response response =  decodeBase64(curlRequest("https://172.24.2.2:443/api/dns_resolver", encodeBytes, list, 1, 1));
    if (response.response == NULL){
        return;
    }

    char filename[200];
    memset(filename,0, sizeof(filename));
    sprintf(filename, "%s%d%s","response",index_xd, ".txt");
    index_xd++;

    /*
    FILE* response_file;
    response_file = fopen(filename, "wb");
    fwrite(response.response,1,response.len,response_file);
    fclose(response_file);
    */
    
    sendto(sockfd, (unInt *)response.response, response.len,
            MSG_CONFIRM, (const struct sockaddr *) cliaddr, n);


    free(response.response);
    free(encodeBytes);
}


unInt ipToDecimal(char * ipR){
    
    char * ip;
    ip = (char*)malloc(sizeof(char)*100);
    memset(ip,0,100);

    memcpy(ip, ipR, 100);

    char *token;
    token = strtok(ip, ".");
    
    unInt a = atol(token);
    a = a << 24;
    token = strtok(NULL, ".");
    
    unInt b = atol(token);
    b = b << 16;
    token = strtok(NULL, ".");
    
    unInt c = atol(token);
    c = c << 8;
    token = strtok(NULL, ".");
    
    unInt d = atol(token);
    //d = d << 8;

    a = a | b | c | d;
    return a;
}


int response_with_ttl_and_ip(struct decoded_response dr, Host* h, int n, int sockfd, struct sockaddr_in *cliaddr){

    unInt* bufferBytes = (unInt *) malloc( sizeof(unInt)*150);
    memset(bufferBytes,0,150);
    char *ttl = (char *) malloc(sizeof(char)*10);
    memset(ttl,0,10);
    char *ip = (char *) malloc(sizeof(char)*20);
    memset(ip,0,20);

    memcpy(bufferBytes, dr.response, sizeof(unInt)*150);
    size_t len = dr.len;
    //Para prueba

    uint8_t *ttl_entero = (uint8_t*) malloc(sizeof(uint8_t)*4); 
    
    //strcpy(ttl, "15");
    //strcpy(ip, "10.25.25.15");
    
    strcpy(ttl, h->TTL);
    strcpy(ip, h->IP);

    int temp_ttl = atoi(ttl);
    memcpy(ttl_entero, &temp_ttl,sizeof(int));

    uint8_t *ip_in_decimal = (uint8_t *) malloc(sizeof(unInt));
    unInt ip_temp = ipToDecimal(ip);

    memcpy(ip_in_decimal,&ip_temp, sizeof(ip_temp));
    uint8_t *start_of_response = (uint8_t *) (bufferBytes);

    *(start_of_response+6) = 0;
    *(start_of_response+7) = 1;

    uint8_t *iter = start_of_response + 12;

    int size = 13;

    while(*iter != 0){
        iter++;
        size++;
    }

    while(*iter == 0){
        iter++;
        size++;
    }
    *(iter+5) = 0;
    *(iter+6) = 1;

    //Meto el ttl
    *(iter+9) = *(ttl_entero+3);
    *(iter+10) = *(ttl_entero+2);
    *(iter+11) = *(ttl_entero+1);
    *(iter+12) = *(ttl_entero+0);

    iter += 14;
    size += 19;

    *iter = 4;

    iter++;
    *iter = *(ip_in_decimal+3);

    iter++;
    *iter = *(ip_in_decimal+2);

    iter++;
    *iter = *(ip_in_decimal+1);

    iter++;
    *iter = *ip_in_decimal;

    iter++;
    *iter = 0;

    printf("Size: %u\n", size);

    sendto(sockfd,(unInt *) bufferBytes, size,
            MSG_CONFIRM, (const struct sockaddr *) cliaddr, n);

    free(dr.response);
    printf("Termino de enviar paquete elastic\n");
    return 0;

}

void* handleMessage(void *args) {
    Args *argumentos = args;

    //unInt tiene tamaño para 4 bytes por lo que puedo guardar los primeros
    //32 bits del header del request del dns
    unInt qrAndOpcode;
    qrAndOpcode = argumentos->bufferBytes[0];


    //Reviso si el QR == 0
    //Elimino los primeros 16 bits
    unInt QR = (qrAndOpcode >> 31);

    //Elimino el QR si está en 1
    unInt OPCODE = (1 << qrAndOpcode);
    OPCODE = (OPCODE >> 28);

    printf("QR: %d\n", QR);
    printf("OPCODE: %d\n", OPCODE);
    
    //Si recibo un paquete diferente a querry estandar
    
    if (QR != 0 || OPCODE != 0){
        sendToApi(argumentos->bufferBytes, argumentos->n, argumentos->sockfd, argumentos->cliaddr);
    }
    //Si recibo un paquete tipo querry estandar
    else{
        char *hostname = (char *) malloc(sizeof(char)*256);
        memset(hostname, 0, strlen(hostname));
        strcpy(hostname, (char *) (argumentos->bufferBytes+3) + 1);

        for (int i = 0;i < strlen(hostname); i++) {
            if(((unsigned char) *(hostname+i)) < 48){
                hostname[i] = 46;
            }
        }
        /*
        printf("Temp: %d\n", *(((uint8_t *) (argumentos->bufferBytes)) + (strlen(hostname)) + 15));
        if (*(((uint8_t *) (argumentos->bufferBytes)) + (strlen(hostname)) + 15) == 28){
            sendToApi(argumentos->bufferBytes, argumentos->n, argumentos->sockfd, argumentos->cliaddr);
        }*/

        char jsonResponse[4097];
        memset(jsonResponse, 0, 4097);

        char buffer[4096];
        memset(buffer, 0, 4096);
        //"http://172.24.2.3:9200/zones/_doc/_search?q="
        char *url = "http://172.24.2.3:9200/zones/_doc/_search?q=";
        strcpy(buffer, url);
        strcat(buffer,hostname);

        printf("URL: %s\n",buffer);

        /* TODO: comentar si es necesario consistencia en index para round robin */
        //pthread_mutex_lock(&elk_mutex);

        strcpy(jsonResponse, curlRequest(buffer, "", NULL, 0, 1));
        

        if (jsonResponse[0] == '\0') {
            printf("Elasticsearch server DOWN!\n");
            return 0;
        }
        Host *selectedHost = RoundRobin(jsonResponse);


        
        /* TODO: comentar si es necesario consistencia en index para round robin */
        //pthread_mutex_unlock(&elk_mutex);

       
        
        if (selectedHost == NULL) {
            printf("No existe en elastic\n");
            sendToApi(argumentos->bufferBytes, argumentos->n, argumentos->sockfd, argumentos->cliaddr);
            return 0;
        }
        printf("Selecionado. IP: %s, TTL: %s\n", selectedHost->IP, selectedHost->TTL);
        struct decoded_response paquete = cliente_resolver(argumentos->bufferBytes, argumentos->n);
        if (response_with_ttl_and_ip(paquete,selectedHost, argumentos->n, argumentos->sockfd, argumentos->cliaddr)) {
            sendToApi(argumentos->bufferBytes, argumentos->n, argumentos->sockfd, argumentos->cliaddr);
        }


        /** TODO Crear paquete, paquete.response contiene los bytes del paquete. Se puede iniciar en el byte 13 ya que son 12 bytes de header **/
        //sendToApi(argumentos->bufferBytes, argumentos->n, argumentos->sockfd, argumentos->cliaddr);
    }
    return 0;
}

// Driver code 
int main() { 
    //Para almacenar los 32bytes del nslookup
    unInt *bufferBytes;
    bufferBytes = (unInt *) malloc( sizeof(unInt)*159); // allocate 8 unsigned int

    memset(bufferBytes,0,150);

    int sockfd; 
    struct sockaddr_in servaddr, cliaddr; 
        
    // Creating socket file descriptor 
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
    //limpio memoria
    memset(&servaddr, 0, sizeof(servaddr)); 
    memset(&cliaddr, 0, sizeof(cliaddr)); 
        
    //Lleno la información del server
    servaddr.sin_family    = AF_INET; // IPv4 
    servaddr.sin_addr.s_addr = INADDR_ANY; 
    servaddr.sin_port = htons(PORT); 
        
    // Bind the socket with the server address 
    if ( bind(sockfd, (const struct sockaddr *)&servaddr,sizeof(servaddr)) < 0 ){ 
        perror("bind failed"); 
        exit(EXIT_FAILURE); 
    } 
        
    int n; 
    socklen_t len = sizeof(cliaddr);  //len is value/result 

    // Setup curl
    curl_global_init(CURL_GLOBAL_DEFAULT);
    
    while (1){
        n = recvfrom(sockfd,bufferBytes,150,  
                MSG_WAITALL, ( struct sockaddr *) &cliaddr, 
                &len);

        pthread_t thread;

        /* Creación de los argumentos del hilo */
        Args *args = (Args*) malloc(sizeof(Args));
        args->bufferBytes = (uint *) malloc(sizeof(unInt)*159);
        memcpy(args->bufferBytes, bufferBytes, sizeof(unInt)*159);
        args->cliaddr = malloc(len);
        memcpy(args->cliaddr, (struct sockaddr *) &cliaddr, len);
        args->n = n;
        args->sockfd = sockfd;

        pthread_create(&thread, NULL, (void *)handleMessage, (void *) args);
    }
    curl_global_cleanup();
    return 0; 
    
}
