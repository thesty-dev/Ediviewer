"""EDIFACT file parser."""

SEGMENT_NAMES = {
    "UNA": "Service String Advice",
    "UNB": "Interchange Header",
    "UNZ": "Interchange Trailer",
    "UNG": "Functional Group Header",
    "UNE": "Functional Group Trailer",
    "UNH": "Message Header",
    "UNT": "Message Trailer",
    "BGM": "Beginning of Message",
    "DTM": "Date/Time/Period",
    "NAD": "Name and Address",
    "LIN": "Line Item",
    "QTY": "Quantity",
    "MOA": "Monetary Amount",
    "PRI": "Price Details",
    "RFF": "Reference",
    "TAX": "Duty/Tax/Fee Details",
    "ALC": "Allowance or Charge",
    "PAC": "Package",
    "PIA": "Additional Product ID",
    "IMD": "Item Description",
    "MEA": "Measurements",
    "ALI": "Additional Information",
    "GIS": "General Indicator",
    "FTX": "Free Text",
    "SCC": "Scheduling Conditions",
    "CUX": "Currencies",
    "PAT": "Payment Terms Basis",
    "TDT": "Details of Transport",
    "TOD": "Terms of Delivery",
    "LOC": "Place/Location Identification",
    "TSR": "Transport Service Requirements",
    "CNT": "Control Total",
    "DOC": "Document/Message Details",
    "CTA": "Contact Information",
    "COM": "Communication Contact",
    "INP": "Parties to Instruction",
    "GIN": "Goods Identity Number",
    "EQD": "Equipment Details",
    "HAN": "Handling Instructions",
    "SGP": "Split Goods Placement",
    "TMP": "Temperature",
    "RNG": "Range Details",
    "DIM": "Dimensions",
    "SEL": "Seal Number",
    "FTX": "Free Text",
    "ORG": "Originator of Message Details",
    "ORD": "Order Status Information",
    "STS": "Status",
    "CST": "Customs Status of Goods",
    "ICD": "Insurance Cover Description",
    "BUS": "Business Function",
    "ATT": "Attribute",
    "APR": "Additional Price Information",
    "ARD": "Amounts Relationship Details",
    "GIR": "Related Identification Numbers",
    "ERC": "Application Error Information",
    "IFD": "Instructions to Despatch Party",
    "IRQ": "Information Required",
    "MKS": "Market/Sales Channel Information",
    "PGI": "Product Group Information",
    "PNA": "Party Identification",
    "PDI": "Person Demographic Information",
    "IDE": "Identity",
    "CMP": "Computer Environment Details",
    "SEQ": "Sequence Details",
    "OTM": "Off-Hire Time",
    "REL": "Relationship",
}

