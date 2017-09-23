import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { NotificationsService, GlobalsService } from 'app/services';
import { Notifications, NotificationFilters, User } from 'app/classes';
import { NO_ACTION_SUBJECTS } from './notifications.module';

@Component({
    selector: 'app-notifications',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './notifications.component.html',
    styleUrls: ['./notifications.style.scss']
})
export class NotificationsComponent implements OnInit {
    user_details: User;
    notifications: Array<Notifications>;
    route_params_subscription: Subscription;
    gs_subscription: Subscription;
    filters: NotificationFilters = {
        page_number: 1,
        records_per_page: 10
    };
    searchText: string;
    first_record: number;
    last_record: number;
    total_filtered_nf: number = 0;
    total_filtered_pages: number = 0;
    total_unread_messages: number = 0;
    total_unread_alerts: number = 0;
    total_pending: number = 0;
    total_completed_unread: number = 0;
    pagination_btns: Array<number> = [];

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private nfService: NotificationsService,
        private gsService: GlobalsService

    ) {
        // Subscribe route params
        this.route_params_subscription = this.route.params.subscribe(
            route_params => {
                this.filters.type = route_params['type'];
                this.filters.status = route_params['status'];
                this.filters.page_number = parseInt(route_params['page_number']);
                this.getNotifications();
            }
        );

        // Subscribe Globals services
        this.gs_subscription = this.gsService.user$.subscribe(user => this.user_details = user);
    }

    ngOnInit() { }

    // Get Notifications by applying provided filters
    getNotifications() {

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

    // Updating component variables from new response data
    updateVariables(data: any) {
        this.notifications = data['notifications'];
        this.total_filtered_nf = data['total_filtered_nf'];
        this.total_filtered_pages = data['total_filtered_pages'];
        this.first_record = data['first_record'];
        this.last_record = data['last_record'];
        this.total_unread_messages = data['total_unread_messages'];
        this.total_unread_alerts = data['total_unread_alerts']
        this.total_pending = data['total_pending'];
        this.total_completed_unread = data['total_completed_unread'];
        // Update global value
        this.gsService.setUnreadNfCount(this.total_unread_messages + this.total_unread_alerts);

        if (data['notifications'].length == 0) {
            if ((this.filters.page_number - 1) > 0) {
                this.filters.page_number -= 1;
                this.getNotifications();
            }
        }

        this.generatePaginationBtns();
    }

    // Generaating pagination buttons according to the current page
    generatePaginationBtns() {
        let pagination_numbers = [];

        for (let num = -4; num <= 4; num++) pagination_numbers.push(this.filters.page_number + num);

        pagination_numbers = pagination_numbers.filter(num => num <= this.total_filtered_pages && num > 0);

        let index = pagination_numbers.indexOf(this.filters.page_number);
        let length = pagination_numbers.length;

        if (length > 5) {
            if (index > 2) {
                let last = length - 1;
                let first = last - 5;
                pagination_numbers.splice(0, first + 1);
            } else if (index <= 2) {
                let last = length - 1;
                let diff = last - (last - 4);
                pagination_numbers.splice(5, diff);
            }
        }

        this.pagination_btns = pagination_numbers;
    }

    ngOnDestroy() {
        this.route_params_subscription.unsubscribe();
        this.gs_subscription.unsubscribe();
    }

}
