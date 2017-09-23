import { Injectable, OnInit } from '@angular/core';
import { Http , Headers, Response } from '@angular/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { AuthHttp } from 'angular2-jwt';


import { GetApiurl } from '../../parameters';

@Injectable()
export class FeedbackService {

  errors: string;

  constructor(private http: Http,private authHttp:AuthHttp) {}

  ngOnInit() {}

  // Error handeling
  private handleError(error : any){
    this.errors = error.json();
    console.log('An error occurred', error);
    return Promise.reject(error.message || error);
  }

  public createFeedback(formvalues, filedata) {
    let url = GetApiurl("partner-feedback/");
    if (typeof filedata != 'undefined') {
      return new Promise((resolve, reject) => {
        let formData: any = new FormData();
        let xhr = new XMLHttpRequest();
        formData.append('attachment', filedata, filedata.name);
        formData.append('reason', formvalues.reason);
        formData.append('name', formvalues.name)
        formData.append('email', formvalues.email)
        formData.append('mobile', formvalues.mobile)
        formData.append('description', formvalues.description);
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
      return this.authHttp
          .post(url, JSON.stringify(formvalues))
          .toPromise()
          .then(Response => Response)
          .catch(this.handleError);
    }

  }
}
