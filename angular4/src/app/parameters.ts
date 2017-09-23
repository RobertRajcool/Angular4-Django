// Configurations
export const baseURL = "http://127.0.0.1:8000/";
const validImageTypes = ['image/png', 'image/jpg', 'image/gif','image/jpeg'];
const validvendoraggrementFileTypes = ['application/pdf', 'text/plain','text/html'];

const validTermsConditionsFileTypes = ['text/plain','text/html'];
const validRedingtonTermsConditionsFileTypes = ['text/plain','text/html'];

const validImageSize=1048576;
const validvendoraggrementFile=1048576;
const validTermsConditionsFile=1048576;
const validRedingtonTermsConditionsFile=1048576;
export const cloudVendors = [
    ['AWS', 'AWS'],
    ['MS', 'AZURE'],
    ['MS', 'Microsoft']
    ];

export const currencySymbols = {
    'INR': '₹',
    'USD': '$'
}


// get ApiURL
export function GetApiurl(path: string) {
    return baseURL + path;
}
//get valid vendor aggrement file
export function GetAgreementFileTypes(){
    return {'validfileType':validvendoraggrementFileTypes,'validfileSize':validvendoraggrementFile}
}
//get valid vendor image file types
export function GetValidimageTypes(){
    return {'validType':validImageTypes,'validSize':validImageSize}
}

export function GetTermsconditionsFileTypes(){
  return {'validfilesType':validTermsConditionsFileTypes,'validfilesSize':validTermsConditionsFile}
}
export function GetRedingtonTermsconditionsFileTypes(){
  return {'validfilesType':validRedingtonTermsConditionsFileTypes,'validfilesSize':validRedingtonTermsConditionsFile}
}

export const monthNames: Array<string> = [ "January", "February", "March", "April", "May", "June",
"July", "August", "September", "October", "November", "December" ];
