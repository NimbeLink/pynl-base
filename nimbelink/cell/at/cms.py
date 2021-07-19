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

class CmsError:
    """CMS errors
    """

    UNASSIGNED_NUMBER                                   = 1
    OPERATOR_DETERMINED_BARRING                         = 8
    CALL_BARED                                          = 10
    SHORT_MESSAGE_TRANSFER_REJECTED                     = 21
    DESTINATION_OUT_OF_SERVICE                          = 27
    UNINDENTIFIED_SUBSCRIBER                            = 28
    FACILITY_REJECTED                                   = 29
    UNKNOWN_SUBSCRIBER                                  = 30
    NETWORK_OUT_OF_ORDER                                = 38
    TEMPORARY_FAILURE                                   = 41
    CONGESTION                                          = 42
    RECOURCES_UNAVAILABLE                               = 47
    REQUESTED_FACILITY_NOT_SUBSCRIBED                   = 50
    REQUESTED_FACILITY_NOT_IMPLEMENTED                  = 69
    INVALID_SHORT_MESSAGE_TRANSFER_REFERENCE_VALUE      = 81
    INVALID_MESSAGE_UNSPECIFIED                         = 95
    INVALID_MANDATORY_INFORMATION                       = 96
    MESSAGE_TYPE_NON_EXISTENT_OR_NOT_IMPLEMENTED        = 97
    MESSAGE_NOT_COMPATIBLE_WITH_SHORT_MESSAGE_PROTOCOL  = 98
    INFORMATION_ELEMENT_NON_EXISTENT_OR_NOT_IMPLEMENTE  = 99
    PROTOCOL_ERROR_UNSPECIFIED                          = 111
    INTERNETWORKING_UNSPECIFIED                         = 127
    TELEMATIC_INTERNETWORKING_NOT_SUPPORTED             = 128
    SHORT_MESSAGE_TYPE_0_NOT_SUPPORTED                  = 129
    CANNOT_REPLACE_SHORT_MESSAGE                        = 130
    UNSPECIFIED_TP_PID_ERROR                            = 143
    DATA_CODE_SCHEME_NOT_SUPPORTED                      = 144
    MESSAGE_CLASS_NOT_SUPPORTED                         = 145
    UNSPECIFIED_TP_DCS_ERROR                            = 159
    COMMAND_CANNOT_BE_ACTIONED                          = 160
    COMMAND_UNSUPPORTED                                 = 161
    UNSPECIFIED_TP_COMMAND_ERROR                        = 175
    TPDU_NOT_SUPPORTED                                  = 176
    SC_BUSY                                             = 192
    NO_SC_SUBSCRIPTION                                  = 193
    SC_SYSTEM_FAILURE                                   = 194
    INVALID_SME_ADDRESS                                 = 195
    DESTINATION_SME_BARRED                              = 196
    SM_REJECTED_DUPLICATE_SM                            = 197
    TP_VPF_NOT_SUPPORTED                                = 198
    TP_VP_NOT_SUPPORTED                                 = 199
    D0_SIM_SMS_STORAGE_FULL                             = 208
    NO_SMS_STORAGE_CAPABILITY_IN_SIM                    = 209
    ERROR_IN_MS                                         = 210
    MEMORY_CAPACITY_EXCEEDED                            = 211
    SIM_APPLICATION_TOOLKIT_BUSY                        = 212
    SIM_DATA_DOWNLOAD_ERROR                             = 213
    UNSPECIFIED_ERROR_CAUSE                             = 255
    ME_FAILURE                                          = 300
    SMS_SERVICE_OF_ME_RESERVED                          = 301
    OPERATION_NOT_ALLOWED                               = 302
    OPERATION_NOT_SUPPORTED                             = 303
    INVALID_PDU_MODE_PARAMETER                          = 304
    INVALID_TEXT_MODE_PARAMETER                         = 305
    SIM_NOT_INSERTED                                    = 310
    SIM_PIN_REQUIRED                                    = 311
    PH_SIM_PIN_REQUIRED                                 = 312
    SIM_FAILURE                                         = 313
    SIM_BUSY                                            = 314
    SIM_WRONG                                           = 315
    SIM_PUK_REQUIRED                                    = 316
    SIM_PIN2_REQUIRED                                   = 317
    SIM_PUK2_REQUIRED                                   = 318
    MEMORY_FAILURE                                      = 320
    INVALID_MEMORY_INDEX                                = 321
    MEMORY_FULL                                         = 322
    SMSC_ADDRESS_UNKNOWN                                = 330
    NO_NETWORK_SERVICE                                  = 331
    NETWORK_TIMEOUT                                     = 332
    NO_CNMA_EXPECTED                                    = 340
    UNKNOWN_ERROR                                       = 500
    USER_ABORT                                          = 512
    UNABLE_TO_STORE                                     = 513
    INVALID_STATUS                                      = 514
    DEVICE_BUSY_OR_INVALID_CHARACTER_IN_STRING          = 515
    INVALID_LENGTH                                      = 516
    INVALID_CHARACTER_IN_PDU                            = 517
    INVALID_PARAMETER                                   = 518
    INVALID_LENGTH_OR_CHARACTER                         = 519
    INVALID_CHARACTER_IN_TEXT                           = 520
    TIMER_EXPIRED                                       = 521
    OPERATION_TEMPORARY_NOT_ALLOWED                     = 522
    SIM_NOT_READY                                       = 532
    CELL_BROADCAST_ERROR_UNKNOWN                        = 534
    PROTOCOL_STACK_BUSY                                 = 535
    INVALID_PARAMETER2                                  = 538

    @staticmethod
    def getName(code):
        """Gets the CMS error name from its code

        :param code:
            The code to map

        :return None:
            Failed to map code
        :return String:
            The name of the code
        """

        for mapping in CmsError.__dict__.items():
            if mapping[1] == code:
                return mapping[0]

        return None

    @staticmethod
    def getCode(name):
        """Gets the CMS error code from its name

        :param name;
            The name to map

        :return None:
            Failed to map name
        :return Integer:
            The code for the name
        """

        for mapping in CmsError.__dict__.items():
            if mapping[0] == name:
                return mapping[1]

        return None
