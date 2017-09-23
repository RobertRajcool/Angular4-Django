import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from 'app/shared';
import { NotificationsComponent } from './notifications.component';
import { AuthGuardService } from 'app/services/auth/auth-guard.service';

export const Notificationsroutes = [
    { path: '', redirectTo: 'messages/unread/page/1', pathMatch: 'full' },
    { path: ':type', redirectTo: ':type/unread/page/1', pathMatch: 'full' },
    { path: ':type/:status', redirectTo: ':type/:status/page/1' },
    {
        path: ':type/:status/page/:page_number',
        component: NotificationsComponent,
        data: {
            regex: {
                type: '(messages|alerts)',
                status: '(unread|read|pending|completed)',
                page_number: '[0-9]+'
            }
        },
        canActivate: [AuthGuardService]
    }
];

@NgModule({
    imports: [
        SharedModule,
        RouterModule.forChild(Notificationsroutes)
    ],
    declarations: [
        NotificationsComponent,
    ]
})
export class NotificationsModule { }


export const NO_ACTION_SUBJECTS: Array<string> = [
    'CloudAccounts',
    'PartnerFeedback'
]
