from django.db import transaction

from apps.settings.mappings.models import (
    GuestCountryCategory,
    GuestCountryDetail,
    GuestCountryGroup,
    GuestCountryMapping,
)


GROUPS = {
    "EU": {"code": "EU", "name": "Europe"},
    "ME": {"code": "ME", "name": "Middle East"},
    "AF": {"code": "AF", "name": "Africa"},
    "AP": {"code": "AP", "name": "Asia Pacific"},
    "AM": {"code": "AM", "name": "Americas"},
    "OC": {"code": "OC", "name": "Oceania"},
    "OT": {"code": "OT", "name": "Other"},
    "UN": {"code": "UN", "name": "Unknown"},
}

CATEGORIES = {
    "EASTERN_EUROPE": {
        "group_code": "EU",
        "category_code": "EASTERN_EUROPE",
        "category_name": "Eastern Europe",
        "mapping_code": "EEU",
        "mapping_name": "Eastern Europe",
    },
    "NORTHERN_EUROPE": {
        "group_code": "EU",
        "category_code": "NORTHERN_EUROPE",
        "category_name": "Northern Europe",
        "mapping_code": "NEU",
        "mapping_name": "Northern Europe",
    },
    "SOUTHERN_EUROPE": {
        "group_code": "EU",
        "category_code": "SOUTHERN_EUROPE",
        "category_name": "Southern Europe",
        "mapping_code": "SEU",
        "mapping_name": "Southern Europe",
    },
    "WESTERN_EUROPE": {
        "group_code": "EU",
        "category_code": "WESTERN_EUROPE",
        "category_name": "Western Europe",
        "mapping_code": "WEU",
        "mapping_name": "Western Europe",
    },
    "GCC": {
        "group_code": "ME",
        "category_code": "GCC",
        "category_name": "GCC",
        "mapping_code": "GCC",
        "mapping_name": "GCC",
    },
    "REST_ARAB": {
        "group_code": "ME",
        "category_code": "REST_ARAB",
        "category_name": "Rest of Arab Countries",
        "mapping_code": "RAC",
        "mapping_name": "Rest of Arab Countries",
    },
    "MIDDLE_EAST_NON_ARAB": {
        "group_code": "ME",
        "category_code": "MIDDLE_EAST_NON_ARAB",
        "category_name": "Middle East Non-Arab",
        "mapping_code": "MENA",
        "mapping_name": "Middle East Non-Arab",
    },
    "NORTH_AFRICA": {
        "group_code": "AF",
        "category_code": "NORTH_AFRICA",
        "category_name": "North Africa",
        "mapping_code": "NAF",
        "mapping_name": "North Africa",
    },
    "SUB_SAHARAN_AFRICA": {
        "group_code": "AF",
        "category_code": "SUB_SAHARAN_AFRICA",
        "category_name": "Sub-Saharan Africa",
        "mapping_code": "SSA",
        "mapping_name": "Sub-Saharan Africa",
    },
    "NORTH_ASIA": {
        "group_code": "AP",
        "category_code": "NORTH_ASIA",
        "category_name": "North Asia",
        "mapping_code": "NAS",
        "mapping_name": "North Asia",
    },
    "SOUTH_ASIA": {
        "group_code": "AP",
        "category_code": "SOUTH_ASIA",
        "category_name": "South Asia",
        "mapping_code": "SAS",
        "mapping_name": "South Asia",
    },
    "SOUTHEAST_ASIA": {
        "group_code": "AP",
        "category_code": "SOUTHEAST_ASIA",
        "category_name": "Southeast Asia",
        "mapping_code": "SEA",
        "mapping_name": "Southeast Asia",
    },
    "EAST_ASIA": {
        "group_code": "AP",
        "category_code": "EAST_ASIA",
        "category_name": "East Asia",
        "mapping_code": "EAS",
        "mapping_name": "East Asia",
    },
    "CENTRAL_ASIA": {
        "group_code": "AP",
        "category_code": "CENTRAL_ASIA",
        "category_name": "Central Asia",
        "mapping_code": "CAS",
        "mapping_name": "Central Asia",
    },
    "NORTH_AMERICA": {
        "group_code": "AM",
        "category_code": "NORTH_AMERICA",
        "category_name": "North America",
        "mapping_code": "NAM",
        "mapping_name": "North America",
    },
    "CENTRAL_AMERICA": {
        "group_code": "AM",
        "category_code": "CENTRAL_AMERICA",
        "category_name": "Central America",
        "mapping_code": "CAM",
        "mapping_name": "Central America",
    },
    "CARIBBEAN": {
        "group_code": "AM",
        "category_code": "CARIBBEAN",
        "category_name": "Caribbean",
        "mapping_code": "CAR",
        "mapping_name": "Caribbean",
    },
    "SOUTH_AMERICA": {
        "group_code": "AM",
        "category_code": "SOUTH_AMERICA",
        "category_name": "South America",
        "mapping_code": "SAM",
        "mapping_name": "South America",
    },
    "OCEANIA": {
        "group_code": "OC",
        "category_code": "OCEANIA",
        "category_name": "Oceania",
        "mapping_code": "OCE",
        "mapping_name": "Oceania",
    },
    "OTHER": {
        "group_code": "OT",
        "category_code": "OTHER",
        "category_name": "Other",
        "mapping_code": "OTH",
        "mapping_name": "Other",
    },
    "UNKNOWN": {
        "group_code": "UN",
        "category_code": "UNKNOWN",
        "category_name": "Unknown",
        "mapping_code": "UNK",
        "mapping_name": "Unknown",
    },
}

