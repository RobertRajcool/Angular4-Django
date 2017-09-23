import { Inject, Injectable, forwardRef, OnDestroy } from '@angular/core';
import { tokenNotExpired, JwtHelper } from 'angular2-jwt';
import { Router } from '@angular/router';
import { Http, Headers, Response } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { GetApiurl } from 'app/parameters';
import { User, RedConstants } from 'app/classes';
import { GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { Angulartics2 } from 'angulartics2';

@Injectable()
export class AuthService {
    user: User;
    userPermissions: Array<string> = [];
    userSubscription: Subscription;
    userPermissionsSubscription: Subscription;

    constructor(
        private http: Http,
        private router: Router,
        private jwthelper: JwtHelper,
        @Inject(forwardRef(() => GlobalsService)) private globals,
        private angulartics2: Angulartics2
    ) {
        this.userSubscription = this.globals.user$.subscribe(u => this.user = u);
        this.userPermissionsSubscription = this.globals.userPermissions$.subscribe(ps => this.userPermissions = ps);
    }

    // Checks is authenticated
    public authenticated() {
        // Check if there's an unexpired JWT
        // This searches for an item in localStorage with key == 'id_token'

        if (localStorage.getItem("id_token")) return tokenNotExpired('id_token');
        else return false;

    }

    // Checks is user has roles 
    public permitted(roles: Array<string>) {

        if (!(this.user instanceof Object) || !(this.userPermissions instanceof Array)) return false;
        else {
            if (intersect(this.userPermissions, roles).length == roles.length) return true;
            else return false;
        }


        function intersect(a, b) {
            var t;
            if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
            return a.filter(e => b.indexOf(e) > -1).filter((e, i, c) => c.indexOf(e) === i);// extra step to remove duplicates
        }
    }

    // Login action
    public login(username: string, password: string) {

        let url = GetApiurl("api-token-auth/");
        let headers = new Headers;
        headers.append("Content-Type", "application/json");
        let credentials = `{"username":"${username}","password":"${password}"}`;

        return this.http
            .post(url, credentials, { headers: headers })
            .map(Response => this.handleResponse(Response))
            .catch(this.handleError);

    }

    // Refreshing token
    public refreshToken(token: string) {
        console.log("Token expired refreshing : ", new Date());

        let url = GetApiurl("api-token-refresh/");
        let headers = new Headers;
        headers.append("Content-Type", "application/json");
        let credentials = `{"token":"${token}"}`;

        return this.http
            .post(url, credentials, { headers: headers })
            .map(Response => this.handleResponse(Response))
            .catch(this.handleError);
    }

    // Logout action
    public logout() {
        if (localStorage.getItem("id_token")) {
            localStorage.removeItem("id_token");
            this.globals.setUser(null);
        }

        localStorage.clear();

        // Recording for google analytics
        this.angulartics2.eventTrack.next({
            action: 'Logout',
            properties: {
                category: 'Authentication'
            }
        });
        this.router.navigate(['/auth/login']);
    }

    // API call to validate user details and generate password reset link
    generatePasswordResetLink(username: string, email: string) {
        let url = GetApiurl(`api-password-reset/`);
        let data = {
            'username': username,
            'email': email,
            'base_path': window.location.origin + this.router.createUrlTree(['/auth/password/reset/confirm/']).toString()
        }

        let headers = new Headers();
        headers.append('Content-Type', 'application/json');

        return this.http
            .post(url, JSON.stringify(data), { 'headers': headers })
            .map(Response => Response.json())
            .catch(Error => {
                return Observable.throw(Error.json());
            });

    }

    // API call to verify password reset key
    verifyPasswordResetToken(token: string) {
        let url = GetApiurl(`api-password-reset-verify/`);
        let data = {
            'token': token,
        }

        let headers = new Headers();
        headers.append('Content-Type', 'application/json');

        return this.http
            .post(url, JSON.stringify(data), { 'headers': headers })
            .map(Response => Response.json())
            .catch(Error => {
                return Observable.throw(Error.json());
            });
    }

    // API call to reset password
    resetPassword(token: string, password: string) {
        let url = GetApiurl(`api-password-reset-confirm/`);
        let data = {
            'password': password,
        }

        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        headers.append('Authorization', `JWT ${token}`);

        return this.http
            .post(url, JSON.stringify(data), { 'headers': headers })
            .map(Response => Response.json())
            .catch(Error => {
                return Observable.throw(Error.json());
            });

    }

    // Handle response and schedule token refresh
    public handleResponse(response: Response) {

        response = response.json();
        localStorage.setItem('id_token', response['token']);
        this.globals.setUser(response['user']);

        let now = new Date().valueOf();
        let tokenExp = this.jwthelper.decodeToken(response['token']).exp;
        let exp = new Date(0);
        exp.setUTCSeconds(tokenExp);
        let delay = exp.valueOf() - now;

        let timer = Observable.timer(delay - 60);

        timer.subscribe(() => {
            this.refreshToken(response['token']).subscribe(
                Response => Response,
                Error => this.router.navigate(['/login'])
            );
        });

        return response;

    }

    // Redirecting to respective homepages for the recpective users
    redirectToHome(){
        /* switch(RedConstants.IsvUserTypes.indexOf(this.user.user_type) >= 0){
                
                default: this.router.navigate(['/app']); break;
                case false: this.router.navigate(['/app']); break;
                case true: this.router.navigate(['/isv']); break;
            } */
            this.router.navigate(['/app']); 
    }

    // Handeling error
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

    ngOnDestroy() {
        this.userSubscription.unsubscribe();
        this.userPermissionsSubscription.unsubscribe();
    }

}
