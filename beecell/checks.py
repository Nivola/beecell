# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte
import re
from logging import getLogger

logger = getLogger(__name__)


def check_tax_code(codice_fiscale):
    CODICE_REGEXP = "^[0-9A-Z]{16}$"
    SETDISP = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23]
    ORD_ZERO = ord("0")
    ORD_A = ord("A")

    if 16 != len(codice_fiscale):
        logger.error(
            "La lunghezza del codice fiscale non è corretta: il codice fiscale dovrebbe essere lungo esattamente 16 caratteri."
        )
        return False

    codice_fiscale = codice_fiscale.upper()
    match = re.match(CODICE_REGEXP, codice_fiscale)
    if not match:
        logger.error(
            "Il codice fiscale contiene dei caratteri non validi: i soli caratteri validi sono le lettere e le cifre."
        )
        return False

    s = 0
    for i in range(1, 14, 2):
        c = codice_fiscale[i]
        if c.isdigit():
            s += ord(c) - ORD_ZERO
        else:
            s += ord(c) - ORD_A
    for i in range(0, 15, 2):
        c = codice_fiscale[i]
        if c.isdigit():
            c = ord(c) - ORD_ZERO
        else:
            c = ord(c) - ORD_A
        s += SETDISP[c]
    if s % 26 + ORD_A != ord(codice_fiscale[15]):
        logger.error("Il codice fiscale non e' corretto: il codice di controllo non corrisponde.")
        return False

    return True


# print(check_tax_code("vllfpp77e09c133k"))
# print(check_tax_code("MCCGPP80E29L219I"))
# print(check_tax_code("NTNDVD73B24H355I"))
# print(check_tax_code("PDTMGB71E63L219W"))
# print(check_tax_code("srrplg74s09l219y"))

# print(check_tax_code("vllfpp77e09c133a"))
# print(check_tax_code("vllfpp77e09c133"))
# print(check_tax_code("vllfppAAe09c133k"))
