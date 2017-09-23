import { Injectable, OnInit } from '@angular/core';
import { Http, Headers, Response, ResponseContentType } from '@angular/http';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/toPromise';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from '../../parameters';

import { Partner } from './partner';
import {AuthHttp} from "angular2-jwt/angular2-jwt";
import { RedConstants } from 'app/classes';
@Injectable()

export class PartnerService implements OnInit {

    errors: string;

    constructor(private http: Http, private authHttp: AuthHttp) { }

    ngOnInit() { }

    // Get registerd partner details
    getPartnerDetails(): Observable<Partner[]> {
        let headers = new Headers();
        let url = GetApiurl("partner_details/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http
            .get(url, { headers: headers })
            .map(this.extractPartnerData)
            .catch(this.handleError);
    }

    // Get specific partner details
    getPartnerDetail(id: number): Observable<Partner> {
        let headers = new Headers();
        let url = GetApiurl("partner_details/" + id + "/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .map(this.extractPartner)
            .catch(this.handleError)
    }

    getCurrentPartnerDetail(): Observable<Partner> {
        let headers = new Headers();
        let url = GetApiurl("partner_details/current_partner_details/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .map(this.extractPartner)
            .catch(this.handleError)
    }

    getCurrentPartnerInfo(): Observable<Partner> {
        let url = GetApiurl(`partner_details/current_partner_details/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    updatePartner(p: Partner) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/" + p.id + "/update/");
        let data = JSON.stringify(p);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
                .map(this.extractPartner)
                .catch(this.handleError);
    }

    private extractPartnerData(res: Response) {
        let partnersBody = res.json();
        let partnersArray: Partner[] = [];
        for (let partner of partnersBody) {
            let contacts = [];
            let documents = [];
            if (partner.contacts) {
                var name = email = '';
                var mobile = 0;
                var contact_id : number;
                for (let contact of partner.contacts) {
                    if (contact.type != 'P') {
                        contacts.push(contact);
                    } else {
                        contact_id = contact['id'];
                        name = contact['name'];
                        email = contact['email'];
                        mobile = contact['mobile'];
                    }
                }
            } else {
                var name = '';
                var email = '';
                var mobile = 0;
                var contact_id = -1;
            }
            let partnerVal: Partner = new Partner(
                partner.id,
                partner.company_name,
                partner.status,
                contact_id,
                name,
                email,
                mobile,
                partner.focused_customer,
                partner.partner_type,
                partner.address_1,
                partner.address_2,
                partner.address_3,
                partner.state,
                partner.city,
                partner.pin_code,
                partner.business_type,
                partner.activated_by,
                partner.interested_workload,
                partner.vendor_list,
                contacts,
                documents,
                partner.credits,
                partner.jba_code,
                partner.mpn_id,
                partner.apn_id,
                partner.apn_id_active,
                partner.user_name,
                partner.gst_number
            );
            partnersArray.push(partnerVal);
        }
        return partnersArray;
    }

    private extractPartner(res: Response) {
        let partner = res.json();
        let contacts = [];
        let documents = [];
        var name , email = '';
        var mobile = 0;
        var contact_id = -1;
        if (partner.contacts) {
            for (let contact of partner.contacts) {
                if (contact.type != 'P') {
                    contacts.push(contact);
                } else {
                    contact_id = contact['id'];
                    name = contact['name'];
                    email = contact['email'];
                    mobile = contact['mobile'];
                }
            }
        }
        if(partner.documents){
            for(let doc of partner.documents) {
                documents.push(doc)
            }
        }
        return new Partner(partner.id,
            partner.company_name,
            partner.status,
            contact_id,
            name,
            email,
            mobile,
            partner.focused_customer,
            partner.partner_type,
            partner.address_1,
            partner.address_2,
            partner.address_3,
            partner.state,
            partner.city,
            partner.pin_code,
            partner.business_type,
            partner.activated_by,
            partner.interested_workload,
            partner.vendor_list,
            contacts,
            documents,
            partner.credits,
            partner.jba_code,
            partner.mpn_id,
            partner.apn_id,
            partner.apn_id_active,
            partner.user_name,
            partner.gst_number
        );
    }

    getCustomersByPartner(id){
        let url = GetApiurl(`customers/get_partner_customer/`);
        return this.authHttp
            .post(url,JSON.stringify({'id':id}))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    updateMPNID(data){
        let url = GetApiurl(`partner_details/update-mpn-id/`);
        return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    updateAPNID(data){
        let url = GetApiurl(`partner_details/update-apn-id/`);
        return this.authHttp
            .post(url, JSON.stringify(data))
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

    public getAllPartnerDetails(){
        let url = GetApiurl("partner_details/partner_list/");
        return this.authHttp
            .get(url)
            .toPromise()
            .then(resp => resp.json())
            .catch(this.handleError);
    }

  getActivatedPartnerDetails(){
    let url = GetApiurl(`partner-reports/activatedpartners/`);
    return this.authHttp
      .get(url)
      .toPromise()
      .catch(this.handleError);
  }

  getRegisteredPartnerDetails(){
     let url = GetApiurl(`partner-reports/registeredpartners/`);
    return this.authHttp
      .get(url)
      .toPromise()
      .catch(this.handleError);

  }

  getPartnerCredits(userId) {
        let url = GetApiurl(`partner_details/get_credits/`+userId+`/`);
        return this.authHttp
            .get(url)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
  }

  getActivatedPartnerList():Observable<Partner[]> {
      let url = GetApiurl("partner_details/");
        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
  }

  getApnPartnerDetails(): Observable<Partner[]> {
        let headers = new Headers();
        let url = GetApiurl("partner_details/apn_partner_details/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .map(this.extractPartnerData)
            .catch(this.handleError)
  }

    activateAPNID(data){
        let url = GetApiurl(`partner_details/activate-apn-id/`);
        return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    addPartnerCredits(data) {
        let url = GetApiurl(`partner-aws-credits/add-partner-credit/`);
        return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    getPartnerAwsCredit(id) {
        let url = GetApiurl(`partner-aws-credits/get-aws-credits/`+id+`/`);
        return this.authHttp
            .get(url)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    updatePartnerAwsCredit(value) {
        let url = GetApiurl("partner-aws-credits/update-aws-credits/" + value.creditId + "/");

        let form_values = JSON.stringify(value);
            return this.authHttp
                .post(url, { 'value': form_values })
                .toPromise()
                .then(data => data.json())
                .catch(this.handleError)
    }

    getAwsCustomerDetails() {
        let headers = new Headers();
        let url = GetApiurl("partner-aws-credits/get-aws-customers");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    getLinkedCustomer(id) {
        let url = GetApiurl(`partner-aws-credits/get-aws-linked-customer/${id}/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    checkCouponCodeExist(coupon_code) {
        let url = GetApiurl(`partner-aws-credits/check-coupon-code/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'coupon_code': coupon_code }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);

    }
    
    //service to call rejected partner reason
    partnerRejectView(id){
       let url = GetApiurl(`rejected-partner-details/view-reason/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'partner_id': id }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);

    }

    deletePartner(id){
       let url = GetApiurl(`rejected-partner-details/delete-partner/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'partner_id': id }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);

    }

    // API call to fetch export file content
    export_aws_active_partners() {
        let url = GetApiurl(`partner_details/download_active_aws_partner_list/`);
        return this.authHttp
            .get(url, { responseType: ResponseContentType.Blob })
            .map(Response => {
                return {
                    'data': new Blob([Response.blob()], { type: RedConstants.FILE_CONTENT_TYPES['csv'][0] })
                }
            })
            .catch(Error => Error);
    }

    // Partner rating & feedback service
    partnerRatingService(feedback) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/store_partner_rating_and_feedback/");
        let data = JSON.stringify(feedback);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Function to check partner updated their feedback or not
    checkFeedbackUpdatedService() {
        var headers = new Headers();
        let url = GetApiurl("partner_details/is_partner_updated_feedback/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Get list of feedback & ratings updated by partner
    getRatings() {
        var headers = new Headers();
        let url = GetApiurl("partner_details/get_ratings/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Get count of ratings
    getRatingsCount() {
        var headers = new Headers();
        let url = GetApiurl("partner_details/get_ratings_count/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Send registration link to customer
    sendLinkService(customer) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/send-registration-link/");
        let data = JSON.stringify(customer);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Partner Customer Linking service (ORC Linking)
    customerLinkingService(partner: any, customer: number) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/"+customer+"/customer-linking/");
        let data = JSON.stringify(partner);
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.post(url, data, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    // Partner customer Delinking service
    customerDelinkingService(customer: number) {
        var headers = new Headers();
        let url = GetApiurl("partner_details/"+customer+"/customer-delinking/");
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')

        return this.http.get(url, { headers: headers })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    getSelectedPartners(ids) {
        let url = GetApiurl(`partner_details/selected_partner/?partner_ids=${ids}`);
        return this.authHttp
            .get(url)
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

}
