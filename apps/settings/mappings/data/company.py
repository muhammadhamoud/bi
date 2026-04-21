# apps/settings/mappings/services/company_defaults.py

from django.db import transaction

from apps.settings.mappings.models import (
    CompanyCategory,
    CompanyGroup,
    CompanyMapping,
)

DEFAULT_COMPANY_INDUSTRY_STRUCTURE = [
    # Hospitality
    {
        "mapping_code": "HOTEL",
        "mapping_name": "Hotel",
        "category_code": "ACCOM",
        "category_name": "Accommodation",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },
    {
        "mapping_code": "RESORT",
        "mapping_name": "Resort",
        "category_code": "ACCOM",
        "category_name": "Accommodation",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },
    {
        "mapping_code": "SERV_APT",
        "mapping_name": "Serviced Apartment",
        "category_code": "ACCOM",
        "category_name": "Accommodation",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },
    {
        "mapping_code": "RESTAURANT",
        "mapping_name": "Restaurant",
        "category_code": "FNB",
        "category_name": "Food and Beverage",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },
    {
        "mapping_code": "CAFE",
        "mapping_name": "Cafe",
        "category_code": "FNB",
        "category_name": "Food and Beverage",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },
    {
        "mapping_code": "CATERING",
        "mapping_name": "Catering",
        "category_code": "FNB",
        "category_name": "Food and Beverage",
        "group_code": "HOSP",
        "group_name": "Hospitality",
    },

    # Real Estate
    {
        "mapping_code": "RES_DEV",
        "mapping_name": "Residential Developer",
        "category_code": "DEVEL",
        "category_name": "Development",
        "group_code": "REAL",
        "group_name": "Real Estate",
    },
    {
        "mapping_code": "COM_DEV",
        "mapping_name": "Commercial Developer",
        "category_code": "DEVEL",
        "category_name": "Development",
        "group_code": "REAL",
        "group_name": "Real Estate",
    },
    {
        "mapping_code": "PROP_MGMT",
        "mapping_name": "Property Management",
        "category_code": "MGMT",
        "category_name": "Management",
        "group_code": "REAL",
        "group_name": "Real Estate",
    },
    {
        "mapping_code": "BROKER",
        "mapping_name": "Brokerage",
        "category_code": "SERV",
        "category_name": "Services",
        "group_code": "REAL",
        "group_name": "Real Estate",
    },
    {
        "mapping_code": "FAC_MGMT",
        "mapping_name": "Facilities Management",
        "category_code": "SERV",
        "category_name": "Services",
        "group_code": "REAL",
        "group_name": "Real Estate",
    },

    # Retail
    {
        "mapping_code": "FASHION",
        "mapping_name": "Fashion Retail",
        "category_code": "STORE",
        "category_name": "Stores",
        "group_code": "RETL",
        "group_name": "Retail",
    },
    {
        "mapping_code": "GROCERY",
        "mapping_name": "Grocery Retail",
        "category_code": "STORE",
        "category_name": "Stores",
        "group_code": "RETL",
        "group_name": "Retail",
    },
    {
        "mapping_code": "ELEC",
        "mapping_name": "Electronics Retail",
        "category_code": "STORE",
        "category_name": "Stores",
        "group_code": "RETL",
        "group_name": "Retail",
    },
    {
        "mapping_code": "ECOM",
        "mapping_name": "E-commerce",
        "category_code": "DIGITAL",
        "category_name": "Digital Retail",
        "group_code": "RETL",
        "group_name": "Retail",
    },

    # Financial Services
    {
        "mapping_code": "BANK",
        "mapping_name": "Bank",
        "category_code": "BANKING",
        "category_name": "Banking",
        "group_code": "FIN",
        "group_name": "Financial Services",
    },
    {
        "mapping_code": "INSURANCE",
        "mapping_name": "Insurance Company",
        "category_code": "INS",
        "category_name": "Insurance",
        "group_code": "FIN",
        "group_name": "Financial Services",
    },
    {
        "mapping_code": "FINTECH",
        "mapping_name": "Fintech",
        "category_code": "FINTECH",
        "category_name": "Fintech",
        "group_code": "FIN",
        "group_name": "Financial Services",
    },
    {
        "mapping_code": "INVEST",
        "mapping_name": "Investment Firm",
        "category_code": "INV",
        "category_name": "Investments",
        "group_code": "FIN",
        "group_name": "Financial Services",
    },

    # Healthcare
    {
        "mapping_code": "HOSPITAL",
        "mapping_name": "Hospital",
        "category_code": "CARE",
        "category_name": "Care Providers",
        "group_code": "HLTH",
        "group_name": "Healthcare",
    },
    {
        "mapping_code": "CLINIC",
        "mapping_name": "Clinic",
        "category_code": "CARE",
        "category_name": "Care Providers",
        "group_code": "HLTH",
        "group_name": "Healthcare",
    },
    {
        "mapping_code": "DIAG",
        "mapping_name": "Diagnostics Center",
        "category_code": "SUPPORT",
        "category_name": "Support Services",
        "group_code": "HLTH",
        "group_name": "Healthcare",
    },
    {
        "mapping_code": "PHARMACY",
        "mapping_name": "Pharmacy",
        "category_code": "SUPPORT",
        "category_name": "Support Services",
        "group_code": "HLTH",
        "group_name": "Healthcare",
    },

    # Information Technology
    {
        "mapping_code": "SOFTWARE",
        "mapping_name": "Software Company",
        "category_code": "TECH",
        "category_name": "Technology",
        "group_code": "IT",
        "group_name": "Information Technology",
    },
    {
        "mapping_code": "SAAS",
        "mapping_name": "SaaS Provider",
        "category_code": "TECH",
        "category_name": "Technology",
        "group_code": "IT",
        "group_name": "Information Technology",
    },
    {
        "mapping_code": "IT_SERV",
        "mapping_name": "IT Services",
        "category_code": "SERV",
        "category_name": "Services",
        "group_code": "IT",
        "group_name": "Information Technology",
    },
    {
        "mapping_code": "CYBER",
        "mapping_name": "Cybersecurity",
        "category_code": "SERV",
        "category_name": "Services",
        "group_code": "IT",
        "group_name": "Information Technology",
    },

    # Logistics and Transportation
    {
        "mapping_code": "LOGISTICS",
        "mapping_name": "Logistics Provider",
        "category_code": "SUPPLY",
        "category_name": "Supply Chain",
        "group_code": "LOG",
        "group_name": "Logistics and Transportation",
    },
    {
        "mapping_code": "FREIGHT",
        "mapping_name": "Freight Services",
        "category_code": "SUPPLY",
        "category_name": "Supply Chain",
        "group_code": "LOG",
        "group_name": "Logistics and Transportation",
    },
    {
        "mapping_code": "TRANSPORT",
        "mapping_name": "Transport Operator",
        "category_code": "TRANS",
        "category_name": "Transport",
        "group_code": "LOG",
        "group_name": "Logistics and Transportation",
    },

    # Education
    {
        "mapping_code": "SCHOOL",
        "mapping_name": "School",
        "category_code": "INST",
        "category_name": "Institutions",
        "group_code": "EDU",
        "group_name": "Education",
    },
    {
        "mapping_code": "UNIVERSITY",
        "mapping_name": "University",
        "category_code": "INST",
        "category_name": "Institutions",
        "group_code": "EDU",
        "group_name": "Education",
    },
    {
        "mapping_code": "TRAINING",
        "mapping_name": "Training Institute",
        "category_code": "SERV",
        "category_name": "Services",
        "group_code": "EDU",
        "group_name": "Education",
    },

    # Media and Advertising
    {
        "mapping_code": "MEDIA",
        "mapping_name": "Media Company",
        "category_code": "MEDIA",
        "category_name": "Media",
        "group_code": "MDA",
        "group_name": "Media and Advertising",
    },
    {
        "mapping_code": "PUBLISH",
        "mapping_name": "Publisher",
        "category_code": "MEDIA",
        "category_name": "Media",
        "group_code": "MDA",
        "group_name": "Media and Advertising",
    },
    {
        "mapping_code": "AGENCY",
        "mapping_name": "Advertising Agency",
        "category_code": "ADV",
        "category_name": "Advertising",
        "group_code": "MDA",
        "group_name": "Media and Advertising",
    },

    # Manufacturing
    {
        "mapping_code": "IND_MAN",
        "mapping_name": "Industrial Manufacturing",
        "category_code": "MFG",
        "category_name": "Manufacturing",
        "group_code": "MFG",
        "group_name": "Manufacturing",
    },
    {
        "mapping_code": "CONS_MAN",
        "mapping_name": "Consumer Goods Manufacturing",
        "category_code": "MFG",
        "category_name": "Manufacturing",
        "group_code": "MFG",
        "group_name": "Manufacturing",
    },

    # Construction
    {
        "mapping_code": "CONTRACTOR",
        "mapping_name": "Contractor",
        "category_code": "BUILD",
        "category_name": "Building",
        "group_code": "CONS",
        "group_name": "Construction",
    },
    {
        "mapping_code": "ENGINEER",
        "mapping_name": "Engineering Services",
        "category_code": "BUILD",
        "category_name": "Building",
        "group_code": "CONS",
        "group_name": "Construction",
    },

    # Energy and Utilities
    {
        "mapping_code": "POWER",
        "mapping_name": "Power Utility",
        "category_code": "UTIL",
        "category_name": "Utilities",
        "group_code": "ENGY",
        "group_name": "Energy and Utilities",
    },
    {
        "mapping_code": "WATER",
        "mapping_name": "Water Utility",
        "category_code": "UTIL",
        "category_name": "Utilities",
        "group_code": "ENGY",
        "group_name": "Energy and Utilities",
    },
    {
        "mapping_code": "OIL_GAS",
        "mapping_name": "Oil and Gas",
        "category_code": "ENERGY",
        "category_name": "Energy",
        "group_code": "ENGY",
        "group_name": "Energy and Utilities",
    },

    # Professional Services
    {
        "mapping_code": "CONSULT",
        "mapping_name": "Consulting Firm",
        "category_code": "ADVISORY",
        "category_name": "Advisory",
        "group_code": "PROF",
        "group_name": "Professional Services",
    },
    {
        "mapping_code": "LEGAL",
        "mapping_name": "Legal Services",
        "category_code": "ADVISORY",
        "category_name": "Advisory",
        "group_code": "PROF",
        "group_name": "Professional Services",
    },
    {
        "mapping_code": "ACCOUNTING",
        "mapping_name": "Accounting Firm",
        "category_code": "ADVISORY",
        "category_name": "Advisory",
        "group_code": "PROF",
        "group_name": "Professional Services",
    },
    {
        "mapping_code": "MULTI_NAT",
        "mapping_name": "Multinational Company",
        "category_code": "CORP",
        "category_name": "Corporate Structure",
        "group_code": "PROF",
        "group_name": "Professional Services",
    },
]


