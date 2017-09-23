import { RouterModule, Routes } from '@angular/router';
import { PortalComponent } from './portal.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthGuardService } from 'app/services/auth/auth-guard.service';
import { ProfileComponent } from './profile/profile.component';
import { NotificationGroupsComponent } from './notification-groups/notification-groups.component';
import { NotificationActionsComponent } from './notification-actions/notification-actions.component';
import { PartnerDetailsComponent } from './partner/partner-view/partner-details/partner-details.component';

import { PartnerFeedbackComponent } from './partner-feedback/partner-feedback.component'
import { ChangePasswordComponent } from "./change-password/change-password.component";
import { RejectedPartnersComponent } from './rejected-partners/rejected-partners.component';
import { PartnerRatingsListComponent } from './partner-ratings-list/partner-ratings-list.component';
import { CustomerRegistrationLinkComponent } from './customer-registration-link/customer-registration-link.component';
import { OrcLinkingComponent } from './orc-linking/orc-linking.component';



const PortalRoutes: Routes = [
    { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    {
        path: '',
        component: PortalComponent,
        children: [
            {
                path: 'dashboard',
                component: DashboardComponent,
                canActivate: [AuthGuardService]
            },
            {
                path: 'users',
                loadChildren: '../users/users.module#UsersModule',
                canActivate: [AuthGuardService],
                data: {
                    roles: ['users.list_reduser', 'users.add_reduser']
                }

            },
            {
                path: 'profile',
                component: ProfileComponent
            },
            //Change Password
            {
                path: 'change-password',
                component: ChangePasswordComponent,
                canActivate: [AuthGuardService]
            },
            {
                path: 'dashboard',
                component: DashboardComponent,
                canActivate: [AuthGuardService]
            },
            //Active Pratners
            {
                path: 'partner',
                loadChildren: './partner/partner.module#PartnerModule',
                canActivate: [AuthGuardService],
                data: {
                    roles: ['partner.view_partner', 'partner.list_partner']
                }
            },
            //Registered Customers
            {
                path: 'partner-customers',
                loadChildren: './registered-customers/registered-customers.module#RegisteredCustomerModule',
                canActivate: [AuthGuardService]
            },
            // partner-profile
            {
                path: 'partner-profile/:id',
                component: PartnerDetailsComponent,
                canActivate: [AuthGuardService]
            },
            //Nofifications
            {
                path: 'notifications',
                loadChildren: './notifications/notifications.module#NotificationsModule',
                canActivate: [AuthGuardService],
                data: {
                    roles: ['notifications.list_notifications', 'notifications.view_notifications']
                }
            },
            //Notification-groups
            {
                path: 'notification-groups',
                component: NotificationGroupsComponent,
                canActivate: [AuthGuardService],
                data: {
                    roles: ['notifications.view_notificationgroups', 'notifications.change_notificationgroups', 'notifications.list_notificationgroups', 'notifications.add_notificationgroups']
                }

            },
            //Notifications-action
            {
                path: 'notification-actions',
                component: NotificationActionsComponent,
                canActivate: [AuthGuardService],
                data: {
                    roles: ['notifications.add_notificationactions', 'notifications.delete_notificationactions', 'notifications.view_notificationactions', 'notifications.list_notificationactions', 'notifications.change_notificationactions']
                }

            },
            //Partner View
            {
                path: 'rentrap-view',
                loadChildren: './partner/partner-view/partner-view.module#PartnerViewModule'
            },
            //Customers
            {
                path: 'customers',
                loadChildren: './customers/customers.module#CustomersModule',
                canActivate: [AuthGuardService],
                data: {
                    roles: ['customers.add_customers']
                }
            },
            //In-active Partner
            {
                path: 'inactive-partner',
                loadChildren: './inactive-partner/inactive-partner.module#InactivePartnerModule',
                canActivate: [AuthGuardService],
                data: {
                    roles: ['partner.view_initialpartner', 'partner.list_initialpartner']
                }
            },
            //Partner Feedback
            {
                path: 'feedback',
                component: PartnerFeedbackComponent,

            },
           {
                path: 'rejected-partner/list',
                component: RejectedPartnersComponent
           },
           {
               path: 'partner-ratings',
               component: PartnerRatingsListComponent
           },
        ]
    }

];

export const PortalRouting = RouterModule.forChild(PortalRoutes);
