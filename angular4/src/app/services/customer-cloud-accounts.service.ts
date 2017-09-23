import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response, ResponseContentType } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';
import { CustomerCloudAccount, RedConstants } from 'app/classes';

@Injectable()
export class CustomerCloudAccountsService {

    constructor(
        private authHttp: AuthHttp
    ) { }

    // API call to get list of cloud accounts of customer
    listCloudAccounts(queryParams?: Object) {
        let url = GetApiurl('customer-cloud-accounts/');

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to save cloud account details
    createCloudAccount(data: CustomerCloudAccount, queryParams?: Object) {
        let url = GetApiurl(`customer-cloud-accounts/`);

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to get cloud account details
    getCloudAccount(id: number, queryParams?: Object) {
        let url = GetApiurl(`customer-cloud-accounts/${id}/`);

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to update cloud account details
    updateCloudAccount(data: CustomerCloudAccount, queryParams?: Object) {
        let url = GetApiurl(`customer-cloud-accounts/${data['id']}/`);

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .patch(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    updateCloudAccountDetail(data: any) {
        let url = GetApiurl(`customer-cloud-accounts/update-cloud-account/${data['id']}/`);

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    //Validate the MS domain name
    validateDomainName(data: CustomerCloudAccount) {
        let url = GetApiurl('customer-cloud-accounts/validate-domain/');

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // Validate cloud account
    validateCloudAccount(queryParams: Object) {
        let url = GetApiurl('customer-cloud-accounts/validate/');

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to Get Raw password
    getRawPassword(id: number, queryParams: Object) {
        let url = GetApiurl(`customer-cloud-accounts/${id}/get-password-raw/`);

        if (queryParams) { url = this.appendQueryparams(url, queryParams); }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // To update pending request and cloud account
    updatePendingRequest(data: any) {
        let url = GetApiurl(`pending-requests/update-status/${data['id']}/`);

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to Fetch export file content
    exportAccounts(exportType: string, queryParams?: Object) {
        let url = GetApiurl(`customer-cloud-accounts/export/${exportType}/`);

        if (queryParams) url = this.appendQueryparams(url, queryParams);

        return this.authHttp
            .get(url, { responseType: ResponseContentType.Blob })
            .map(Response => {
                debugger
                return {
                    'data': new Blob([Response.blob()], { type: RedConstants.FILE_CONTENT_TYPES[exportType][0] }),
                    'file_ext': `${RedConstants.FILE_CONTENT_TYPES[exportType][1]}`
                }
            })
            .catch(Error => Error);
    }

    // API call to Fetch peding requests export file content
    exportPendingRequests(exportType: string, queryParams?: Object) {
        let url = GetApiurl(`pending-requests/export/${exportType}/`);

        if (queryParams) url = this.appendQueryparams(url, queryParams);

        return this.authHttp
            .get(url, { responseType: ResponseContentType.Blob })
            .map(Response => {
                return {
                    'data': new Blob([Response.blob()], { type: RedConstants.FILE_CONTENT_TYPES[exportType][0] }),
                    'file_ext': `${RedConstants.FILE_CONTENT_TYPES[exportType][1]}`
                }
            })
            .catch(Error => Error);
    }

    searchCloudAccounts(queryParams?: Object): Observable<Array<any>> {
        let url = GetApiurl('customer-cloud-accounts/search/');

        if (queryParams) url = this.appendQueryparams(url, queryParams);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(Err => Err);
    }

    private appendQueryparams(url: string, qParams: Object) {
        url += '?';

        Object.keys(qParams).forEach(property => {
            url += `${encodeURIComponent(property)}=${encodeURIComponent(qParams[property])}&`;
        })

        return url;
    }

    // Error handeling function
    private handleError(error: Response | any) {
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            const err = body.error || JSON.stringify(body);
            errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Observable.throw(errMsg);
    }
    // API call to save cloud account details of ibm customers
    createCloudAccount_IBM_Customer(data: any) {
        let url = GetApiurl(`customer-cloud-accounts/create_ibm_customer/`);
        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }
    // API call to update ibm customers
    updateIBM_CloudAccountDetail(data: any) {
        let url = GetApiurl(`customer-cloud-accounts/update-ibm-cloud-account/${data['id']}/`);

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }
}
