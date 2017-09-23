import { RouterModule, Routes } from '@angular/router';

import { InactivePartnerComponent } from './inactive-partner.component';
import { InactivePartnerListComponent} from './inactive-partner-list/inactive-partner-list.component';
import { PartnerActivateComponent } from '../partner/partner-activate/partner-activate.component';

const InactivePartnerRoutes: Routes = [
    { path: '', redirectTo: 'list', pathMatch: 'full'},
    {
        path: '',
        component: InactivePartnerComponent,
        children: [
            { path: 'list', component: InactivePartnerListComponent },
            { path: ':id/activate', component: PartnerActivateComponent }
        ]
    }
];

export const InactivePartnerRouting = RouterModule.forChild(InactivePartnerRoutes);
