PARTNER_DETAILS_API = "http://edi.redingtonb2b.in/redcloudstaging/api/RedingtonCloudApi/GetPartner"
"""
:Method:
    GET
:Params:
    CustomerCode : Customer's (i.e Partner) JBA code
"""

ORDER_POSTING_API = "http://edi.redingtonb2b.in/RedCloudStaging/api/RedingtonCloudApi/Invoice"
"""
:Method:
    POST
:Format:
    {
        "Order_Number": "C100002",
        "CustomerCode": "S10003",
        "DueDate": "120316",
        "EcAccId": "",
        "PONumber": "PO00002",
        "Items": [
            {
                "itemCode": "AWSC0025",
                "lineQty": "1",
                "unitPrice": "199",
                "cashDiscount": "0"
            },
            {
                "itemCode": "AWSC0026",
                "lineQty": "1",
                "unitPrice": "299",
                "cashDiscount": "0"
            }
        ]
    }

    Field Explanation:
        EcAccId: Can be left blank
"""

DELIVERY_SEQUENCE_API = "http://edi.redingtonb2b.in/RedCloudStaging/api/RedingtonCloudApi/DeliverSequence"
"""
:Method:
    GET
:Params:
    CustomerCode : Customer's (i.e Partner) JBA code
"""

PARTNER_EMAIL_UPDATE = "http://edi.redingtonb2b.in/RedCloudStaging/api/RedingtonCloudApi/PartnerEmailAccountActivation"

"""
:Method:
    POST

 :Format:
    {"CustCode": "S12614", "Email1": "raja@test.com"}
"""