DEFAULT_COUNTRY_STRUCTURE = [
    {"country_code": "AF", "country_name": "Afghanistan"},
    {"country_code": "AX", "country_name": "Aland Islands"},
    {"country_code": "AL", "country_name": "Albania"},
    {"country_code": "DZ", "country_name": "Algeria"},
    {"country_code": "AS", "country_name": "American Samoa"},
    {"country_code": "AD", "country_name": "Andorra"},
    {"country_code": "AO", "country_name": "Angola"},
    {"country_code": "AI", "country_name": "Anguilla/St Kitts"},
    {"country_code": "AQ", "country_name": "Antarctica"},
    {"country_code": "AG", "country_name": "Antigua and Barbuda"},
    {"country_code": "AR", "country_name": "Argentina"},
    {"country_code": "AM", "country_name": "Armenia"},
    {"country_code": "AW", "country_name": "Aruba"},
    {"country_code": "AU", "country_name": "Australia"},
    {"country_code": "AT", "country_name": "Austria"},
    {"country_code": "AZ", "country_name": "Azerbaijan"},
    {"country_code": "BS", "country_name": "Bahamas"},
    {"country_code": "BH", "country_name": "Bahrain"},
    {"country_code": "BD", "country_name": "Bangladesh"},
    {"country_code": "BB", "country_name": "Barbados"},
    {"country_code": "BY", "country_name": "Belarus"},
    {"country_code": "BE", "country_name": "Belgium"},
    {"country_code": "BZ", "country_name": "Belize"},
    {"country_code": "BJ", "country_name": "Benin"},
    {"country_code": "BM", "country_name": "Bermuda"},
    {"country_code": "BT", "country_name": "Bhutan"},
    {"country_code": "BO", "country_name": "Bolivia"},
    {"country_code": "BQ", "country_name": "Bonaire,Saba,St Eustatius"},
    {"country_code": "BA", "country_name": "Bosnia and Herzegovina"},
    {"country_code": "BW", "country_name": "Botswana"},
    {"country_code": "BV", "country_name": "Bouvet Island"},
    {"country_code": "BR", "country_name": "Brazil"},
    {"country_code": "IO", "country_name": "British Indian Ocean Territory"},
    {"country_code": "BN", "country_name": "Brunei Darussalam"},
    {"country_code": "BG", "country_name": "Bulgaria"},
    {"country_code": "BF", "country_name": "Burkina Faso"},
    {"country_code": "BI", "country_name": "Burundi"},
    {"country_code": "KH", "country_name": "Cambodia"},
    {"country_code": "CM", "country_name": "Cameroon"},
    {"country_code": "CA", "country_name": "Canada"},
    {"country_code": "CV", "country_name": "Cape Verde"},
    {"country_code": "KY", "country_name": "Cayman Islands"},
    {"country_code": "CF", "country_name": "Central African Republic"},
    {"country_code": "TD", "country_name": "Chad"},
    {"country_code": "CL", "country_name": "Chile"},
    {"country_code": "CN", "country_name": "China"},
    {"country_code": "CX", "country_name": "Christmas Island"},
    {"country_code": "CC", "country_name": "Cocos Islands, Keeling Islands"},
    {"country_code": "CO", "country_name": "Colombia"},
    {"country_code": "KM", "country_name": "Comoros"},
    {"country_code": "CG", "country_name": "Congo"},
    {"country_code": "CD", "country_name": "Congo, The Democratic Republic of the"},
    {"country_code": "CK", "country_name": "Cook Islands"},
    {"country_code": "CR", "country_name": "Costa Rica"},
    {"country_code": "CI", "country_name": "Cote D'Ivoire"},
    {"country_code": "HR", "country_name": "Croatia"},
    {"country_code": "CU", "country_name": "Cuba"},
    {"country_code": "CW", "country_name": "Curacao"},
    {"country_code": "CY", "country_name": "Cyprus"},
    {"country_code": "CZ", "country_name": "Czech Republic"},
    {"country_code": "DK", "country_name": "Denmark"},
    {"country_code": "DJ", "country_name": "Djibouti"},
    {"country_code": "RQ", "country_name": "Do Not Use-Russian Federation"},
    {"country_code": "FX", "country_name": "Do not Use - France"},
    {"country_code": "ZR", "country_name": "Do not Use -Zaire"},
    {"country_code": "DM", "country_name": "Dominica"},
    {"country_code": "DO", "country_name": "Dominican Republic"},
    {"country_code": "TP", "country_name": "East Timor"},
    {"country_code": "EC", "country_name": "Ecuador"},
    {"country_code": "EG", "country_name": "Egypt"},
    {"country_code": "SV", "country_name": "El Salvador"},
    {"country_code": "GQ", "country_name": "Equatorial Guinea"},
    {"country_code": "ER", "country_name": "Eritrea"},
    {"country_code": "EE", "country_name": "Estonia"},
    {"country_code": "ET", "country_name": "Ethiopia"},
    {"country_code": "FK", "country_name": "Falkland Islands, Malvinas"},
    {"country_code": "FO", "country_name": "Faroe Islands"},
    {"country_code": "FJ", "country_name": "Fiji"},
    {"country_code": "FI", "country_name": "Finland"},
    {"country_code": "FR", "country_name": "France"},
    {"country_code": "GF", "country_name": "French Guiana"},
    {"country_code": "PF", "country_name": "French Polynesia"},
    {"country_code": "TF", "country_name": "French Southern Territories"},
    {"country_code": "GA", "country_name": "Gabon"},
    {"country_code": "GM", "country_name": "Gambia"},
    {"country_code": "GE", "country_name": "Georgia"},
    {"country_code": "DE", "country_name": "Germany"},
    {"country_code": "GH", "country_name": "Ghana"},
    {"country_code": "GI", "country_name": "Gibraltar"},
    {"country_code": "GR", "country_name": "Greece"},
    {"country_code": "GL", "country_name": "Greenland"},
    {"country_code": "GD", "country_name": "Grenada"},
    {"country_code": "GP", "country_name": "Guadeloupe"},
    {"country_code": "GU", "country_name": "Guam"},
    {"country_code": "GT", "country_name": "Guatemala"},
    {"country_code": "GG", "country_name": "Guernsey"},
    {"country_code": "GN", "country_name": "Guinea"},
    {"country_code": "GW", "country_name": "Guinea Bissau"},
    {"country_code": "GY", "country_name": "Guyana"},
    {"country_code": "HT", "country_name": "Haiti"},
    {"country_code": "HM", "country_name": "Heard and McDonald Islands"},
    {"country_code": "VA", "country_name": "Holy See, Vatican City State"},
    {"country_code": "HN", "country_name": "Honduras"},
    {"country_code": "HK", "country_name": "Hong Kong, SAR of China"},
    {"country_code": "HU", "country_name": "Hungary"},
    {"country_code": "IS", "country_name": "Iceland"},
    {"country_code": "IN", "country_name": "India"},
    {"country_code": "ID", "country_name": "Indonesia"},
    {"country_code": "IR", "country_name": "Iran"},
    {"country_code": "IQ", "country_name": "Iraq"},
    {"country_code": "IE", "country_name": "Ireland"},
    {"country_code": "IM", "country_name": "Isle Of Man"},
    {"country_code": "IL", "country_name": "Israel"},
    {"country_code": "IT", "country_name": "Italy"},
    {"country_code": "JM", "country_name": "Jamaica"},
    {"country_code": "JP", "country_name": "Japan"},
    {"country_code": "JE", "country_name": "Jersey"},
    {"country_code": "JO", "country_name": "Jordan"},
    {"country_code": "KZ", "country_name": "Kazakhstan"},
    {"country_code": "KE", "country_name": "Kenya"},
    {"country_code": "KI", "country_name": "Kiribati"},
    {"country_code": "KR", "country_name": "Korea, Republic Of"},
    {"country_code": "KP", "country_name": "Korea,Democratic People's Republic of"},
    {"country_code": "XK", "country_name": "Kosovo"},
    {"country_code": "KW", "country_name": "Kuwait"},
    {"country_code": "KG", "country_name": "Kyrgzstan"},
    {"country_code": "LA", "country_name": "Lao, People's Democratic Republic"},
    {"country_code": "LV", "country_name": "Latvia"},
    {"country_code": "LB", "country_name": "Lebanon"},
    {"country_code": "LS", "country_name": "Lesotho"},
    {"country_code": "LR", "country_name": "Liberia"},
    {"country_code": "LY", "country_name": "Libya"},
    {"country_code": "LI", "country_name": "Liechtenstein"},
    {"country_code": "LT", "country_name": "Lithuania"},
    {"country_code": "LU", "country_name": "Luxembourg"},
    {"country_code": "MO", "country_name": "Macao, SAR of China"},
    {"country_code": "MG", "country_name": "Madagascar"},
    {"country_code": "MW", "country_name": "Malawi"},
    {"country_code": "MY", "country_name": "Malaysia"},
    {"country_code": "MV", "country_name": "Maldives"},
    {"country_code": "ML", "country_name": "Mali"},
    {"country_code": "MT", "country_name": "Malta"},
    {"country_code": "MH", "country_name": "Marshall Islands"},
    {"country_code": "MQ", "country_name": "Martinique"},
    {"country_code": "MR", "country_name": "Mauritania"},
    {"country_code": "MU", "country_name": "Mauritius"},
    {"country_code": "YT", "country_name": "Mayotte"},
    {"country_code": "MX", "country_name": "Mexico"},
    {"country_code": "FM", "country_name": "Micronesia, Federated States of"},
    {"country_code": "MI", "country_name": "Midway Islands"},
    {"country_code": "MD", "country_name": "Moldova"},
    {"country_code": "MC", "country_name": "Monaco"},
    {"country_code": "MN", "country_name": "Mongolia"},
    {"country_code": "ME", "country_name": "Montenegro"},
    {"country_code": "MS", "country_name": "Montserrat"},
    {"country_code": "MA", "country_name": "Morocco"},
    {"country_code": "MZ", "country_name": "Mozambique"},
    {"country_code": "MM", "country_name": "Myanmar"},
    {"country_code": "NA", "country_name": "Namibia"},
    {"country_code": "NR", "country_name": "Nauru"},
    {"country_code": "NP", "country_name": "Nepal"},
    {"country_code": "NL", "country_name": "Netherlands"},
    {"country_code": "AN", "country_name": "Netherlands Antilles"},
    {"country_code": "NC", "country_name": "New Caledonia"},
    {"country_code": "NZ", "country_name": "New Zealand"},
    {"country_code": "NI", "country_name": "Nicaragua"},
    {"country_code": "NE", "country_name": "Niger"},
    {"country_code": "NG", "country_name": "Nigeria"},
    {"country_code": "NU", "country_name": "Niue"},
    {"country_code": "NF", "country_name": "Norfolk Island"},
    {"country_code": "MK", "country_name": "North Macedonia"},
    {"country_code": "MP", "country_name": "Northern Mariana Islands"},
    {"country_code": "NO", "country_name": "Norway"},
    {"country_code": "OM", "country_name": "Oman"},
    {"country_code": "PK", "country_name": "Pakistan"},
    {"country_code": "PW", "country_name": "Palau"},
    {"country_code": "PS", "country_name": "Palestine"},
    {"country_code": "PA", "country_name": "Panama"},
    {"country_code": "PG", "country_name": "Papua New Guinea"},
    {"country_code": "PY", "country_name": "Paraguay"},
    {"country_code": "PE", "country_name": "Peru"},
    {"country_code": "PH", "country_name": "Philippines"},
    {"country_code": "PN", "country_name": "Pitcairn"},
    {"country_code": "PL", "country_name": "Poland"},
    {"country_code": "PT", "country_name": "Portugal"},
    {"country_code": "PR", "country_name": "Puerto Rico"},
    {"country_code": "QA", "country_name": "Qatar"},
    {"country_code": "RE", "country_name": "Reunion"},
    {"country_code": "RO", "country_name": "Romania"},
    {"country_code": "RU", "country_name": "Russian Federation"},
    {"country_code": "RW", "country_name": "Rwanda"},
    {"country_code": "BL", "country_name": "Saint Barthelemy"},
    {"country_code": "SH", "country_name": "Saint Helena, Ascension, Tristan"},
    {"country_code": "KN", "country_name": "Saint Kitts and Nevis"},
    {"country_code": "LC", "country_name": "Saint Lucia"},
    {"country_code": "MF", "country_name": "Saint Martin"},
    {"country_code": "PM", "country_name": "Saint Pierre and Miquelon"},
    {"country_code": "VC", "country_name": "Saint Vincent and Grenadines"},
    {"country_code": "WS", "country_name": "Samoa"},
    {"country_code": "SM", "country_name": "San Marino"},
    {"country_code": "ST", "country_name": "Sao Tome and Principe"},
    {"country_code": "SA", "country_name": "Saudi Arabia"},
    {"country_code": "SN", "country_name": "Senegal"},
    {"country_code": "RS", "country_name": "Serbia"},
    {"country_code": "SC", "country_name": "Seychelles"},
    {"country_code": "SL", "country_name": "Sierra Leone"},
    {"country_code": "SG", "country_name": "Singapore"},
    {"country_code": "SX", "country_name": "Sint Maarten"},
    {"country_code": "SK", "country_name": "Slovakia"},
    {"country_code": "SI", "country_name": "Slovenia"},
    {"country_code": "SB", "country_name": "Solomon Islands"},
    {"country_code": "SO", "country_name": "Somalia"},
    {"country_code": "ZA", "country_name": "South Africa"},
    {"country_code": "GS", "country_name": "South Georgia and the South Sandwich Islands"},
    {"country_code": "SS", "country_name": "South Sudan"},
    {"country_code": "ES", "country_name": "Spain"},
    {"country_code": "LK", "country_name": "Sri Lanka"},
    {"country_code": "SD", "country_name": "Sudan"},
    {"country_code": "SR", "country_name": "Suriname"},
    {"country_code": "SJ", "country_name": "Svalbard and Jan Mayen Islands"},
    {"country_code": "SZ", "country_name": "Swaziland"},
    {"country_code": "SE", "country_name": "Sweden"},
    {"country_code": "CH", "country_name": "Switzerland"},
    {"country_code": "SY", "country_name": "Syrian Arab Republic"},
    {"country_code": "TW", "country_name": "Taiwan, Province of China"},
    {"country_code": "TJ", "country_name": "Tajikistan"},
    {"country_code": "TZ", "country_name": "Tanzania, United Republic of"},
    {"country_code": "TH", "country_name": "Thailand"},
    {"country_code": "TL", "country_name": "Timor Leste"},
    {"country_code": "TG", "country_name": "Togo"},
    {"country_code": "TK", "country_name": "Tokelau"},
    {"country_code": "TO", "country_name": "Tonga"},
    {"country_code": "TT", "country_name": "Trinidad And Tobago"},
    {"country_code": "TN", "country_name": "Tunisia"},
    {"country_code": "TR", "country_name": "Turkiye"},
    {"country_code": "TM", "country_name": "Turkmenistan"},
    {"country_code": "TC", "country_name": "Turks and Caicos Islands"},
    {"country_code": "TV", "country_name": "Tuvalu"},
    {"country_code": "VI", "country_name": "US Virgin Islands"},
    {"country_code": "UG", "country_name": "Uganda"},
    {"country_code": "UA", "country_name": "Ukraine"},
    {"country_code": "AE", "country_name": "United Arab Emirates"},
    {"country_code": "GB", "country_name": "United Kingdon, Great Britain"},
    {"country_code": "UM", "country_name": "United States Minor Outlying Islands"},
    {"country_code": "US", "country_name": "United States of America"},
    {"country_code": "UY", "country_name": "Uruguay"},
    {"country_code": "UZ", "country_name": "Uzbekistan"},
    {"country_code": "VU", "country_name": "Vanuatu"},
    {"country_code": "VE", "country_name": "Venezuela"},
    {"country_code": "VN", "country_name": "Vietnam"},
    {"country_code": "VG", "country_name": "Virgin Islands, British"},
    {"country_code": "WF", "country_name": "Wallis and Futuna"},
    {"country_code": "EH", "country_name": "Western Sahara"},
    {"country_code": "YE", "country_name": "Yemen"},
    {"country_code": "ZM", "country_name": "Zambia"},
    {"country_code": "ZW", "country_name": "Zimbabwe"},
    {"country_code": "XX", "country_name": "Unknown"},
]