# Qualifier meanings for common data elements
QUALIFIERS = {
    "DTM": {
        "2": "Delivery date/time, requested",
        "7": "Effective date/time",
        "11": "Despatch date and/or time",
        "17": "Delivery date/time, estimated",
        "35": "Delivery date/time, actual",
        "36": "Expiry date",
        "37": "Ship not before date/time",
        "38": "Ship not later than date/time",
        "63": "Latest delivery date/time",
        "64": "Delivery date/time, promised for",
        "69": "Delivery date/time, promised for",
        "76": "Delivery date/time, scheduled for",
        "111": "Manufacture date",
        "124": "Delivery date/time, actual",
        "131": "Tax point date/time",
        "137": "Document/message date/time",
        "140": "Payment due date",
        "157": "Expiry date",
        "158": "Valid from date",
        "159": "Valid to date",
        "171": "Reference date/time",
        "178": "Calculation date/time",
        "179": "Payment date",
        "181": "Pick up / collection date/time",
        "182": "Customs declaration date",
        "191": "Invoice date",
        "200": "Pick-up date/time",
        "201": "Delivery date/time",
        "202": "Arrival date/time, estimated",
        "203": "Order date/time",
        "206": "Cancel if not delivered by this date",
        "209": "Delivery date/time, last",
        "232": "Coupon validity period",
        "233": "Effective from date",
        "234": "Period start date",
        "235": "Period end date",
        "243": "Date of renewal",
    },
    "NAD": {
        "BY": "Buyer",
        "SE": "Seller",
        "BS": "Bill and ship to",
        "DP": "Delivery party",
        "SU": "Supplier",
        "MS": "Message sender",
        "MR": "Message recipient",
        "ST": "Ship to",
        "UC": "Ultimate consignee",
        "CN": "Consignee",
        "CA": "Carrier",
        "FW": "Freight forwarder",
        "AG": "Agent",
        "GS": "Goods supplier",
        "II": "Issuer of invoice",
        "IV": "Invoicee",
        "OB": "Ordered by",
        "PA": "Paying agent",
        "PL": "Party paying freight",
        "RE": "Party to receive commercial invoice remittance",
        "BT": "Bill to",
        "PW": "Picking address",
        "WH": "Warehouse",
    },
    "QTY": {
        "1": "Discrete quantity",
        "2": "Charge quantity",
        "3": "Cumulative quantity",
        "6": "Invoiced quantity",
        "11": "Despatch quantity",
        "12": "Received quantity",
        "21": "Ordered quantity",
        "37": "Number of consumer units in the traded unit",
        "38": "Transport equipment quantity",
        "46": "Delivered quantity",
        "47": "Invoiced quantity, gross",
        "48": "Quantity per pack",
        "52": "Quantity, difference",
        "53": "Quantity, additional",
        "59": "Number of consumer units",
        "113": "Expired quantity",
        "145": "Received and accepted",
        "146": "Received, not accepted, to be returned",
        "147": "Received, not accepted, to be destroyed",
    },
    "MOA": {
        "1": "Payment amount",
        "2": "Charge amount",
        "4": "Advance payment amount",
        "5": "Charge/allowance basis",
        "8": "Allowance amount",
        "9": "Charge amount",
        "23": "Taxable amount",
        "25": "Payable amount",
        "31": "Net line item amount",
        "35": "Invoice amount",
        "36": "Message total monetary amount",
        "38": "Line item amount",
        "39": "Charged amount",
        "40": "Line item amount",
        "52": "Credit note amount",
        "53": "Invoice amount",
        "58": "Prepaid amount",
        "60": "Tax amount",
        "66": "Goods item total",
        "74": "Credit amount",
        "77": "Invoice total amount",
        "79": "Total charges/allowances",
        "86": "Total tax amount",
        "125": "Payment amount",
        "128": "Charge amount",
        "129": "Goods + services amount",
        "131": "Total amount",
        "132": "Tax amount",
        "140": "Total charges",
        "146": "Retentions",
        "150": "Paid amount",
        "165": "Remittance amount",
        "176": "Message total monetary amount",
        "204": "Debit note amount",
        "259": "VAT amount",
        "263": "Invoice total monetary amount",
        "265": "Tax amount",
    },
    "PRI": {
        "AAA": "Calculation net",
        "AAB": "Calculation gross",
        "AAC": "Calculation net incl. duty",
        "AAD": "Calculation net incl. freight",
        "AAE": "Calculation net incl. freight and duty",
        "INF": "Information price",
        "INV": "Invoice price",
    },
}


def parse_una(raw: str):
    """Extract separator characters from UNA segment."""
    if not raw.startswith("UNA"):
        return ":", "+", ".", "?", " ", "'"
    una = raw[3:9]
    if len(una) < 6:
        return ":", "+", ".", "?", " ", "'"
    return una[0], una[1], una[2], una[3], una[4], una[5]


def unescape(value: str, release: str) -> str:
    """Remove release characters."""
    if not release:
        return value
    result = []
    i = 0
    while i < len(value):
        if value[i] == release and i + 1 < len(value):
            result.append(value[i + 1])
            i += 2
        else:
            result.append(value[i])
            i += 1
    return "".join(result)


def split_with_release(text: str, separator: str, release: str) -> list:
    """Split string by separator, respecting release (escape) character."""
    parts = []
    current = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == release and i + 1 < len(text):
            current.append(ch)
            current.append(text[i + 1])
            i += 2
        elif ch == separator:
            parts.append("".join(current))
            current = []
            i += 1
        else:
            current.append(ch)
            i += 1
    parts.append("".join(current))
    return parts


def parse_edifact(content: str) -> dict:
    """Parse EDIFACT content and return structured result."""
    content = content.strip()

    # Detect and extract UNA
    comp_sep, data_sep, decimal, release, reserved, seg_term = ":", "+", ".", "?", " ", "'"
    if content.startswith("UNA"):
        comp_sep, data_sep, decimal, release, reserved, seg_term = parse_una(content)
        content = content[9:].lstrip()

    # Split into raw segments
    raw_segments = split_with_release(content, seg_term, release)

    segments = []
    for raw in raw_segments:
        raw = raw.strip()
        if not raw:
            continue

        data_elements_raw = split_with_release(raw, data_sep, release)
        tag = data_elements_raw[0].strip()
        elements = []

        for elem_raw in data_elements_raw[1:]:
            components = split_with_release(elem_raw, comp_sep, release)
            cleaned = [unescape(c, release) for c in components]
            elements.append(cleaned)

        qualifier = elements[0][0] if elements and elements[0] else ""
        qualifier_desc = QUALIFIERS.get(tag, {}).get(qualifier, "")

        segments.append({
            "tag": tag,
            "name": SEGMENT_NAMES.get(tag, "Unknown Segment"),
            "qualifier": qualifier,
            "qualifier_desc": qualifier_desc,
            "elements": elements,
            "raw": raw,
        })

    return {
        "separators": {
            "component": comp_sep,
            "data": data_sep,
            "decimal": decimal,
            "release": release,
            "segment": seg_term,
        },
        "segments": segments,
        "segment_count": len(segments),
    }
