import { RouterModule, Routes } from '@angular/router';

import { PartnerViewComponent } from './partner-view.component';
import { PartnerDetailsComponent } from './partner-details/partner-details.component';
import { CustomersListComponent } from './../customers/customers-list/customers-list.component';
import { OrdersComponent } from './../orders/orders.component';
//import { InvoicesListComponent } from './../../../portal/invoices/invoices-list/invoices-list.component'

const PartnerViewRoutes: Routes = [
    { path: '', redirectTo: 'details', pathMatch: 'full' },
    {
        path: '',
        component: PartnerViewComponent,
        children: [
            { path: 'details', component: PartnerDetailsComponent },
            { path: 'customers', component: CustomersListComponent },
            { path: 'orders', component: OrdersComponent },
             ]
    }
]

export const PartnerViewRouting = RouterModule.forChild(PartnerViewRoutes);
