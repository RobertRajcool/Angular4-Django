import { RouterModule, Routes } from '@angular/router';

import { CustomersComponent } from './customers.component';
import { CustomersListComponent } from './customers-list/customers-list.component';

const CustomerRoutes: Routes = [
    { path: '', redirectTo: 'list', pathMatch: '' },
    {
        path: '',
        component: CustomersComponent,
        children: [
            { path: 'list', component: CustomersListComponent  }
        ]
    }
]

export const CustomersRouting = RouterModule.forChild(CustomerRoutes);
