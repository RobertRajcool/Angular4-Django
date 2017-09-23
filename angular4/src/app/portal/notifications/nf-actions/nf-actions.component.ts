import { Component, OnInit, ViewEncapsulation, Input, Output, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { Notifications } from 'app/classes';
import { NotificationsService } from 'app/services';

@Component({
    selector: 'app-nf-actions',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './nf-actions.component.html',
    styleUrls: ['../notifications.style.scss']
})
export class NfActionsComponent implements OnInit {
    @Input() design: string = 'normal';
    @Input() notification: Notifications;
    @Output() refresh: EventEmitter<any> = new EventEmitter();

    constructor(
        private router: Router,
        private nfService: NotificationsService
    ) { }

    ngOnInit() {
    }

    // Navigate to view order details
    viewOrder() {
        var order = this.notification.details;
        this.nfService.markAsCompleted(this.notification.id)
            .subscribe(
            Result => {
                // Referesh notifications
                this.refresh.emit();
                this.router.navigate(['/app/orders', order['id']]);
            });
    }

    // Navigate to view instance details
    viewInstance() {
        var instance = this.notification.details;
        this.nfService.markAsCompleted(this.notification.id)
            .subscribe(
            Result => {
                // Referesh notifications
                this.refresh.emit();
                this.router.navigate(["/app/cloud-instances/"+instance['id']]);
            });
    }

    viewIsvProduct(){
        var isvProduct = this.notification.details;

        this.nfService.markAsCompleted(this.notification.id)
            .subscribe(
            Result => {
                // Referesh notifications
                this.refresh.emit();
                this.router.navigate(['/isv/products', isvProduct['id'], 'view']);
            });
    }

}
