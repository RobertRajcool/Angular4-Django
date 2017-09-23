import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { NotificationsService, GlobalsService } from 'app/services';
import { Notifications, NotificationFilters, User } from 'app/classes';
import { NO_ACTION_SUBJECTS } from '../notifications.module';
declare var jQuery: any;

@Component({
    selector: 'app-popup-notifications',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './popup-notifications.component.html',
    styleUrls: ['../notifications.style.scss']
})
export class PopupNotificationsComponent implements OnInit {
    user_details: User;
    notifications: Array<Notifications>;
    last_sync: Date;
    gs_subscription: Subscription;
    filters: NotificationFilters = {
        page_number: 1,
        records_per_page: 10,
        type: 'messages',
        status: 'unread'
    };
    total_unread_messages: number = 0;
    total_unread_alerts: number = 0;
    synchronizing: boolean = false;

    constructor(
        private router: Router,
        private nfService: NotificationsService,
        private gsService: GlobalsService

    ) {

        // Subscribe Globals services
        this.gs_subscription = this.gsService.user$.subscribe(user => this.user_details = user);
    }

    ngOnInit() {
        this.getNotifications();

        // Preventing data-toggle on popup ajax actions
        jQuery(window.document).on('click', '[data-ajax=true]', (e) => {
            e.preventDefault();
            return false;
        });
    }

    // Change Notifications type
    changeType(type: string) {
        this.filters['type'] = type;
        this.getNotifications();
    }

    // Get Notifications by applying provided filters
    getNotifications() {
        this.synchronizing = true;

        this.nfService.getNotifications(this.filters)
            .subscribe(
            Result => {
                this.updateVariables(Result);
            },
            Error => console.log(Error)
            );
    }

    // Mark selected notification as readed
    markAsRead(index: number) {
        let notification: Notifications = this.notifications[index];

        this.nfService.markAsRead(notification.id, this.filters)
            .subscribe(
            Result => {
                if (NO_ACTION_SUBJECTS.indexOf(notification.subject) >= 0) {

                    this.nfService.markAsCompleted(notification.id).subscribe(CompletionResult => {
                        this.updateVariables(Result);
                    },
                        Error => console.log(Error)
                    );
                } else {
                    this.updateVariables(Result);
                }
            },
            Error => console.log(Error)
            )
    }

    // Mark selected notification as completed
    markAsCompleted(id: number) {
        this.nfService.markAsCompleted(id).subscribe(Result => {
            this.updateVariables(Result);
        },
            Error => console.log(Error)
        );
    }

    // Updating component variables from new response data
    updateVariables(data: any) {
        this.notifications = data['notifications'];
        this.total_unread_messages = data['total_unread_messages'];
        this.total_unread_alerts = data['total_unread_alerts'];
        this.last_sync = new Date();
        this.synchronizing = false;

        // Update global value
        this.gsService.setUnreadNfCount(this.total_unread_messages + this.total_unread_alerts);

    }

    ngOnDestroy() {
        this.gs_subscription.unsubscribe();
    }

}
