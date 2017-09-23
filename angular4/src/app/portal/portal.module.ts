// Modules
import { NgModule } from '@angular/core';
import { LiveTileModule } from '../components/tile/tile.module';

// Services
import { VendorService,  CustomerCloudAccountsService, PartnerService,InactivePartnerService } from 'app/services';
import {ChangePasswordService} from "./change-password/change-password.service";

// Components
import { PortalComponent } from './portal.component';
import { PortalRouting } from './portal.routing';
import { DashboardComponent } from './dashboard/dashboard.component';
import { Sidebar } from './sidebar/sidebar.component';
import { Navbar } from './navbar/navbar.component';
import { ProfileComponent } from './profile/profile.component';
import { NotificationGroupsComponent } from './notification-groups/notification-groups.component';
import { NotificationActionsComponent } from './notification-actions/notification-actions.component';
import { PartnerFeedbackComponent } from './partner-feedback/partner-feedback.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { HelpPopupComponent } from './navbar/help-popup/help-popup.component';
import { RejectedPartnersComponent } from './rejected-partners/rejected-partners.component';
import { PartnerRatingsListComponent } from './partner-ratings-list/partner-ratings-list.component';
import { CustomerRegistrationLinkComponent } from './customer-registration-link/customer-registration-link.component';
import { RegisteredCustomersComponent } from './registered-customers/registered-customers.component';
import { OrcLinkingComponent } from './orc-linking/orc-linking.component';
import { SharedModule } from 'app/shared'
import { RedingtonErrorComponent } from './redingtonerror/redington.error.component'
@NgModule({
    imports: [
        PortalRouting,
        LiveTileModule,
        SharedModule,
        
    ],
    declarations: [
        PortalComponent,
        DashboardComponent,
        Sidebar,
        Navbar,
        ProfileComponent,
        NotificationGroupsComponent,
        NotificationActionsComponent,
        PartnerFeedbackComponent,
        HelpPopupComponent,
        RejectedPartnersComponent,
        PartnerRatingsListComponent,
        CustomerRegistrationLinkComponent,
        RegisteredCustomersComponent,
        OrcLinkingComponent,
        RedingtonErrorComponent
    ],
    providers: [
        InactivePartnerService,
        PartnerService,
        VendorService,
        CustomerCloudAccountsService,
        ChangePasswordService,
        
    ]

})
export class PortalModule { }