COUNTRY_CATEGORY_MAP = {
    "Russian Federation": "EASTERN_EUROPE",
    "Russia": "EASTERN_EUROPE",
    "Ukraine": "EASTERN_EUROPE",
    "Belarus": "EASTERN_EUROPE",
    "Azerbaijan": "EASTERN_EUROPE",
    "Romania": "EASTERN_EUROPE",
    "Bulgaria": "EASTERN_EUROPE",
    "Georgia": "EASTERN_EUROPE",
    "Poland": "EASTERN_EUROPE",
    "Kazakhstan": "CENTRAL_ASIA",
    "Armenia": "EASTERN_EUROPE",
    "Kyrgzstan": "CENTRAL_ASIA",
    "Hungary": "EASTERN_EUROPE",
    "Czech Republic": "EASTERN_EUROPE",
    "Moldova": "EASTERN_EUROPE",
    "Uzbekistan": "CENTRAL_ASIA",
    "Slovakia": "EASTERN_EUROPE",
    "Turkmenistan": "CENTRAL_ASIA",
    "Tajikistan": "CENTRAL_ASIA",

    "United Kingdon, Great Britain": "NORTHERN_EUROPE",
    "Norway": "NORTHERN_EUROPE",
    "Iceland": "NORTHERN_EUROPE",
    "Ireland": "NORTHERN_EUROPE",
    "Lithuania": "NORTHERN_EUROPE",
    "Sweden": "NORTHERN_EUROPE",
    "Denmark": "NORTHERN_EUROPE",
    "Finland": "NORTHERN_EUROPE",
    "Latvia": "NORTHERN_EUROPE",
    "Faroe Islands": "NORTHERN_EUROPE",
    "Estonia": "NORTHERN_EUROPE",

    "Turkiye": "SOUTHERN_EUROPE",
    "Greece": "SOUTHERN_EUROPE",
    "North Macedonia": "SOUTHERN_EUROPE",
    "Spain": "SOUTHERN_EUROPE",
    "Italy": "SOUTHERN_EUROPE",
    "Portugal": "SOUTHERN_EUROPE",
    "Malta": "SOUTHERN_EUROPE",
    "Montenegro": "SOUTHERN_EUROPE",
    "Bosnia and Herzegovina": "SOUTHERN_EUROPE",
    "Gibraltar": "SOUTHERN_EUROPE",
    "Serbia": "SOUTHERN_EUROPE",
    "Croatia": "SOUTHERN_EUROPE",
    "Cyprus": "SOUTHERN_EUROPE",
    "Albania": "SOUTHERN_EUROPE",
    "Kosovo": "SOUTHERN_EUROPE",
    "Slovenia": "SOUTHERN_EUROPE",
    "San Marino": "SOUTHERN_EUROPE",
    "Andorra": "SOUTHERN_EUROPE",

    "France": "WESTERN_EUROPE",
    "Switzerland": "WESTERN_EUROPE",
    "Belgium": "WESTERN_EUROPE",
    "Germany": "WESTERN_EUROPE",
    "Netherlands": "WESTERN_EUROPE",
    "Austria": "WESTERN_EUROPE",
    "Luxembourg": "WESTERN_EUROPE",
    "Liechtenstein": "WESTERN_EUROPE",
    "Monaco": "WESTERN_EUROPE",

    "United Arab Emirates": "GCC",
    "Saudi Arabia": "GCC",
    "Kuwait": "GCC",
    "Bahrain": "GCC",
    "Qatar": "GCC",
    "Oman": "GCC",

    "Jordan": "REST_ARAB",
    "Iraq": "REST_ARAB",
    "Syrian Arab Republic": "REST_ARAB",
    "Lebanon": "REST_ARAB",
    "Yemen": "REST_ARAB",
    "Palestine": "REST_ARAB",

    "Israel": "MIDDLE_EAST_NON_ARAB",
    "Iran": "MIDDLE_EAST_NON_ARAB",
    "Afghanistan": "MIDDLE_EAST_NON_ARAB",

    "Libya": "NORTH_AFRICA",
    "Morocco": "NORTH_AFRICA",
    "Egypt": "NORTH_AFRICA",
    "Algeria": "NORTH_AFRICA",
    "Tunisia": "NORTH_AFRICA",
    "Western Sahara": "NORTH_AFRICA",

    "Canada": "NORTH_AMERICA",
    "United States of America": "NORTH_AMERICA",
    "United States Minor Outlying Islands": "NORTH_AMERICA",
    "Saint Pierre and Miquelon": "NORTH_AMERICA",

    "Belize": "CENTRAL_AMERICA",
    "Costa Rica": "CENTRAL_AMERICA",
    "El Salvador": "CENTRAL_AMERICA",
    "Honduras": "CENTRAL_AMERICA",
    "Mexico": "CENTRAL_AMERICA",
    "Nicaragua": "CENTRAL_AMERICA",
    "Panama": "CENTRAL_AMERICA",
    "Guatemala": "CENTRAL_AMERICA",

    "Bahamas": "CARIBBEAN",
    "Barbados": "CARIBBEAN",
    "Bermuda": "CARIBBEAN",
    "Cayman Islands": "CARIBBEAN",
    "Cuba": "CARIBBEAN",
    "Curacao": "CARIBBEAN",
    "Dominica": "CARIBBEAN",
    "Dominican Republic": "CARIBBEAN",
    "Guadeloupe": "CARIBBEAN",
    "Haiti": "CARIBBEAN",
    "Jamaica": "CARIBBEAN",
    "Martinique": "CARIBBEAN",
    "Montserrat": "CARIBBEAN",
    "Puerto Rico": "CARIBBEAN",
    "Saint Kitts and Nevis": "CARIBBEAN",
    "Saint Lucia": "CARIBBEAN",
    "Saint Vincent and Grenadines": "CARIBBEAN",
    "Sint Maarten": "CARIBBEAN",
    "Trinidad And Tobago": "CARIBBEAN",
    "US Virgin Islands": "CARIBBEAN",
    "Virgin Islands, British": "CARIBBEAN",
    "Aruba": "CARIBBEAN",
    "Turks and Caicos Islands": "CARIBBEAN",
    "Antigua and Barbuda": "CARIBBEAN",
    "Bonaire,Saba,St Eustatius": "CARIBBEAN",
    "Anguilla/St Kitts": "CARIBBEAN",
    "Netherlands Antilles": "CARIBBEAN",

    "Argentina": "SOUTH_AMERICA",
    "Brazil": "SOUTH_AMERICA",
    "Chile": "SOUTH_AMERICA",
    "Colombia": "SOUTH_AMERICA",
    "Guyana": "SOUTH_AMERICA",
    "Paraguay": "SOUTH_AMERICA",
    "Peru": "SOUTH_AMERICA",
    "Uruguay": "SOUTH_AMERICA",
    "Venezuela": "SOUTH_AMERICA",
    "Bolivia": "SOUTH_AMERICA",
    "Suriname": "SOUTH_AMERICA",
    "Ecuador": "SOUTH_AMERICA",
    "French Guiana": "SOUTH_AMERICA",

    "Japan": "NORTH_ASIA",
    "Korea, Republic Of": "NORTH_ASIA",
    "Korea,Democratic People's Republic of": "NORTH_ASIA",
    "Mongolia": "NORTH_ASIA",

    "India": "SOUTH_ASIA",
    "Bangladesh": "SOUTH_ASIA",
    "Sri Lanka": "SOUTH_ASIA",
    "Nepal": "SOUTH_ASIA",
    "Pakistan": "SOUTH_ASIA",
    "Bhutan": "SOUTH_ASIA",
    "Maldives": "SOUTH_ASIA",

    "Thailand": "SOUTHEAST_ASIA",
    "Vietnam": "SOUTHEAST_ASIA",
    "Singapore": "SOUTHEAST_ASIA",
    "Malaysia": "SOUTHEAST_ASIA",
    "Indonesia": "SOUTHEAST_ASIA",
    "Philippines": "SOUTHEAST_ASIA",
    "Cambodia": "SOUTHEAST_ASIA",
    "Myanmar": "SOUTHEAST_ASIA",
    "Lao, People's Democratic Republic": "SOUTHEAST_ASIA",
    "Brunei Darussalam": "SOUTHEAST_ASIA",
    "Timor Leste": "SOUTHEAST_ASIA",
    "East Timor": "SOUTHEAST_ASIA",

    "China": "EAST_ASIA",
    "Hong Kong, SAR of China": "EAST_ASIA",
    "Macao, SAR of China": "EAST_ASIA",
    "Taiwan, Province of China": "EAST_ASIA",

    "Australia": "OCEANIA",
    "New Zealand": "OCEANIA",
    "Fiji": "OCEANIA",
    "Papua New Guinea": "OCEANIA",
    "Samoa": "OCEANIA",
    "Solomon Islands": "OCEANIA",
    "Tonga": "OCEANIA",
    "Tuvalu": "OCEANIA",
    "Vanuatu": "OCEANIA",
    "Wallis and Futuna": "OCEANIA",
    "New Caledonia": "OCEANIA",
    "Guam": "OCEANIA",
    "Northern Mariana Islands": "OCEANIA",
    "Palau": "OCEANIA",
    "Micronesia, Federated States of": "OCEANIA",
    "Nauru": "OCEANIA",
    "Marshall Islands": "OCEANIA",
    "Cook Islands": "OCEANIA",
    "Tokelau": "OCEANIA",
    "Niue": "OCEANIA",
    "American Samoa": "OCEANIA",
    "Kiribati": "OCEANIA",
    "French Polynesia": "OCEANIA",
    "Pitcairn": "OCEANIA",
    "Norfolk Island": "OCEANIA",
    "Christmas Island": "OCEANIA",
    "Cocos Islands, Keeling Islands": "OCEANIA",
    "Midway Islands": "OCEANIA",

    "Unknown": "UNKNOWN",
}