def get_default_company_industry_structure():
    return list(DEFAULT_COMPANY_INDUSTRY_STRUCTURE)


@transaction.atomic
def seed_default_company_industries_for_property(property_obj, actor=None):
    structure = get_default_company_industry_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = CompanyGroup.objects.get_or_create(
            property=property_obj,
            code=group_code,
            defaults={
                "name": group_name,
                "sort_order": group_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if group.name != group_name:
            group.name = group_name
            changed = True
        if group.sort_order != group_index:
            group.sort_order = group_index
            changed = True
        if not group.is_active:
            group.is_active = True
            changed = True
        if actor and group.updated_by_id != actor.id:
            group.updated_by = actor
            changed = True

        if changed:
            group.save()

        group_cache[group_code] = group

    unique_categories = list(
        dict.fromkeys(
            (row["category_code"], row["category_name"], row["group_code"])
            for row in structure
        )
    )
    for category_index, (category_code, category_name, group_code) in enumerate(unique_categories, start=1):
        category_group = group_cache[group_code]
        category, _ = CompanyCategory.objects.get_or_create(
            property=property_obj,
            code=category_code,
            defaults={
                "name": category_name,
                "group": category_group,
                "sort_order": category_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if category.name != category_name:
            category.name = category_name
            changed = True
        if category.group_id != category_group.id:
            category.group = category_group
            changed = True
        if category.sort_order != category_index:
            category.sort_order = category_index
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True
        if actor and category.updated_by_id != actor.id:
            category.updated_by = actor
            changed = True

        if changed:
            category.save()

        category_cache[category_code] = category

    for mapping_index, row in enumerate(structure, start=1):
        mapping_category = category_cache[row["category_code"]]
        mapping, _ = CompanyMapping.objects.get_or_create(
            property=property_obj,
            code=row["mapping_code"],
            defaults={
                "name": row["mapping_name"],
                "category": mapping_category,
                "sort_order": mapping_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if mapping.name != row["mapping_name"]:
            mapping.name = row["mapping_name"]
            changed = True
        if mapping.category_id != mapping_category.id:
            mapping.category = mapping_category
            changed = True
        if mapping.sort_order != mapping_index:
            mapping.sort_order = mapping_index
            changed = True
        if not mapping.is_active:
            mapping.is_active = True
            changed = True
        if actor and mapping.updated_by_id != actor.id:
            mapping.updated_by = actor
            changed = True

        if changed:
            mapping.save()