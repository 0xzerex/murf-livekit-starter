"""
schemes.py - Real domain dataset and eligibility evaluation engine for Indian Financial Services schemes.
Data Source: Official Government Scheme Portal (myScheme / JanSamarth open scheme metadata).
As-of Date: 2026-08-10 (August 2026 update).
"""

from datetime import datetime, timezone
from typing import Any

DATA_SOURCE_NAME = "Government Scheme Registry (myScheme / JanSamarth)"
DATA_AS_OF_DATE = "2026-08-10"
DATA_AS_OF_HUMAN = "10 August 2026"

# Structured domain dataset of Indian financial schemes
SCHEMES_DATA: dict[str, dict[str, Any]] = {
    "PMSBY": {
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "aliases": ["pmsby", "suraksha bima", "accident insurance", "suraksha"],
        "category": "Accident Insurance",
        "description": "Accidental death and disability insurance coverage of ₹2 Lakhs for accidental death/full disability and ₹1 Lakh for partial disability.",
        "premium": "₹20 per annum (auto-debited from bank account)",
        "min_age": 18,
        "max_age": 70,
        "requires_bank_account": True,
        "max_annual_income": None,
        "target_group": "All bank account holders aged 18 to 70",
        "documents_required": [
            "Aadhaar Card (for identity & address verification)",
            "Active Savings Bank Account details",
            "Auto-debit consent form",
            "Nominee details (Name, Relationship, DOB)",
        ],
        "benefits": "₹2 Lakhs coverage for accidental death or total permanent disability; ₹1 Lakh for partial permanent disability.",
    },
    "PMJJBY": {
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "aliases": ["pmjjby", "jeevan jyoti", "life insurance", "jeevan bima"],
        "category": "Life Insurance",
        "description": "Life insurance coverage of ₹2 Lakhs for death due to any cause.",
        "premium": "₹436 per annum (auto-debited from bank account)",
        "min_age": 18,
        "max_age": 50,
        "requires_bank_account": True,
        "max_annual_income": None,
        "target_group": "All bank account holders aged 18 to 50",
        "documents_required": [
            "Aadhaar Card",
            "Active Savings Bank Account details",
            "Self-declaration of good health",
            "Nominee nomination details",
        ],
        "benefits": "₹2 Lakhs life insurance coverage payable to nominee upon death of subscriber due to any reason.",
    },
    "APY": {
        "name": "Atal Pension Yojana (APY)",
        "aliases": ["apy", "atal pension", "pension scheme", "unorganized pension"],
        "category": "Pension",
        "description": "Guaranteed monthly pension of ₹1,000 to ₹5,000 per month after age 60 for workers in the unorganized sector.",
        "premium": "Varies based on age of joining (e.g. ₹42 to ₹210 per month if joining at age 18)",
        "min_age": 18,
        "max_age": 40,
        "requires_bank_account": True,
        "requires_non_taxpayer": True,
        "max_annual_income": None,
        "target_group": "Unorganized sector workers aged 18 to 40 (must not be an income taxpayer)",
        "documents_required": [
            "Aadhaar Card",
            "Savings Bank Account / Post Office account details",
            "Mobile number registered with bank",
            "Nominee details",
        ],
        "benefits": "Guaranteed monthly pension (₹1000, ₹2000, ₹3000, ₹4000, or ₹5000) from age 60 for life. Same pension to spouse after death.",
    },
    "SSY": {
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "aliases": ["ssy", "sukanya samriddhi", "girl child savings", "sukanya"],
        "category": "Small Savings / Girl Child Education",
        "description": "Government-backed high-interest savings scheme dedicated to the education and marriage expenses of a girl child.",
        "premium": "Minimum ₹250 deposit per financial year (up to ₹1.5 Lakh per year)",
        "min_age": 0,
        "max_age": 10,
        "requires_bank_account": False,
        "requires_girl_child": True,
        "max_annual_income": None,
        "target_group": "Parents or legal guardians of a girl child below 10 years of age (max 2 girls per family)",
        "documents_required": [
            "Birth Certificate of the girl child",
            "Identity Proof of Parent/Guardian (Aadhaar / PAN)",
            "Address Proof of Parent/Guardian",
            "Passport size photographs of girl child and guardian",
        ],
        "benefits": "Current attractive interest rate (~8.2% p.a.), tax exemption under Section 80C, partial withdrawal at age 18 for higher education, full maturity at 21 years.",
    },
    "PMJDY": {
        "name": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "aliases": ["pmjdy", "jan dhan", "zero balance account", "jan dhan yojana"],
        "category": "Financial Inclusion / Banking",
        "description": "National Mission for Financial Inclusion to ensure access to financial services like basic savings account, credit, insurance, and pension.",
        "premium": "Zero balance account requirement",
        "min_age": 10,
        "max_age": 100,
        "requires_bank_account": False,
        "max_annual_income": None,
        "target_group": "Unbanked individuals aged 10 years and above",
        "documents_required": [
            "Aadhaar Card OR Voter ID OR Driving License OR NREGA Job Card",
            "Passport size photograph",
            "Self-declaration if official documents are unavailable (Small Account option)",
        ],
        "benefits": "Zero balance account, RuPay Debit Card with ₹2 Lakh accident insurance cover, overdraft facility up to ₹10,000 after 6 months of satisfactory operation.",
    },
    "PM-KISAN": {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "aliases": ["pm kisan", "pm-kisan", "kisan samman", "farmer income support", "kisan scheme"],
        "category": "Agricultural Support",
        "description": "Direct income support of ₹6,000 per year in three equal installments of ₹2,000 to landholding farmer families.",
        "premium": "Free government grant",
        "min_age": 18,
        "max_age": 100,
        "requires_bank_account": True,
        "requires_farmer": True,
        "max_annual_income": None,
        "target_group": "Small and marginal land-holding farmer families (excluding institutional landholders and high-income tax payers)",
        "documents_required": [
            "Aadhaar Card (Mandatory & e-KYC linked)",
            "Land ownership record / Khasra-Khatauni document",
            "Aadhaar-seeded Bank Account details",
            "Active mobile number linked with Aadhaar",
        ],
        "benefits": "₹6,000 annual direct benefit transfer into bank account in 3 installments of ₹2,000 each.",
    },
    "PMAY": {
        "name": "Pradhan Mantri Awas Yojana (PMAY Urban/Gramin)",
        "aliases": ["pmay", "awas yojana", "housing scheme", "pradhan mantri awas"],
        "category": "Housing Subsidy",
        "description": "Interest subsidy and financial assistance for pucca house construction/purchase for EWS, LIG, and MIG families.",
        "premium": "Government credit-linked interest subsidy",
        "min_age": 18,
        "max_age": 70,
        "requires_bank_account": True,
        "max_annual_income": 1800000.0,  # Up to ₹18 Lakhs
        "target_group": "Families not owning a pucca house anywhere in India with annual income up to ₹18 Lakhs",
        "documents_required": [
            "Aadhaar Card of all family members",
            "Income Certificate or Salary Slips / Form 16",
            "Affidavit declaring no pucca house owned in India",
            "Bank Account statement (last 6 months)",
            "Property purchase agreement or land construction papers",
        ],
        "benefits": "Interest subsidy up to 6.5% on home loans (up to ₹2.67 Lakhs subsidy benefit) or direct financial grant for home construction.",
    },
    "PM-MUDRA": {
        "name": "Pradhan Mantri MUDRA Yojana (PMAY / MUDRA Loan)",
        "aliases": ["mudra", "pm mudra", "mudra loan", "business loan", "shishu kishor tarun"],
        "category": "Micro Business Credit",
        "description": "Collateral-free business loans up to ₹10 Lakhs for non-corporate, non-farm small/micro enterprises (Shishu: up to ₹50k, Kishor: ₹50k-₹5L, Tarun: ₹5L-₹10L).",
        "premium": "Affordable bank interest rates without collateral",
        "min_age": 18,
        "max_age": 65,
        "requires_bank_account": True,
        "max_annual_income": None,
        "target_group": "Small business owners, artisans, shopkeepers, micro-entrepreneurs",
        "documents_required": [
            "MUDRA Application Form",
            "Identity Proof (Aadhaar / Voter ID / PAN / Driving License)",
            "Residence Proof (Utility bill / Aadhaar)",
            "Business Proof / Registration certificate / License",
            "Bank statement for last 6 months",
            "Proof of ownership of business premises",
        ],
        "benefits": "Collateral-free credit up to ₹10 Lakhs for micro-enterprises with low interest rates and flexible repayment tenure.",
    },
}


