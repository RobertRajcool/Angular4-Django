import { Injectable } from '@angular/core';
import { Http, Headers, Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { AuthHttp } from 'angular2-jwt';

import 'rxjs/add/operator/toPromise';

import { GetApiurl } from '../../parameters';
import { User } from './../../users/user';
import { PartnerRegistration_1, PartnerRegistration_2, PartnerRegistration_3 } from './partner-registration';

@Injectable()

export class PartnerService {

    errors: string;
    
    constructor(private http: Http,private authHttp: AuthHttp) {}

    getStates() {
        let headers = new Headers();
        let url = GetApiurl("pin_code/states/"); 
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        
        return this.http
                .get(url, { headers: headers})
                .toPromise()
                .then(Response => Response.json())
                .catch(this.handleError);             
    }

    // Partner registration first step process without authentication 
    partnerRegistration(partner_detail: PartnerRegistration_1) {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let url = GetApiurl("initial_partner_details/partner-registration-step-one/"); 

        return this.http
                .post(url, JSON.stringify(partner_detail), { headers: headers})
                .toPromise()
                .then(Response => Response.json())
                .catch(this.handleError);
    }

    // Partner registration first step process - updation
    partnerRegistrationUpdate(partner_detail: PartnerRegistration_1) {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let url = GetApiurl("initial_partner_details/"+partner_detail.id+"/partner-registration-step-one/"); 

        return this.http
                .post(url, JSON.stringify(partner_detail), { headers: headers})
                .toPromise()
                .then(Response => Response.json())
                .catch(this.handleError);
    }

    // Partner registration second step process - updation
    partnerRegistration_2(partner_detail: PartnerRegistration_2) {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let url = GetApiurl("initial_partner_details/"+partner_detail.id+"/partner-registration-step-two/"); 

        let res = new Promise((resolve, reject) => {
            let formData: any = new FormData();
            let xhr = new XMLHttpRequest();
            partner_detail.documents.forEach(element => {
                formData.append(element.type, element.file)
            });
            formData.append('partner_detail', JSON.stringify(partner_detail));
            xhr.open('POST', url, true);
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.send(formData);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == XMLHttpRequest.DONE) {
                    let respone = JSON.parse(xhr.responseText);
                    console.log(respone);
                }
            }
        })

    }

    // Partner registration final step process - updation
    PartnerRegistration_3(partner_detail: PartnerRegistration_3) {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let url = GetApiurl("initial_partner_details/"+partner_detail.id+"/partner-registration-step-three/"); 

        return this.http
                .post(url, JSON.stringify(partner_detail), { headers: headers})
                .toPromise()
                .then(Response => Response.json())
                .catch(this.handleError);
    }

    // Get registered partner details
    getRegisteredPartner(key: string) {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let url = GetApiurl("initial_partner_details/"+key+"/registered_partner/");
        
        return this.http
                .get(url, { headers: headers})
                .toPromise()
                .then(Response => Response.json())
                .catch(this.handleError);
    }

    // Error handeling
    handleError(error : any){
        this.errors = error.json();
        console.log('An error occurred', error);
        return Promise.reject(error.message || error);
    }

    public getTermsAndConditionsContent(url) {
        return this.authHttp
            .get(url)
            .toPromise()
            .then(resp => resp.text())
            .catch(this.handleError);
    }

    // Check customer registration token expired
    checkTokenExpired(token, k) {
        let url = GetApiurl("initial_partner_details/check-token-expired/"+token+"/"+k+"/");
        let headers = new Headers({ 'Content-Type': 'application/json' });

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

}