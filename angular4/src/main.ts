import './polyfills.ts';
import 'ts-helpers';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { enableProdMode } from '@angular/core';
import { environment } from './environments/environment';
import { AppModule } from './app/app.module';
import { tokenNotExpired } from 'angular2-jwt';
import { ReflectiveInjector } from '@angular/core';
import {
    Http,
    HttpModule,
    BrowserXhr,
    XHRBackend,
    ResponseOptions,
    RequestOptions,
    ConnectionBackend,
    BaseRequestOptions,
    BaseResponseOptions,
    XSRFStrategy,
    CookieXSRFStrategy,
    Headers,
    Request
} from '@angular/http';

import { GetApiurl } from 'app/parameters';
import 'rxjs/add/operator/map';


if (environment.production) {
    enableProdMode();
}

//.....................Bootstraping App with Config data...................................
// Variable declarations
class FakeXSRFStrategy implements XSRFStrategy {
    public configureRequest(req: Request) { /* */ }
}

var http = ReflectiveInjector.resolveAndCreate([HttpModule,
    Http, BrowserXhr,
    { provide: ConnectionBackend, useClass: XHRBackend },
    { provide: ResponseOptions, useClass: BaseResponseOptions },
    { provide: XSRFStrategy, useFactory: () => new FakeXSRFStrategy() },
    { provide: RequestOptions, useClass: BaseRequestOptions }
]).get(Http);

var data = {
    token: null,
    user: null
};

// Get prefetch datas

// Bootstraps App if not authenticated
if (!localStorage.getItem('id_token') || !tokenNotExpired('id_token')) {
    bootstrap(data);
}
// Fetches config data and Bootstraps App if authenticated
else {
    getUserdata().subscribe(
        response => {
            data['token'] = response['token'];
            data['user'] = response['user'];
            bootstrap(data);
        }
    );
}


// Get user data & new token
function getUserdata() {
    let url = GetApiurl('api-token-refresh/');
    let headers = new Headers();
    headers.append("Content-Type", "application/json");
    let credentials = `{"token":"${localStorage.getItem('id_token')}"}`;

    return http
        .post(url, credentials, { headers: headers })
        .map(Response => Response.json())
        .catch(error => console.log(error));
}

// Bootstraping App
function bootstrap(data) {
    return platformBrowserDynamic([{ provide: 'Config', useValue: data }]).bootstrapModule(AppModule);
}