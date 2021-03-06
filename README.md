## Introduction 
Creates PEM, PKCS12 and JKS (Java Keystore) certificates, signed by the given
CA. Uses OpenSSL and Keytool (OpenJDK 7).

Usage example (assuming ```ca.crt``` and ```ca.key``` are in ```$PWD```):

```
docker run -it --rm -v $PWD:/certs/ -w /certs/ \
    -e MKCERT_SIGNING_CA="ca.crt"                      \
    -e MKCERT_SIGNING_CA_KEY="ca.key"                  \
    -e MKCERT_SERIAL_NUMBER=42                 \
    -e MKCERT_COMMON_NAME="Foo"                \
    daniperez/mkcert 
```

That command line will generate 3 certificates (.crt, .pkcs2 and .jks), a key (.key), a signing request (.csr) and it will print the password used to protect the key and the certificates.

## Parameters

```mkcert``` accepts parameters passed as environment variables. 
The **mandatory** ones are:

* ```MKCERT_COMMON_NAME```: name of the certificate's subject.
* ```MKCERT_SIGNING_CA```: file containing the CA certificate used to 
sign the certificates being generated. The path has to be valid within
the Docker container if Docker is used (see example below).
* ```MKCERT_SIGNING_CA_KEY```: file containing the key for the previous certificate.
The path has to be valid within the Docker container if Docker is used
(see example below).

Other accepted parameters are:

* ```MKCERT_KEY_LENGTH_BITS```: length in bits of the key to be generated. 
Default: 2048.
* ```MKCERT_VALIDITY_DAYS```: days the certificate will be valid. Default: 365.
* ```MKCERT_COUNTRY```: country of certificate's subject. Default: "".
* ```MKCERT_STATE```: country of certificate's subject. Default: "".
* ```MKCERT_LOCATION```: location of certificate's subject. Default: "".
* ```MKCERT_ORGANIZATION```: organization of certificate's subject.
Default: "".
* ```MKCERT_ORGANIZATION_UNIT```: organization unit of certificate's subject.
Default: "".
* ```MKCERT_SERIAL_NUMBER```: file containing the next serial number to use
or just a number to use. If a file is supplied, it has to be valid within the
Docker container if Docker is used (see example below).
* ```MKCERT_MAKE_CA```: whether to create a certificate for a CA or a simple
certificate. Default: "False".
* ```MKCERT_CA_CONF```: if ```MKCERT_MAKE_CA``` is true, this variable points to
the desired CA conf file to be used when creating a CA certificate.

## Usage

The easiest way to run this is with Docker. Assuming the CA certificate,
key and the serial number are in ```$PWD```:

```
docker run -it --rm -v $PWD:/certs/ -w /certs/ \
    -e MKCERT_CA=ca.crt                        \
    -e MKCERT_CA_KEY=ca.key                    \
    -e MKCERT_SERIAL_NUMBER=42                 \
    -e MKCERT_COMMON_NAME="Foo"                \
    daniperez/mkcert 
```

If you don't want to use Docker, just do:

```
MKCERT_COMMON_NAME="Foo" MKCERT_CA=ca.crt MKCERT_CA_KEY=ca.key MKCERT_SERIAL_NUMBER=42 ./mkcert.py
```

You'll see some things going on but at the end, and most important, you'll
get a summary if it succeeded to create the certificate:

```
(...)
=======
Summary
=======

 - Certificate            : Foo.crt
 - Certificate (pkcs12)   : Foo.p12
 - Certificate (keystore) : Foo.jks
 - Key file               : Foo.key
 - Validity               : 365 days 
 - Password               : BnlrSlkds
 ```

And _**pay attention to the final remarks!**_:

```
   NOTE: the same password is used for: 'Foo.p12', 'Foo.key' and 'Foo.jks'.
WARNING: remember to save serial number '42', or two certificates
         could get the same serial number in the future.
WARNING: store the certificates and the password in a safe place!
         Don't be the weakest link!
```

### Common errors

### Duplicate CA certificates

If you try to issue a CA certificate twice with the same
input parameters, you'll get the following:
```
failed to update database
TXT_DB error number 2
error: the certificate creation didn't succeed.
```
It suffices to change the CN of the CA your are creating or
remove the duplicate from the ```ca.index``` file.

### More duplicates

If you create 2 certificates with the same CN, they will use
the same ```.jks``` file. Keytool will try to update the keystore
with the same name but since we used another password to
write it the first time, it will fail with the following error:
```
keytool error: java.io.IOException: Keystore was tampered with, or password was incorrect
error: the certificate creation didn't succeed.
```
Just use another CN or remove the existing jks file if it's not used anymore.


### Fedora, SELinux & Docker cocktail 

If you get a SELinux error, you might need to execute the following command on
the folder that you want to mount as volumen in the container:

```
su -c "chcon -Rt svirt_sandbox_file_t ./"
```
