import { Injectable, OnInit } from '@angular/core';
import { Http, Headers, Response } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/toPromise';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from '../../parameters';
import { Activation, Rejection } from './../partner/partner';

@Injectable()

export class InactivePartnerService implements OnInit {

    errors: string;
    
    constructor(private http: Http) {}

    ngOnInit() {}

    // Get inactive partner details
    getInactivePartners() {
        let headers = new Headers();
        let url = GetApiurl("initial_partner_details/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Get particular inactive partner details
    getInactivePartner(id: number) { 
        let headers = new Headers();
        let url = GetApiurl("initial_partner_details/" + id + "/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Check partner user name exists in database
    checkUserName(p: Activation) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/" + p.preferred_user_name + "/check/");
        let data = JSON.stringify(p);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Check dealer code exists in database
    checkDealerCode(p: Activation) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/" + p.jba_code + "/check_dealer_code/");
        let data = JSON.stringify(p);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Partner activation function
    partnerActivation(p: Activation) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/" + p.id + "/activate/");
        let data = JSON.stringify(p);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }
    
    // Partner rejection function
    partnerRejection(p: Rejection) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/" + p.id + "/reject/");
        let data = JSON.stringify(p);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Error handeling
    handleError(error: any) {
        this.errors = error.json();
        console.log('An error occurred', error);
        return Promise.reject(error.message || error);
    }
}