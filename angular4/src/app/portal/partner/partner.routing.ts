import { RouterModule, Routes } from '@angular/router';
import { PartnerComponent } from './partner.component';
import { PartnerListComponent } from './partner-list/partner-list.component';
import { PartnerViewComponent } from './partner-view/partner-view.component';
import { CustomersViewComponent } from "../customers/customers-view/customers-view.component";
import {CustomersEditComponent} from "../customers/customers-edit/customers-edit.component";
import {AddComponent} from "../customers/add/add.component";

const PartnerRoutes: Routes = [
    { path: '', redirectTo: 'list', pathMatch: 'full'},
    {
        path: '',
        component: PartnerComponent,
        children: [
            { path: 'list', component: PartnerListComponent },
         //   { path: ':id', loadChildren: './partner/partner-view/partner-view.module#PartnerViewModule' },
//{ path: ':id', loadChildren: 'app/portal/partner/partner-view/partner-view.module#PartnerViewModule' },
            { path: ':partnerid/customers/:id', redirectTo: ':partnerid/customers/:id/view/details', pathMatch: 'full'},
            { path: ':partnerid/customers/:id/view/:tab', component: CustomersViewComponent } ,
            { path: ':partner_id/customers/:id/edit', component: CustomersEditComponent },
            { path: ':id/add_customer' , component: AddComponent },
        ]
    }
];

export const PartnerRouting = RouterModule.forChild(PartnerRoutes);

