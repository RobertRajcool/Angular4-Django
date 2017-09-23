import { RouterModule, Routes } from '@angular/router';

import { LandingPageComponent } from './landing-page/landing-page.component';
import { UsersComponent } from './users/users.component';
import { AuthGuardService, AuthRedirectorService } from 'app/services/auth/auth-guard.service';

const AppRoutes: Routes = [
    {
        path: '',
        loadChildren: './landing-page/landing-page.module#LandingPageModule'
    },
    {
        path: 'app',
        loadChildren: './portal/portal.module#PortalModule',
        canActivate: [AuthGuardService]
    },
    {
        path: 'error',
        loadChildren: './error/error.module#ErrorModule'
    },
    {
        path: '**',
        redirectTo: '/error/not-found'
    }
];

export const Routing = RouterModule.forRoot(AppRoutes);
export const APP_ROUTER_PROVIDERS = [AuthGuardService, AuthRedirectorService];
