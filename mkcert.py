#!/usr/bin/env python

import os
import sys
import base64

#
# This tool creates client certificates. The process to create a
# server certificate is the same, there aren't any differences
# between client and server certificates, other than that the server
# won't # need probably the p12 and jks certificates.
#
# If you want to create a CA for testing (and use self-signed
# certificates), you can create it as follows:
#
# > openssl genrsa 1024 > ca.key
# > openssl req -new -newkey rsa:1024 -x509 -days 365 \
#   -key ca.key -out ca.crt
#
# Or in one step:
#
# > openssl req -new -newkey rsa:1024 -x509 -days 365 \
#   -keyout ca.key -out ca.crt
#


def fail():

    print "error: the certificate creation didn't succeed."

    sys.exit(1)


def random_string(N=9):

    return base64.urlsafe_b64encode(os.urandom(N))


if __name__ == "__main__":

    key_length = os.getenv("MKCERT_KEY_LENGTH", "2048")
    validity = os.getenv("MKCERT_VALIDITY", "365")
    country_code = os.getenv("MKCERT_COUNTRY", "US")
    state = os.getenv("MKCERT_STATE", "CA")
    location = os.getenv("MKCERT_LOCATION", "San Francisco")
    organization = os.getenv("MKCERT_ORGANIZATION", "Example Inc.")
    organization_unit = os.getenv("MKCERT_ORGANIZATION_UNIT",
                                  "Important Matters Group")

    common_name = os.environ["MKCERT_COMMON_NAME"]
    ca = os.environ["MKCERT_CA"]
    ca_key = os.environ["MKCERT_CA_KEY"]
    serial_number = os.environ["MKCERT_SERIAL_NUMBER"]

    password = random_string()

    print "=========================================="
    print "Create certificate signing request and key"
    print "=========================================="
    subject = (
        "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s/" %
        (country_code, state, location, organization,
         organization_unit, common_name))

    not os.system(
        "openssl req -new -sha1 -newkey rsa:%s "
        "-batch -subj '%s' "
        "-keyout '%s.key' -out '%s.csr' "
        "-passout pass:%s"
        % (key_length, subject, common_name,
           common_name, password)) or fail()

    print "============================================"
    print "Creating and signing certificate with the CA"
    print " (the password of the CA can be requested) "
    print "============================================"
    if os.path.isfile(serial_number):
        serial_switch = "-CAserial %s" % serial_number
    else:
        serial_switch = "-set_serial %s" % serial_number

    not os.system(
        "openssl x509 -req -days %s "
        "-in '%s.csr' "
        "-CA %s -CAkey %s "
        "%s "
        "-out '%s.crt'" % (
            validity, common_name, ca, ca_key,
            serial_switch, common_name)) or fail()

    print "================================================="
    print "Exporting a pkcs12 certificate (e.g. for Firefox)"
    print "================================================="
    not os.system(
        "openssl pkcs12 -export "
        "-out '%s.p12' "
        "-inkey '%s.key' -in '%s.crt' "
        "-certfile %s "
        "-passin pass:%s -passout pass:%s"
        % (common_name, common_name, common_name, ca,
           password, password)) or fail()

    print ""
    print "==========================="
    print "Exporting a jks certificate"
    print "==========================="
    # Error "keytool error: java.io.IOException: Keystore was
    # tampered with, or  password was incorrect" means that the
    # certificate jks already exists and has another password.
    # Remove the certificate if you don't use it anymore.
    not os.system(
        "keytool -importkeystore -srckeystore '%s.p12' "
        "-srcstoretype PKCS12 -destkeystore '%s.jks' "
        "-deststorepass %s "
        "-srcstorepass %s "
        % (common_name, common_name, password, password)) or fail()

    print ""
    print "======="
    print "Summary"
    print "======="
    print ""
    print " - Certificate            : %s.crt" % common_name
    print " - Certificate (pkcs12)   : %s.p12" % common_name
    print " - Certificate (keystore) : %s.jks" % common_name
    print " - Key file               : %s.key" % common_name
    print " - Validity               : %s days " % validity
    print " - Password               : %s" % password
    print ""
    print("WARNING: the same password is used for: "
          "'%s.p12', '%s.key' and '%s.jks'." %
          (common_name, common_name, common_name))
    print("""WARNING: remember to save serial number '%s', or two certificates
         could get the same serial number in the future.""" % serial_number)
    print("""WARNING: store the certificates and the password in a safe place!
         Don't be the weakest link!""")
