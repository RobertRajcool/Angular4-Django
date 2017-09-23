// Imports & Providers
import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { Routing, APP_ROUTER_PROVIDERS } from './app.routing';
import { HttpModule, Http, RequestOptions, ResponseOptions } from '@angular/http';
import { JwtHelper, AuthHttp, AuthConfig, AUTH_PROVIDERS } from 'angular2-jwt';
import { AppConfig } from './services/app.config';
import { SharedModule } from './shared/shared.module';
// Declarations
//import { ChartModule } from 'angular2-highcharts';
import * as Raven from 'raven-js';


// Declarations
import { AppComponent } from './app.component';
import { RedGridDirective } from './directives/red-grid.directive';
import { RedingtonErrorService } from './services/redington.error.service'

// Services
import {
     UserService, RolesService, GlobalsService, NotificationsService,
    VendorService, AipDirectoryService, NotificationGroupsService, NotificationActionsService,
    CustomersService, 
    FeedbackService

} from 'app/services';
import { AuthService } from 'app/services/auth/auth.service'
import { HttpInterceptorModule } from 'ng-http-interceptor';
import {HighchartsStatic} from 'angular2-highcharts/dist/HighchartsService';
import {ChartModule} from "angular2-highcharts";
// Google analytics
import { Angulartics2Module, Angulartics2GoogleAnalytics } from 'angulartics2';


export function highchartsFactory() {
  var hc = require('highcharts');
  var hc3d = require('highcharts/highcharts-3d');
  hc3d(hc);
  return hc;
}

@NgModule({
    declarations: [
        AppComponent,
        RedGridDirective,

    ],
    imports: [
        BrowserModule,
        SharedModule,
        HttpModule,
        Routing,
        HttpInterceptorModule,
        ChartModule,
        Angulartics2Module.forRoot([Angulartics2GoogleAnalytics]),
    ],
providers: [
        APP_ROUTER_PROVIDERS,
        RedingtonErrorService,
        AuthService,
        JwtHelper,
        AuthHttp,
        UserService,
        AppConfig,
        RolesService,
        GlobalsService,
        NotificationsService,
        VendorService,
        AipDirectoryService,
        NotificationGroupsService,
        NotificationActionsService,
        CustomersService,
        FeedbackService,

        {
            provide: AuthHttp,
            useFactory: authHttpServiceFactory,
            deps: [Http, RequestOptions]
        },
        {
            provide: HighchartsStatic,
            useFactory: highchartsFactory
        }
        /* { provide: ErrorHandler, useClass: RavenErrorHandler } */
    ],
    
    bootstrap: [AppComponent]


})
export class AppModule { }
// Service factory for angular2-jwt configuration
export function authHttpServiceFactory(http: Http, options: RequestOptions) {
    return new AuthHttp(new AuthConfig({
        headerName: 'Authorization',
        headerPrefix: 'JWT',
        tokenName: 'id_token',
        globalHeaders: [{ 'Content-Type': ' application/json' }],
        noJwtError: true,
        noTokenScheme: true
    }), http, options);
}