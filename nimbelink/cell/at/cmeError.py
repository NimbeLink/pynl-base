###
 # \file
 #
 # \brief AT interface utilities
 #
 # (C), NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding cyright notice of NimbeLink Corp.
 ##

class CmeError:
    """CME errors
    """

    PHONE_FAILURE                                       = 0
    NO_CONNECTION_TO_PHONE                              = 1
    PHONE_ADAPTER_LINK_RESERVED                         = 2
    OPERATION_NOT_ALLOWED                               = 3
    OPERATION_NOT_SUPPORTED                             = 4
    PH_SIM_PIN_REQUIRED                                 = 5
    PH_FSIM_PIN_REQUIRED                                = 6
    PH_FSIM_PUK_REQUIRED                                = 7
    SIM_NOT_INSERTED                                    = 10
    SIM_PIN_REQUIRED                                    = 11
    SIM_PUK_REQUIRED                                    = 12
    SIM_FAILURE                                         = 13
    SIM_BUSY                                            = 14
    SIM_WRONG                                           = 15
    INCORRECT_PASSWORD                                  = 16
    SIM_PIN2_REQUIRED                                   = 17
    SIM_PUK2_REQUIRED                                   = 18
    MEMORY_FULL                                         = 20
    INVALID_INDEX                                       = 21
    NOT_FOUND                                           = 22
    MEMORY_FAILURE                                      = 23
    TEXT_STRING_TOO_LONG                                = 24
    INVALID_CHARACTERS_IN_TEXT_STRING                   = 25
    DIAL_STRING_TOO_LONG                                = 26
    INVALID_CHARACTERS_IN_DIAL_STRING                   = 27
    NO_NETWORK_SERVICE                                  = 30
    NETWORK_TIMEOUT                                     = 31
    NETWORK_NOT_ALLOWED_EMERGENCY_CALLS_ONLY            = 32
    NETWORK_PERSONALIZATION_PIN_REQUIRED                = 40
    NETWORK_PERSONALIZATION_PUK_REQUIRED                = 41
    NETWORK_SUBSET_PERSONALIZATION_PIN_REQUIRED         = 42
    NETWORK_SUBSET_PERSONALIZATION_PUK_REQUIRED         = 43
    SERVICE_PROVIDER_PERSONALIZATION_PIN_REQUIRED       = 44
    SERVICE_PROVIDER_PERSONALIZATION_PUK_REQUIRED       = 45
    CORPORATE_PERSONALIZATION_PIN_REQUIRED              = 46
    CORPORATE_PERSONALIZATION_PUK_REQUIRED              = 47
    PH_SIM_PUK_REQUIRED                                 = 48
    INCORRECT_PARAMETERS                                = 50
    UNKNOWN_ERROR                                       = 100
    ILLEGAL_MS                                          = 103
    ILLEGAL_ME                                          = 106
    GPRS_SERVICES_NOT_ALLOWED                           = 107
    PLMN_NOT_ALLOWED                                    = 111
    LOCATION_AREA_NOT_ALLOWED                           = 112
    ROAMING_NOT_ALLOWED_IN_THIS_LOCATION_AREA           = 113
    OPERATION_TEMPORARY_NOT_ALLOWED                     = 126
    SERVICE_OPERATION_NOT_SUPPORTED                     = 132
    REQUESTED_SERVICE_OPTION_NOT_SUBSCRIBED             = 133
    SERVICE_OPTION_TEMPORARY_OUT_OF_ORDER               = 134
    UNSPECIFIED_GPRS_ERROR                              = 148
    PDP_AUTHENTICATION_FAILURE                          = 149
    INVALID_MOBILE_CLASS                                = 150
    OPERATION_TEMPORARILY_NOT_ALLOWED                   = 256
    CALL_BARRED                                         = 257
    PHONE_IS_BUSY                                       = 258
    USER_ABORT                                          = 259
    INVALID_DIAL_STRING                                 = 260
    SS_NOT_EXECUTED                                     = 261
    SIM_BLOCKED                                         = 262
    INVALID_BLOCK                                       = 263
    SIM_POWERED_DOWN                                    = 772

    @staticmethod
    def getName(code):
        """Gets the CME error name from its code

        :param code:
            The code to map

        :return None:
            Failed to map code
        :return String:
            The name of the code
        """

        for mapping in CmeError.__dict__.items():
            if mapping[1] == code:
                return mapping[0]

        return None

    @staticmethod
    def getCode(name):
        """Gets the CME error code from its name

        :param name;
            The name to map

        :return None:
            Failed to map name
        :return Integer:
            The code for the name
        """

        for mapping in CmeError.__dict__.items():
            if mapping[0] == name:
                return mapping[1]

        return None
