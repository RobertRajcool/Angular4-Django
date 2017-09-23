import {RouterModule, Routes} from '@angular/router';
import {AuthGuardService} from 'app/services/auth/auth-guard.service';
import {CustomersListComponent} from './customers-list/customers-list.component';
import {CustomersComponent} from './customers/customers.component';
import {AddComponent} from "./add/add.component";
import {CustomersEditComponent} from "./customers-edit/customers-edit.component";
import {CustomersViewComponent} from "./customers-view/customers-view.component";

const CustomerRoutes: Routes = [
    {path: '', redirectTo: 'list', pathMatch: 'full'},
    {
        path: '',
        component: CustomersComponent,
        children: [
            {path: 'list', component: CustomersListComponent},
            {path: 'add', component: AddComponent},
            {path: ':id/edit', component: CustomersEditComponent},
            {
                path: ':id',
                children: [
                    {path: '', redirectTo: 'details', pathMatch: 'full'},
                    {
                        path: ':tab',
                        component: CustomersViewComponent,
                        data: {
                            regex: {
                                tab: '(details|contacts|orders|invoices|cloud-accounts)'
                            }
                        },
                        canActivate: [AuthGuardService]
                    }
                ],
                data: {
                    regex: {
                        id: '[0-9]+',
                    }
                },

                canActivate: [AuthGuardService]
            }
        ]
    }
];

export const CustomersRouting = RouterModule.forChild(CustomerRoutes);