SUB_SAHARAN_AFRICA_COUNTRIES = {
    "Senegal", "Tanzania, United Republic of", "Sierra Leone", "Botswana", "Nigeria", "South Africa",
    "Benin", "Cape Verde", "Madagascar", "Seychelles", "Ethiopia", "Angola", "Guinea",
    "Mauritania", "Ghana", "South Sudan", "Rwanda", "Sudan", "Kenya", "Uganda", "Cameroon",
    "Congo, The Democratic Republic of the", "Namibia", "Cote D'Ivoire", "Congo", "Zimbabwe",
    "Mauritius", "Mozambique", "Niger", "Malawi", "Zambia", "Mali", "Liberia", "Gabon",
    "Djibouti", "Chad", "Gambia", "Swaziland", "Burkina Faso", "Togo", "Eritrea", "Lesotho",
    "Sao Tome and Principe", "Burundi", "Equatorial Guinea", "Comoros", "Guinea Bissau", "Somalia",
    "Reunion", "Mayotte", "Central African Republic"
}

OTHER_COUNTRIES = {
    "Antarctica", "Bouvet Island", "Do Not Use-Russian Federation", "Do not Use - France",
    "Do not Use -Zaire", "Heard and McDonald Islands", "Holy See, Vatican City State",
    "French Southern Territories", "South Georgia and the South Sandwich Islands"
}