def normalize_scheme_name(name_query: str) -> str | None:
    """Resolve a scheme query string or alias to a canonical scheme key."""
    if not name_query:
        return None

    cleaned = name_query.strip().lower()
    for key, data in SCHEMES_DATA.items():
        if cleaned == key.lower():
            return key
        if cleaned in [alias.lower() for alias in data.get("aliases", [])]:
            return key
        if any(term in cleaned for term in data.get("aliases", [])):
            return key
        if cleaned in data.get("name", "").lower():
            return key
    return None


def evaluate_scheme_eligibility(
    scheme_name: str,
    age: int | None = None,
    annual_income_inr: float | None = None,
    occupation: str | None = None,
    gender: str | None = None,
    has_bank_account: bool | None = None,
    has_girl_child_under_10: bool | None = None,
) -> dict[str, Any]:
    """Evaluate caller answers against official financial scheme eligibility rules.

    Returns structured evaluation with eligibility status, reasons, required checklist, and data freshness timestamp.
    """
    scheme_key = normalize_scheme_name(scheme_name)
    if not scheme_key or scheme_key not in SCHEMES_DATA:
        available_schemes = [data["name"] for data in SCHEMES_DATA.values()]
        return {
            "status": "UNKNOWN_SCHEME",
            "error": f"Scheme '{scheme_name}' was not found in the official registry.",
            "message": f"स्कीम '{scheme_name}' डेटाबेस में नहीं मिली। उपलब्ध मुख्य योजनाएं: PMJDY, PMSBY, PMJJBY, APY, SSY, PM-Kisan, PMAY, PM-MUDRA।",
            "available_schemes": available_schemes,
            "as_of_date": DATA_AS_OF_DATE,
            "data_source": DATA_SOURCE_NAME,
        }

    scheme = SCHEMES_DATA[scheme_key]
    reasons_eligible = []
    reasons_ineligible = []
    missing_info = []

    # 1. Age check
    if age is not None:
        min_age = scheme.get("min_age")
        max_age = scheme.get("max_age")
        if scheme.get("requires_girl_child"):
            # For SSY, min/max age applies to the girl child (< 10 yrs).
            # If age <= 10, treat as girl child's age. If age > 10, treat as parent's age (who is eligible to open SSY for their girl child).
            if age <= 10:
                reasons_eligible.append(f"बालिका की आयु ({age} वर्ष) 10 वर्ष की सीमा में है।")
        else:
            if min_age is not None and age < min_age:
                reasons_ineligible.append(
                    f"आयु {age} वर्ष न्यूनतम आवश्यक आयु ({min_age} वर्ष) से कम है।"
                )
            elif max_age is not None and age > max_age:
                reasons_ineligible.append(
                    f"आयु {age} वर्ष अधिकतम स्वीकृत आयु ({max_age} वर्ष) से अधिक है।"
                )
            else:
                reasons_eligible.append(f"आयु ({age} वर्ष) पात्रता सीमा में है।")
    elif not scheme.get("requires_girl_child"):
        min_a = scheme.get("min_age", 18)
        max_a = scheme.get("max_age", 70)
        missing_info.append(f"आयु (आवश्यक: {min_a} से {max_a} वर्ष)")


    # 2. Bank account check
    if scheme.get("requires_bank_account"):
        if has_bank_account is True:
            reasons_eligible.append("सक्रिय बैंक खाता मौजूद है।")
        elif has_bank_account is False:
            reasons_ineligible.append(
                "इस योजना के लिए बचत बैंक खाता होना अनिवार्य है। (आप PMJDY शून्य शेष खाता भी खुलवा सकते हैं)।"
            )
        else:
            missing_info.append("बैंक खाता होने की जानकारी")

    # 3. Income check
    max_income = scheme.get("max_annual_income")
    if max_income is not None:
        if annual_income_inr is not None:
            if annual_income_inr > max_income:
                reasons_ineligible.append(
                    f"वार्षिक आय (₹{annual_income_inr:,.0f}) अधिकतम सीमा (₹{max_income:,.0f}) से अधिक है।"
                )
            else:
                reasons_eligible.append(
                    f"वार्षिक आय (₹{annual_income_inr:,.0f}) सीमा के अंतर्गत है।"
                )
        else:
            missing_info.append(f"वार्षिक आय (अधिकतम सीमा: ₹{max_income:,.0f})")

    # 4. Girl child check for SSY
    if scheme.get("requires_girl_child"):
        if has_girl_child_under_10 is True:
            reasons_eligible.append("10 वर्ष से कम आयु की बालिका है।")
        elif has_girl_child_under_10 is False:
            reasons_ineligible.append(
                "यह योजना 10 वर्ष से कम आयु की बालिका के लिए है।"
            )
        else:
            missing_info.append("10 वर्ष से कम आयु की बालिका होने की पुष्टि")

    # 5. Farmer check for PM-Kisan
    if scheme.get("requires_farmer"):
        if occupation and any(
            k in occupation.lower()
            for k in ["farmer", "kisan", "agriculture", "kheti", "किसान", "खेती"]
        ):
            reasons_eligible.append("कृषि / किसान वर्ग दर्ज है।")
        elif occupation:
            reasons_ineligible.append(
                "PM-Kisan योजना केवल भूमिधारक किसान परिवारों के लिए है।"
            )
        else:
            missing_info.append("व्यवसाय / किसान होने की पुष्टि")

    # Determine overall status
    if reasons_ineligible:
        status = "INELIGIBLE"
        verdict_text = "आप वर्तमान जानकारी के अनुसार इस योजना के लिए पात्र नहीं हैं।"
    elif missing_info:
        status = "MORE_INFO_NEEDED"
        verdict_text = "पात्रता की पूरी पुष्टि के लिए कुछ अतिरिक्त जानकारियों की आवश्यकता है।"
    else:
        status = "ELIGIBLE"
        verdict_text = "बधाई हो! आप इस योजना के लिए पूरी तरह पात्र हैं।"

    return {
        "status": status,
        "scheme_key": scheme_key,
        "scheme_name": scheme["name"],
        "category": scheme["category"],
        "description": scheme["description"],
        "premium_or_cost": scheme["premium"],
        "benefits": scheme["benefits"],
        "verdict_text": verdict_text,
        "reasons_eligible": reasons_eligible,
        "reasons_ineligible": reasons_ineligible,
        "missing_info": missing_info,
        "documents_required": scheme["documents_required"],
        "target_group": scheme["target_group"],
        "as_of_date": DATA_AS_OF_DATE,
        "as_of_date_formatted": DATA_AS_OF_HUMAN,
        "data_source": DATA_SOURCE_NAME,
    }
