#!/usr/bin/env python

import os
import sys
import base64
import random

#
# This tool creates client certificates. The process to create a
# server certificate is the same, there aren't any differences
# between client and server certificates, other than that the server
# won't need probably the p12 and jks certificates.
#


def fail():

    print "error: the certificate creation didn't succeed."

    sys.exit(1)


def random_string(N=9):

    return base64.urlsafe_b64encode(os.urandom(N))


if __name__ == "__main__":

    # Length of the key in bits
    key_length = os.getenv("MKCERT_KEY_LENGTH_BITS", "2048")
    # Validity in days
    validity_days = os.getenv("MKCERT_VALIDITY_DAYS", "365")
    # Serial number of the certificate
    serial_number = os.getenv("MKCERT_SERIAL_NUMBER",
                              "%s" % random.randint(0, 1 << 32))
    # Whether the certificate is for a CA or not.
    is_ca = os.getenv("MKCERT_MAKE_CA", "False").lower() not in (
        "false", "0", "f", "no")
    ca_config = os.getenv("MKCERT_CA_CONF", "ca.cnf")

    # Certificate subject (DN)
    country_code = os.getenv("MKCERT_COUNTRY", "US")
    state = os.getenv("MKCERT_STATE", "CA")
    location = os.getenv("MKCERT_LOCATION", "San Francisco")
    organization = os.getenv("MKCERT_ORGANIZATION", "Example Inc.")
    organization_unit = os.getenv("MKCERT_ORGANIZATION_UNIT",
                                  "Important Matters Group")

    common_name = os.environ["MKCERT_COMMON_NAME"]

    if os.getenv("MKCERT_SIGNING_CA"):
        ca = os.environ["MKCERT_SIGNING_CA"]
        ca_key = os.environ["MKCERT_SIGNING_CA_KEY"]
    else:
        print "No CA provided. Creating self-signed certificate."
        ca = None
        ca_key = None

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

    print "========================================= "
    print "Creating and signing the certificate      "
    print " (the password of the CA can be requested)"
    print "========================================= "
    if os.path.isfile(serial_number):
        if serial_number != "ca.serial":
            not os.system("cp %s ca.serial"
                          % serial_number) or fail()
    elif serial_number.isdigit():

        if len(serial_number) % 2:
            serial_number = "0%s" % serial_number

        not os.system("echo %s > ca.serial"
                      % serial_number) or fail()
    else:
        print("Invalid serial number, it's not a number or "
              "file [%s] doesn't exist or it isn't valid." % serial_number)
        fail()

    not os.system("touch ca.index") or fail()
    not os.system("touch ca.index.attr") or fail()
    not os.system("touch ca.serial") or fail()

    if is_ca:
        not os.system(
            "openssl req -x509 -batch -new -days %s -in '%s.csr' "
            "-subj '%s' "
            "-key %s.key "
            "-passin pass:%s "
            "-out '%s.crt'" % (
                validity_days, common_name,
                subject,
                common_name,
                password,
                common_name)
            ) or fail()
    else:
        not os.system(
            "openssl x509 -req -days %s "
            "-in '%s.csr' "
            "-CA %s -CAkey %s "
            "-CAserial ca.serial "
            "-out '%s.crt'" % (
                validity_days,
                common_name,
                ca, ca_key,
                common_name)
            ) or fail()

    print "================================================="
    print "Exporting a pkcs12 certificate (e.g. for Firefox)"
    print "================================================="
    not os.system(
        "openssl pkcs12 -export -nodes "
        "-out '%s.p12' -inkey '%s.key' -in '%s.crt' "
        "%s " 
        "-passin pass:%s -passout pass:%s"
        % (common_name, common_name, common_name,
           "-certfile %s " % ca if ca else "",
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
        "keytool -importkeystore -srckeystore \"%s.p12\" "
        "-srcstoretype PKCS12 -destkeystore \"%s.jks\" "
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
    print " - Validity               : %s days " % validity_days
    print " - Serial number          : %s " % serial_number
    print " - Password               : %s" % password
    print ""
    print("WARNING: the same password is used for: "
          "'%s.p12', '%s.key' and '%s.jks'." %
          (common_name, common_name, common_name))
    print("""WARNING: remember to save serial number '%s', or two certificates
         could get the same serial number in the future.""" % serial_number)
    print("""WARNING: store the certificates and the password in a safe place!
         Don't be the weakest link!""")