def get_country_category_key(country_name):
    if country_name in COUNTRY_CATEGORY_MAP:
        return COUNTRY_CATEGORY_MAP[country_name]

    if country_name in SUB_SAHARAN_AFRICA_COUNTRIES:
        return "SUB_SAHARAN_AFRICA"

    if country_name in OTHER_COUNTRIES:
        return "OTHER"

    return "OTHER"


@transaction.atomic
def seed_default_countries_for_property(property_obj, actor=None):
    group_cache = {}
    category_cache = {}
    mapping_cache = {}

    unique_category_keys = []
    seen = set()

    for row in DEFAULT_COUNTRY_STRUCTURE:
        category_key = get_country_category_key(row["country_name"])
        if category_key not in seen:
            seen.add(category_key)
            unique_category_keys.append(category_key)

    for index, category_key in enumerate(unique_category_keys, start=1):
        category_config = CATEGORIES[category_key]
        group_config = GROUPS[category_config["group_code"]]

        group, _ = GuestCountryGroup.objects.get_or_create(
            property=property_obj,
            code=group_config["code"],
            defaults={
                "name": group_config["name"],
                "sort_order": index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if group.name != group_config["name"]:
            group.name = group_config["name"]
            changed = True
        if not group.is_active:
            group.is_active = True
            changed = True
        if actor and group.updated_by_id != actor.id:
            group.updated_by = actor
            changed = True
        if changed:
            group.save()

        group_cache[group.code] = group

        category, _ = GuestCountryCategory.objects.get_or_create(
            property=property_obj,
            code=category_config["category_code"],
            defaults={
                "name": category_config["category_name"],
                "group": group,
                "sort_order": index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if category.name != category_config["category_name"]:
            category.name = category_config["category_name"]
            changed = True
        if category.group_id != group.id:
            category.group = group
            changed = True
        if category.sort_order != index:
            category.sort_order = index
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True
        if actor and category.updated_by_id != actor.id:
            category.updated_by = actor
            changed = True
        if changed:
            category.save()

        category_cache[category.code] = category

        mapping, _ = GuestCountryMapping.objects.get_or_create(
            property=property_obj,
            code=category_config["mapping_code"],
            defaults={
                "name": category_config["mapping_name"],
                "category": category,
                "sort_order": index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if mapping.name != category_config["mapping_name"]:
            mapping.name = category_config["mapping_name"]
            changed = True
        if mapping.category_id != category.id:
            mapping.category = category
            changed = True
        if mapping.sort_order != index:
            mapping.sort_order = index
            changed = True
        if not mapping.is_active:
            mapping.is_active = True
            changed = True
        if actor and mapping.updated_by_id != actor.id:
            mapping.updated_by = actor
            changed = True
        if changed:
            mapping.save()

        mapping_cache[mapping.code] = mapping

    for detail_index, row in enumerate(DEFAULT_COUNTRY_STRUCTURE, start=1):
        category_key = get_country_category_key(row["country_name"])
        category_config = CATEGORIES[category_key]
        mapping_obj = mapping_cache[category_config["mapping_code"]]

        detail, _ = GuestCountryDetail.objects.get_or_create(
            property=property_obj,
            code=row["country_code"],
            defaults={
                "name": row["country_name"],
                "mapping": mapping_obj,
                "sort_order": detail_index,
                "is_active": True,
                "is_review_required": False,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if detail.name != row["country_name"]:
            detail.name = row["country_name"]
            changed = True
        if detail.mapping_id != mapping_obj.id:
            detail.mapping = mapping_obj
            changed = True
        if detail.sort_order != detail_index:
            detail.sort_order = detail_index
            changed = True
        if not detail.is_active:
            detail.is_active = True
            changed = True
        if hasattr(detail, "is_review_required") and detail.is_review_required:
            detail.is_review_required = False
            changed = True
        if actor and detail.updated_by_id != actor.id:
            detail.updated_by = actor
            changed = True
        if changed:
            detail.save()