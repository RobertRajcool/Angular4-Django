import { Injectable } from '@angular/core';
import { Http, Headers } from "@angular/http";
import { GetApiurl } from 'app/parameters';
import { AuthHttp } from 'angular2-jwt';
import { Observable } from "rxjs/Rx";
import { RolesList } from 'app/classes/roles';
import { Roles } from 'app/classes';
import { Response } from '@angular/http';
@Injectable()
export class VendorService {
    errors: string;

    constructor(private http: Http, private authHttp: AuthHttp) { }

    ngOnInit() { }

    // Get list  vendor
    public getVendors() {
        let apiurl = GetApiurl("vendor-details/")
        return this.authHttp
            .get(apiurl)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }
    // Get all vendor that associated with the users
    public getUsersVendors() {
        let apiurl = GetApiurl("vendor-details/get_vendor_details/")
        return this.authHttp
            .get(apiurl)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }
    public checkvendorname(vendor_name) {
        let url = GetApiurl(`vendor-details/check-vendorname/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'vendorname': vendor_name }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }
    //getting vendordetails By vendorid
    public getvendor(id: number) {
        let url = GetApiurl(`vendor-details/getvendor-list/`);
        let data = { 'vendor_id': id };
        return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // API call to fetch vendor details by queryParams
    fetchVendor(queryParams: Object) {
        let url = GetApiurl(`vendor-details/fetch-vendor/`);

        if (queryParams) {
            url += '?';
            for (let property of Object.keys(queryParams)) {
                url += `${property}=${ encodeURIComponent(queryParams[property]) }&`;
            }
        }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);

    }

    //delete vendor
    public delete(id: number) {
        let url = GetApiurl(`vendor-details/delete-vendor/`);
        let data = { 'vendor_id': id };
        return this.authHttp
            .post(url, { 'vendor_id': id })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    public getRolesList(): Observable<RolesList[]> {
        let url = GetApiurl(`roles/`);

        return this.authHttp
            .get(url)
            .map(this.extractRoles)
            .catch(this.handleError)
    }

    private extractRoles(res: Response) {
        let rolesBody = res.json();
        let rolesArray: RolesList[] = [];
        for (let rBody of rolesBody) {
            let roles: RolesList = new RolesList(
                rBody.id,
                rBody.alias);
            rolesArray.push(roles);
        }
        return rolesArray;
    }
    //add vendor Details
    public addVendor(formvalues, aggrementfiledetails, logofiledetails, conditionsFileDetail,redingtonFileDetail) {
        return new Promise((resolve, reject) => {
            let formData: any = new FormData();
            let xhr = new XMLHttpRequest();
            formData.append('aggrementfile', aggrementfiledetails);
            formData.append('imagefile', logofiledetails);
            formData.append('conditionalfile', conditionsFileDetail);
            formData.append('redingtonfile',redingtonFileDetail)
            /*for (let aggrementfile of aggrementfiledetails) {
                formData.append('aggrementfile', aggrementfile);
            }
            for (let imagefile of logofiledetails) {
                formData.append('imagefile', imagefile);
            }
            for (let conditionfile of conditionsFileDetail) {
                formData.append('conditionalfile', conditionfile);
            }
            for (let redingtonfile of redingtonFileDetail){
              formData.append('redingtonfile',redingtonfile)
            }*/
            let url = GetApiurl("vendor-details/");
            formData.append('formvalues', JSON.stringify(formvalues));
            xhr.open('POST', url, true);
            xhr.setRequestHeader('Authorization', 'JWT ' + localStorage.getItem('id_token'));
            xhr.send(formData);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == XMLHttpRequest.DONE) {
                    resolve(JSON.parse(xhr.responseText));
                }
            }
        });
    }
    //update vendor Details
    public updateVendordetails(formvalues, agreementfileDetail, imagefileDetails, conditionsFileDetail,redingtonFileDetail) {
        let url = GetApiurl("vendor-details/update/" + formvalues.vendorid + "/");
        if (typeof imagefileDetails != 'undefined' || typeof agreementfileDetail != 'undefined' || typeof conditionsFileDetail != 'undefined' || typeof redingtonFileDetail != 'undefined' ) {
            return new Promise((resolve, reject) => {
                let formData: any = new FormData();
                let xhr = new XMLHttpRequest();
                if (agreementfileDetail != undefined) {
                    for (let agreementfile of agreementfileDetail) {
                        formData.append('aggrementfile', agreementfile);
                    }
                }
                if (imagefileDetails != undefined) {
                    for (let imagefile of imagefileDetails) {
                        formData.append('imagefile', imagefile);
                    }
                }
                if (conditionsFileDetail != undefined) {
                    for (let conditionalfile of conditionsFileDetail) {
                        formData.append('termsandconditionfile', conditionalfile);
                    }
                }
                if(redingtonFileDetail != undefined) {
                    for (let redingtonfile of redingtonFileDetail) {
                        formData.append('redingtonfile', redingtonfile);
                    }
                }
                formData.append('formvalues', JSON.stringify(formvalues));
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Authorization', 'JWT ' + localStorage.getItem('id_token'));
                xhr.send(formData);
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == XMLHttpRequest.DONE) {
                        resolve(JSON.parse(xhr.responseText));
                    }
                }
            });
        }
        else {
            let form_values = JSON.stringify(formvalues);
            return this.authHttp
                .post(url, { 'formvalues': form_values })
                .toPromise()
                .then(data => data.json())
                .catch(this.handleError)
        }
    }

    /* //getting vendordetails
      public getvendorDetails(id: number) {
           let url = GetApiurl(`vendor-details/viewVendor-list/`);
          let data = { 'vendor_id': id };
          return this.authHttp
              .post(url, { 'vendor_id': id })
              .toPromise()
              .then(Response => Response.json())
              .catch(this.handleError);
      }*/

    //check vendor while updating
    public checkVendorName(vendor_name, id) {
        let url = GetApiurl(`vendor-details/check-vendor/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'vendorname': vendor_name, 'id': id }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Error handeling
    handleError(error: any) {
        return Promise.reject(error.message || error);
    }

    //getting vendordetails By vendorid
    public canVendorDelete(id: number) {
        let url = GetApiurl(`vendor-details/can-vendor-delete/${id}/`);
        let data = { 'vendor_id': id };
        return this.authHttp
            .get(url)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    public getTrialRequestDetails(id:number){
      let url = GetApiurl("portal_trialaccounts/" + id + "/");
        return this.authHttp
            .get(url)
            .toPromise()
            .then(resp => resp.json())
            .catch(this.handleError);
    }

   public approveTrialStatus(status_value){
      let url = GetApiurl("portal_trialaccounts/approve-trial-request/");
        return this.authHttp
            .post(url,status_value)
            .toPromise()
            .then(resp => resp.json())
            .catch(this.handleError);
    }


}
