import { Injectable } from '@angular/core';
import {AuthHttp} from "angular2-jwt";
import {Http} from "@angular/http";
import {GetApiurl} from "app/parameters";

@Injectable()
export class ChangePasswordService {
  private errors
  constructor(private http: Http,private authHttp:AuthHttp) { }


  changePassword(formvalues){
    let url = GetApiurl("users/change-password/");
    return this.authHttp
        .post(url,JSON.stringify(formvalues))
        .map(res =>res.json())
  }
// Error handeling
  private handleError(error : any){
    this.errors = error.json();
    console.log('An error occurred', error);
    return Promise.reject(error.message || error);
  }
}
