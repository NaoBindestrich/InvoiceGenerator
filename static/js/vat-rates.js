/**
 * EU VAT Rates Database
 * Contains standard and reduced VAT rates for all EU countries
 * Based on official EU VAT rates (updated 2026)
 */

const VAT_RATES = {
    // Format: Country Code => { name, standard, reduced }
    'AT': { name: 'Austria', standard: 0.20, reduced: 0.10 },
    'BE': { name: 'Belgium', standard: 0.21, reduced: 0.06 },
    'BG': { name: 'Bulgaria', standard: 0.20, reduced: 0.09 },
    'HR': { name: 'Croatia', standard: 0.25, reduced: 0.05 },
    'CY': { name: 'Cyprus', standard: 0.19, reduced: 0.05 },
    'CZ': { name: 'Czech Republic', standard: 0.21, reduced: 0.12 },
    'DK': { name: 'Denmark', standard: 0.25, reduced: 0.25 }, // No reduced rate
    'EE': { name: 'Estonia', standard: 0.24, reduced: 0.09 },
    'FI': { name: 'Finland', standard: 0.255, reduced: 0.10 },
    'FR': { name: 'France', standard: 0.20, reduced: 0.055 },
    'DE': { name: 'Germany', standard: 0.19, reduced: 0.07 },
    'GR': { name: 'Greece', standard: 0.24, reduced: 0.06 },
    'HU': { name: 'Hungary', standard: 0.27, reduced: 0.05 },
    'IE': { name: 'Ireland', standard: 0.23, reduced: 0.048 },
    'IT': { name: 'Italy', standard: 0.22, reduced: 0.10 },
    'LV': { name: 'Latvia', standard: 0.21, reduced: 0.05 },
    'LT': { name: 'Lithuania', standard: 0.21, reduced: 0.05 },
    'LU': { name: 'Luxembourg', standard: 0.17, reduced: 0.03 },
    'MT': { name: 'Malta', standard: 0.18, reduced: 0.05 },
    'NL': { name: 'Netherlands', standard: 0.21, reduced: 0.09 },
    'PL': { name: 'Poland', standard: 0.23, reduced: 0.05 },
    'PT': { name: 'Portugal', standard: 0.23, reduced: 0.06 },
    'RO': { name: 'Romania', standard: 0.21, reduced: 0.11 },
    'SK': { name: 'Slovakia', standard: 0.23, reduced: 0.05 },
    'SI': { name: 'Slovenia', standard: 0.22, reduced: 0.05 },
    'ES': { name: 'Spain', standard: 0.21, reduced: 0.10 },
    'SE': { name: 'Sweden', standard: 0.25, reduced: 0.06 },
    // Non-EU European countries
    'CH': { name: 'Switzerland', standard: 0.077, reduced: 0.025 },
    'GB': { name: 'United Kingdom', standard: 0.20, reduced: 0.05 },
    'NO': { name: 'Norway', standard: 0.25, reduced: 0.12 }
};

/**
 * Get VAT rate for a country
 * @param {string} countryCode - Two-letter country code
 * @param {string} rateType - 'standard' or 'reduced'
 * @returns {number} VAT rate as decimal (e.g., 0.19 for 19%)
 */
function getVATRate(countryCode, rateType = 'standard') {
    const country = VAT_RATES[countryCode.toUpperCase()];
    if (!country) {
        console.warn(`VAT rate not found for country: ${countryCode}, using 19%`);
        return 0.19; // Default fallback
    }
    return rateType === 'reduced' ? country.reduced : country.standard;
}

/**
 * Get VAT rate as percentage
 * @param {string} countryCode - Two-letter country code
 * @param {string} rateType - 'standard' or 'reduced'
 * @returns {number} VAT rate as percentage (e.g., 19 for 19%)
 */
function getVATRatePercentage(countryCode, rateType = 'standard') {
    return Math.round(getVATRate(countryCode, rateType) * 100);
}

/**
 * Get country name from code
 * @param {string} countryCode - Two-letter country code
 * @returns {string} Country name
 */
function getCountryName(countryCode) {
    const country = VAT_RATES[countryCode.toUpperCase()];
    return country ? country.name : countryCode;
}

/**
 * Check if country has different reduced rate
 * @param {string} countryCode - Two-letter country code
 * @returns {boolean} True if reduced rate differs from standard
 */
function hasReducedRate(countryCode) {
    const country = VAT_RATES[countryCode.toUpperCase()];
    if (!country) return false;
    return country.reduced !== country.standard;
}
