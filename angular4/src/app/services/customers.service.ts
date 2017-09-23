import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';
import { Customers } from 'app/classes/customers';

@Injectable()
export class CustomersService {

    constructor(private authHttp: AuthHttp) { }

    // Api call to get list of customers created by the authenticated user
    getCustomers(): Observable<Customers[]> {
        let url = GetApiurl(`customers/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    // Api call to create new customer
    createCustomer(customers: any, imageFile: any) {
        let url = GetApiurl(`customers/`);

        return new Promise((resolve, reject) => {
            let formData: any = new FormData();
            let xhr = new XMLHttpRequest();
            if (customers.logo && customers.logo != '') {
                formData.append('logo', imageFile);
            }
            formData.append('data', JSON.stringify(customers));
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
    // Api call to get details of the selected Customer
    getCustomer(id: number, queryParams?: Object): Observable<Customers> {
        let url = GetApiurl(`customers/${id}/`);

        if (queryParams) {
            url += `?`;
            for (let property of Object.keys(queryParams)) {
                url += `${property}=${ encodeURIComponent(queryParams[property]) }&`;
            }
        }

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    // Api call to delete the selected customer
    checkIsDeletable(customerId: number): Observable<Customers> {
        let url = GetApiurl(`customers/${customerId}/is_deletable/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    // Api call to delete the selected customer
    deleteCustomer(customerId: number): Observable<Customers> {
        let url = GetApiurl(`customers/${customerId}/`) + '?mode=delete';

        return this.authHttp
            .patch(url, { deleted: 1 })
            .map(Response => Response.json())
            .catch(this.handleError)
    }
    //get customers based on id
    getCustomersList(id: string) {
        let url = GetApiurl(`customers/edit/`);
        return this.authHttp
            .post(url, { 'id': id })
            .toPromise().then(Response => Response.json())
            .catch(this.handleError);

    }

    updateCustomer(formvalues, imageFile) {
        let url = GetApiurl("customers/update/" + formvalues.customerId + "/");
        if (typeof imageFile != 'undefined') {
            return new Promise((resolve, reject) => {
                let formData: any = new FormData();
                let xhr = new XMLHttpRequest();
                if (imageFile != 'undefined') {
                    for (let imagefile of imageFile) {
                        formData.append('imagefile', imagefile);
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

    public checkcompanyName(company_name, id) {
        let url = GetApiurl(`customers/check_companyname/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'company_name': company_name, 'id': id }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    public checkPanNumber(pan_number, id) {
        let url = GetApiurl(`customers/check_pan_number/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'pan_number': pan_number, 'id': id }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }



   searchCustomers(): Observable<Customers[]> {
      let url = GetApiurl('customers/search/');
        return this.authHttp
            .post(url, {search_text: '', search_field: 'company_name'})
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    public authenticateToken(token:string) {
        let url = GetApiurl('token/authenticate/');
        return this.authHttp
            .post(url, JSON.stringify({ 'token': token }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    public createMSCustomer(data:any) {
        let url = GetApiurl('ms/create_customer/');
        return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

     public updateMSCustomerDomain(data:any){
     let url =GetApiurl('customer-cloud-accounts/update_domain_name/')
       return this.authHttp
            .post(url, JSON.stringify(data))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    public customerReportDetails(){
        let url = GetApiurl(`partner-reports/customer-reports/`);
        return this.authHttp
       .get(url)
       .toPromise()
           .then(resp => resp.json())
          .catch(this.handleError);
  }

  public getOrderStatus(){
     let url = GetApiurl(`partner-reports/order-status/`);
        return this.authHttp
       .get(url)
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);

  }
  public getOrders(values){
     let url = GetApiurl(`partner-reports/order-reports/`);
        return this.authHttp
       .post(url, JSON.stringify({'formvalues': values }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);

  }


  public orderDettails(id){
    let url = GetApiurl(`partner-reports/getorder-details/`);
        return this.authHttp
       .post(url,JSON.stringify({'id': id }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);

  }

  public deliverySequence(customer){
     let url = GetApiurl(`customers/get-partner-deliverysequence/`);
        return this.authHttp
       .post(url,JSON.stringify({'id': customer }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);

  }

  /*public soViewOrder(orderNumber){
    let url = GetApiurl(`customers/view-so-order-details/`);
        return this.authHttp
       .post(url,JSON.stringify({'id': orderNumber }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);

  }*/
  public getAmendmentDetails(amendmentId){
     let url = GetApiurl(`subscriptions/get_amendment_details/`);
        return this.authHttp
       .post(url,JSON.stringify({'id': amendmentId }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);
  }


  public MsCustomerOrderStatus(id){
    let url = GetApiurl(`ms-customer/get-ms-customer-order/`);
        return this.authHttp
       .post(url,JSON.stringify({'id': id }))
       .toPromise()
          .then(resp => resp.json())
          .catch(this.handleError);
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
}
