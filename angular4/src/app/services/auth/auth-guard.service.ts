import { Injectable, Inject } from '@angular/core';
import {
    CanActivate, Router,
    ActivatedRouteSnapshot,
    RouterStateSnapshot,
    NavigationExtras
} from '@angular/router';

import { AuthService } from 'app/services/auth/auth.service';
import { User } from 'app/classes';

@Injectable()
export class AuthGuardService implements CanActivate {

    constructor(private router: Router, private authService: AuthService) { }

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {

        // Validating url params
        if (Object.keys(route.data).indexOf('regex') >= 0) {
            let params = route.params;
            for (let param of Object.keys(params)) {
                if (Object.keys(route.data['regex']).indexOf(param) >= 0) {
                    let regex_str = `^${route.data['regex'][param]}$`;
                    let exp = new RegExp(regex_str, 'g');

                    if (!exp.test(params[param])) {
                        this.router.navigate(['/error/not-found']);
                        return false;
                    }
                }
            }
        }

        // Checks is user authenticated
        if (!this.authService.authenticated()) {
            this.router.navigate(['/auth/login']);
            return false;
        }
        // Checks permission if roles provided
        if (Object.keys(route.data).indexOf('roles') == -1)
            return true;
        else {
            if (this.authService.permitted(route.data['roles'])) return true;
            else {
                this.router.navigate(['/error/denied']);
                return false;
            }
        }
    }
}

//###############################################################################################################

// Authenticated redirecting services, it helps to redirect directly to homepage if the user is authenticated already
@Injectable()
export class AuthRedirectorService implements CanActivate {
    userDetails: User;

    constructor(
        private router: Router,
        private authService: AuthService
    ) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        // Redirecting Authenticated user
        if (this.authService.authenticated()) {

            this.authService.redirectToHome();
            return false;

        } else return true;
    }
}