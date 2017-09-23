import { RouterModule, Routes } from '@angular/router';
import { RegisteredCustomersComponent } from './registered-customers.component';
import { InactiveCustomersComponent } from './inactive-customers/inactive-customers.component';
import { ActiveCustomersComponent } from './active-customers/active-customers.component';
import { PartnerActivateComponent } from '../partner/partner-activate/partner-activate.component';

const RegisteredCustomerRoutes: Routes = [
    { path: 'inactive', component: InactiveCustomersComponent },
    { path: 'active', component: ActiveCustomersComponent },
    { path: ':id/activate', component: PartnerActivateComponent },
   // { path: ':id', loadChildren: './partner/partner-view/partner-view.module#PartnerViewModule' }
];

export const RegisteredCustomerRouting = RouterModule.forChild(RegisteredCustomerRoutes);