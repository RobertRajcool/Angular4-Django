import { Injectable } from '@angular/core';
import { Http, Headers, Response } from '@angular/http';
import { AuthHttp } from 'angular2-jwt';
import { Router } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from '../parameters';

import { User, UserType } from './user';

@Injectable()
export class UserService {

    constructor(private http: Http, private authHttp: AuthHttp, private router: Router) { }

    getUsers(): Observable<User[]> {
        var headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        return this.http.get(GetApiurl('users/'), { headers: headers })
            .map(this.extractData)
            .catch(this.handleError);
    }

    getUser(id: number): Observable<User> {
        var headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        return this.http.get(GetApiurl('users/') + id + '/', { headers: headers })
            .map(this.extractUser)
            .catch(this.handleError);
    }

    addUser(u: User): Observable<User> {
        var headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')
        return this.http.post(GetApiurl('users/'), this.stringify(u), { headers: headers })
            .map(this.extractUser)
            .catch(this.handleError);
    }

    updateUser(u: User): Observable<User> {
        var headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')
        return this.http.put(GetApiurl('users/') + u.id + '/', this.stringify(u), { headers: headers })
            .map(this.extractUser)
            .catch(this.handleError);
    }

    deleteUser(id: number) {
        var headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        headers.append('Content-Type', 'application/json')
        return this.http.get(GetApiurl('users/delete/') + id + '/', { headers: headers })
            .map(this.extractData)
            .catch(this.handleError);
    }

    getUserTypeList(): Observable<UserType> {
        let url = GetApiurl(`users/user_type/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError)
    }

    checkNameExist(username) {
        let url = GetApiurl(`users/check-username/`);
        return this.authHttp
            .post(url, JSON.stringify({ 'username': username }))
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    getUserPartnerDetails(id) {
        let url = GetApiurl('users/user-partner-details/'+id+'/');
        return this.authHttp
            .get(url).toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

     getUserIsvDetails(id) {
        let url = GetApiurl('isv/vendors/user-isv-details/'+id+'/');
        return this.authHttp
            .get(url).toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);
    }

    private extractUser(res: Response) {
        let jsonResponse = res.json();
        return new User(jsonResponse.id,
            jsonResponse.username,
            jsonResponse.email,
            jsonResponse.user_type,
            jsonResponse.first_name,
            jsonResponse.last_name,
            jsonResponse.address,
            jsonResponse.description,
            jsonResponse.user_location,
            jsonResponse.vendor_category,
            jsonResponse.role_id,
            jsonResponse.permissions
        );
    }

    private stringify(u: User): string {
        return JSON.stringify({
            "username": u.username,
            "first_name": u.firstName,
            "last_name": u.lastName,
            "email": u.email,
            "address": u.address,
            "description": u.description,
            "user_type": u.user_type,
            "user_location": u.location,
            "role_id": u.roleId,
            "vendor_category": u.vendorCategory,
            "region_name": u.region
        });
    }

    private extractData(res: Response) {
        let usersBody = res.json();
        let usersArray: User[] = [];
        for (let uBody of usersBody) {
            let user: User = new User(
                uBody.id,
                uBody.username,
                uBody.email,
                uBody.user_type,
                uBody.first_name,
                uBody.last_name,
                uBody.address,
                uBody.description,
                uBody.user_location,
                uBody.vendor_category,
                uBody.role_id);
            usersArray.push(user);
        }
        return usersArray;
    }

    public getusers(id: any) {
        let url = GetApiurl(`users/user-view/`);
        return this.authHttp
            .post(url, { 'id': id })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);

    }

    getEmployeeDetails(EmployeeCode:any){
       let url = GetApiurl(`users/user-getEmployeeDetails/`);
        return this.authHttp
            .post(url,{ 'employe_id':EmployeeCode })
            .toPromise()
            .then(Response => Response.json())
            .catch(this.handleError);

    }

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
