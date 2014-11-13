## Introduction 
Creates PEM, PKCS12 and JKS (Java Keystore) certificates, signed by the given
CA.

## Parameters

```mkcert``` accepts parameters passed as environment variables. 
The **mandatory** ones are:

* ```MKCERT_COMMON_NAME```: name of the certificate's subject.
* ```MKCERT_CA```: file containing the CA certificate used to 
sign the certificates being generated. The path has to be valid within
the Docker container if Docker is used (see example below).
* ```MKCERT_CA_KEY```: file containing the key for the previous certificate.
The path has to be valid within the Docker container if Docker is used
(see example below).
* ```MKCERT_SERIAL_NUMBER```: file containing the next serial number to use
or just a number to use. If a file is supplied, it has to be valid within the
Docker container if Docker is used (see example below).

Other accepted parameters are:

* ```MKCERT_KEY_LENGTH```: length in bits of the key to be generated. 
Default: 2048.
* ```MKCERT_VALIDITY```: days the certificate will be valid. Default: 365.
* ```MKCERT_COUNTRY```: country of certificate's subject. Default: "".
* ```MKCERT_STATE```: country of certificate's subject. Default: "".
* ```MKCERT_LOCATION```: location of certificate's subject. Default: "".
* ```MKCERT_ORGANIZATION```: organization of certificate's subject.
Default: "".
* ```MKCERT_ORGANIZATION_UNIT```: organization unit of certificate's subject.
Default: "".

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
 - Validity               : 999 days 
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

**Pay attention to the warnings** at the end of the summary!

### Note for Fedora users

If you get a SELinux error, you might need to execute the following command on
the folder that you want to mount as volumen in the container:

```
su -c "chcon -Rt svirt_sandbox_file_t ./"
```
